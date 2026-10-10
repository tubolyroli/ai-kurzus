"""A KT-csomag adatlekérő függvényei: kormányzati hiány és adósság, és a dokumentumok letöltése.

Az adat az Eurostat `gov_10dd_edpt1` táblájából jön (Government deficit/surplus, debt and
associated data), Magyarországra, a kormányzati szektorra (S13), éves bontásban.

Először a netről kéri le az adatot. Ha ez nem sikerül (nincs net, leállt a szerver,
megváltozott a cím), a csomagba mentett `data/tartalek.csv`-ből dolgozik, és ezt ki is írja.
Csak a Python standard könyvtárát használja.

Használat:
    from adatlekeres import kormanyzati_adat, dokumentumok_letoltese
    kormanyzati_adat("egyenleg", "2025")
    kormanyzati_adat("adossag", "2020", "2025", mertekegyseg="millio_ft")
"""
import csv
import itertools
import json
import urllib.request
from datetime import datetime
from pathlib import Path

MAPPA = Path(__file__).resolve().parent
TARTALEK = MAPPA / "data" / "tartalek.csv"
FORRASOK = MAPPA / "forrasok.csv"

URL = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/gov_10dd_edpt1"
       "?geo=HU&sector=S13&na_item=B9&na_item=GD&unit=PC_GDP&unit=MIO_NAC"
       "&sinceTimePeriod=2010&format=JSON&lang=en")

MUTATOK = {  # a függvény paramétere -> Eurostat-kód és leírás
    "egyenleg": ("B9", "a kormányzati szektor (S13) egyenlege, Eurostat B9: nettó hitelnyújtás (+) / nettó hitelfelvétel (-)"),
    "adossag": ("GD", "a kormányzati szektor (S13) konszolidált bruttó adóssága, Eurostat GD"),
}
MERTEKEGYSEGEK = {
    "gdp_szazalek": ("PC_GDP", "a GDP százalékában"),
    "millio_ft": ("MIO_NAC", "millió forint (folyó áron)"),
}
LEGTOBB = 30  # ennél több évet nem adunk vissza egyszerre: az ágens kontextusa kicsi

_gyorsitotar = {}  # egy futáson belül ne kérjük le újra ugyanazt


def kormanyzati_adat(mutato, tol, ig=None, mertekegyseg="gdp_szazalek"):
    """Magyarország kormányzati egyenlege vagy adóssága az Eurostat szerint, évente.

    Paraméterek:
        mutato:       "egyenleg" (a kormányzati szektor egyenlege; negatív érték = hiány)
                      vagy "adossag" (a kormányzati szektor bruttó adóssága).
        tol:          az első év, "ÉÉÉÉ" formában (pl. "2023").
        ig:           az utolsó év; ha nincs megadva, csak a `tol` év.
        mertekegyseg: "gdp_szazalek" (alapértelmezés) vagy "millio_ft".

    Visszaad egy rövid szótárat: forrás, mutató, mértékegység, honnan jött az adat (élő vagy
    mentett), és az `adatok` (év -> érték). Ha valami nem stimmel (rossz paraméter, nincs
    adat az évre), a szótárban `hiba` kulcs van. Egyszerre legfeljebb 30 évet ad vissza.
    """
    if mutato not in MUTATOK:
        return {"hiba": f"ismeretlen mutató: {mutato!r}; lehet: 'egyenleg' vagy 'adossag'"}
    if mertekegyseg not in MERTEKEGYSEGEK:
        return {"hiba": f"ismeretlen mértékegység: {mertekegyseg!r}; lehet: 'gdp_szazalek' vagy 'millio_ft'"}
    tol, ig = str(tol).strip(), str(ig or tol).strip()
    if not (len(tol) == len(ig) == 4 and tol.isdigit() and ig.isdigit()):
        return {"hiba": "az év formája 'ÉÉÉÉ', pl. '2024'"}

    tabla, honnan = _tabla()
    kulcs = (MUTATOK[mutato][0], MERTEKEGYSEGEK[mertekegyseg][0])
    sorozat = tabla.get(kulcs, {})
    adatok = {ev: v for ev, v in sorted(sorozat.items()) if tol <= ev <= ig}
    if not adatok:
        elerheto = f"{min(sorozat)}–{max(sorozat)}" if sorozat else "semmi"
        return {"hiba": f"nincs adat erre: {tol}–{ig}; elérhető: {elerheto}", "adat_honnan": honnan}
    if len(adatok) > LEGTOBB:
        return {"hiba": f"túl sok év ({len(adatok)}); egyszerre legfeljebb {LEGTOBB} kérhető"}
    return {
        "forras": "Eurostat, gov_10dd_edpt1 (Magyarország, kormányzati szektor)",
        "mutato": MUTATOK[mutato][1],
        "mertekegyseg": MERTEKEGYSEGEK[mertekegyseg][1],
        "adat_honnan": honnan,
        "adatok": adatok,
    }


# ------------------------------------------------------------------ belső részek

def _tabla():
    """Az egész tábla {(mutató, mértékegység): {év: érték}} alakban, és a származása."""
    if "tabla" not in _gyorsitotar:
        try:
            tabla = _eurostat(_letolt(URL))
            if not tabla:
                raise ValueError("üres tábla")
            honnan = f"élő, letöltve {datetime.now():%Y-%m-%d %H:%M}"
        except Exception as hiba:  # bármi baj van a netes lekéréssel, a mentett adatra váltunk
            tabla, mentve = _tartalek()
            honnan = f"mentett tartalék ({TARTALEK.name}), mentve {mentve}"
            print(f"Nincs net, vagy nem érem el a forrást ({type(hiba).__name__}). "
                  f"A mentett adatot használom: data/{TARTALEK.name}, mentve {mentve}.")
        _gyorsitotar["tabla"] = (tabla, honnan)
    return _gyorsitotar["tabla"]


def _letolt(url, idokorlat=20):
    """Egy URL tartalma bájtokban."""
    keres = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (kurzus-projektcsomag)"})
    with urllib.request.urlopen(keres, timeout=idokorlat) as valasz:
        return valasz.read()


def _eurostat(nyers):
    """Eurostat JSON-stat -> {(na_item, unit): {év: érték}}.

    A JSON-stat az értékeket egyetlen sorszámozott listában adja; a sorszám a dimenziók
    (freq, unit, sector, na_item, geo, time) indexeinek „kilométeróra-szerű” kombinációja.
    """
    adat = json.loads(nyers)
    dimenziok = [sorted(adat["dimension"][d]["category"]["index"].items(), key=lambda p: p[1])
                 for d in adat["id"]]
    nevek = adat["id"]
    tabla = {}
    for sorszam, kombinacio in enumerate(itertools.product(*dimenziok)):
        ertek = adat["value"].get(str(sorszam))
        if ertek is None:
            continue
        kodok = dict(zip(nevek, (kod for kod, _ in kombinacio)))
        tabla.setdefault((kodok["na_item"], kodok["unit"]), {})[kodok["time"]] = float(ertek)
    return tabla


def _tartalek():
    """A mentett tábla a data/tartalek.csv-ből, és a mentés dátuma."""
    tabla, mentve = {}, "ismeretlen"
    with TARTALEK.open(encoding="utf-8-sig", newline="") as f:
        for sor in csv.DictReader(f, delimiter=";"):
            tabla.setdefault((sor["mutato"], sor["mertekegyseg"]), {})[sor["ev"]] = float(sor["ertek"])
            mentve = sor["letoltve"]
    return tabla, mentve


# ------------------------------------------------------------------ dokumentumok

def dokumentumok_letoltese(mappa=None):
    """Letölti a forrasok.csv-ben felsorolt KT-dokumentumokat (PDF), ha még nincsenek meg.

    A PDF-ek nem részei a csomagnak: az első futtatáskor töltődnek le a `dokumentumok/`
    mappába. A letöltött fájlok listáját adja vissza.
    """
    mappa = Path(mappa) if mappa else MAPPA / "dokumentumok"
    mappa.mkdir(parents=True, exist_ok=True)
    fajlok = []
    with FORRASOK.open(encoding="utf-8-sig", newline="") as f:
        for sor in csv.DictReader(f, delimiter=";"):
            cel = mappa / sor["fajl"]
            if not cel.exists():
                print(f"Letöltöm: {sor['fajl']}")
                cel.write_bytes(_letolt(sor["url"], idokorlat=300))
            fajlok.append(cel)
    return fajlok


if __name__ == "__main__":
    print(kormanyzati_adat("egyenleg", "2022", "2025"))
    print(kormanyzati_adat("adossag", "2025", mertekegyseg="millio_ft"))
