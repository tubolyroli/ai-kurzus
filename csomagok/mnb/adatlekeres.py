"""Az MNB-csomag adatlekérő függvényei: inflációs tényadatok és a jelentések letöltése.

Két adatsort ad, mindkettőt havi és éves bontásban:
- KSH: fogyasztóiár-index, a KSH STADAT-tábláiból (ara0039 havi, ara0001 éves);
- Eurostat: harmonizált fogyasztóiár-index (HICP), az Eurostat adat-API-jából.

Először a netről kéri le az adatot. Ha ez nem sikerül (nincs net, leállt a szerver,
megváltozott a cím), a csomagba mentett `data/tartalek.csv`-ből dolgozik, és ezt ki is írja.
Csak a Python standard könyvtárát használja.

Használat:
    from adatlekeres import inflacio, dokumentumok_letoltese
    inflacio("KSH", "2023-08")
    inflacio("Eurostat", "2023", "2025")
"""
import csv
import json
import urllib.request
from datetime import datetime
from pathlib import Path

MAPPA = Path(__file__).resolve().parent
TARTALEK = MAPPA / "data" / "tartalek.csv"
FORRASOK = MAPPA / "forrasok.csv"

EUROSTAT = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
URL = {
    ("KSH", "havi"): "https://www.ksh.hu/stadat_files/ara/hu/ara0039.csv",
    ("KSH", "eves"): "https://www.ksh.hu/stadat_files/ara/hu/ara0001.csv",
    ("Eurostat", "havi"): EUROSTAT + "prc_hicp_minr?geo=HU&coicop18=TOTAL&unit=RCH_A"
                                     "&sinceTimePeriod=2022-01&format=JSON&lang=en",
    ("Eurostat", "eves"): EUROSTAT + "prc_hicp_ainr?geo=HU&coicop18=TOTAL&unit=RCH_A_AVG"
                                     "&sinceTimePeriod=2010&format=JSON&lang=en",
}
LEIRAS = {
    "KSH": "KSH, fogyasztóiár-index (STADAT ara0039 / ara0001)",
    "Eurostat": "Eurostat, harmonizált fogyasztóiár-index, HICP (prc_hicp_minr / prc_hicp_ainr)",
}
MERTEKEGYSEG = {
    "havi": "%, az előző év azonos hónapjához képest",
    "eves": "%, éves átlag az előző év átlagához képest",
}
LEGTOBB = 60  # ennél több időszakot nem adunk vissza egyszerre: az ágens kontextusa kicsi

HONAPOK = ["január", "február", "március", "április", "május", "június", "július",
           "augusztus", "szeptember", "október", "november", "december"]

_gyorsitotar = {}  # egy futáson belül ne kérjük le újra ugyanazt


def inflacio(forras, tol, ig=None):
    """Magyarországi infláció a KSH vagy az Eurostat adataiból, egy időszakra vagy időszakokra.

    Paraméterek:
        forras: "KSH" vagy "Eurostat".
        tol:    "ÉÉÉÉ-HH" (havi adat, pl. "2023-08") vagy "ÉÉÉÉ" (éves átlag, pl. "2023").
        ig:     az utolsó időszak, ugyanolyan formában; ha nincs megadva, csak a `tol` időszak.

    Visszaad egy rövid szótárat: forrás, mértékegység, honnan jött az adat (élő vagy
    mentett), és az `adatok` (időszak -> érték, százalékban, egy tizedesre). Ha valami
    nem stimmel (rossz forrásnév, nincs adat az időszakra), a szótárban `hiba` kulcs van.
    Egyszerre legfeljebb 60 időszakot ad vissza.
    """
    if forras not in LEIRAS:
        return {"hiba": f"ismeretlen forrás: {forras!r}; lehet: 'KSH' vagy 'Eurostat'"}
    ig = ig or tol
    tol, ig = str(tol).strip(), str(ig).strip()
    gyakorisag = "havi" if len(tol) == 7 else "eves"
    if len(tol) not in (4, 7) or len(ig) != len(tol):
        return {"hiba": "az időszak formája 'ÉÉÉÉ' (éves) vagy 'ÉÉÉÉ-HH' (havi), és a kettő egyforma legyen"}

    sorozat, honnan = _sorozat(forras, gyakorisag)
    adatok = {k: v for k, v in sorted(sorozat.items()) if tol <= k <= ig}
    if not adatok:
        elso, utolso = min(sorozat), max(sorozat)
        return {"hiba": f"nincs adat erre: {tol}–{ig}; elérhető: {elso}–{utolso}", "adat_honnan": honnan}
    if len(adatok) > LEGTOBB:
        return {"hiba": f"túl sok időszak ({len(adatok)}); egyszerre legfeljebb {LEGTOBB} kérhető"}
    return {
        "forras": LEIRAS[forras],
        "mertekegyseg": MERTEKEGYSEG[gyakorisag],
        "adat_honnan": honnan,
        "adatok": adatok,
    }


# ------------------------------------------------------------------ belső részek

def _sorozat(forras, gyakorisag):
    """Egy teljes adatsor (időszak -> érték) és a származása; élőben, ennek híján a tartalékból."""
    kulcs = (forras, gyakorisag)
    if kulcs not in _gyorsitotar:
        try:
            nyers = _letolt(URL[kulcs])
            sorozat = _ksh(nyers, gyakorisag) if forras == "KSH" else _eurostat(nyers)
            if not sorozat:
                raise ValueError("üres adatsor")
            honnan = f"élő, letöltve {datetime.now():%Y-%m-%d %H:%M}"
        except Exception as hiba:  # bármi baj van a netes lekéréssel, a mentett adatra váltunk
            sorozat, mentve = _tartalek(forras, gyakorisag)
            honnan = f"mentett tartalék ({TARTALEK.name}), mentve {mentve}"
            print(f"Nincs net, vagy nem érem el a forrást ({type(hiba).__name__}). "
                  f"A mentett adatot használom: data/{TARTALEK.name}, mentve {mentve}.")
        _gyorsitotar[kulcs] = (sorozat, honnan)
    return _gyorsitotar[kulcs]


def _letolt(url, idokorlat=20):
    """Egy URL tartalma bájtokban. A KSH szervere a böngészőnek látszó kérést fogadja el."""
    keres = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (kurzus-projektcsomag)"})
    with urllib.request.urlopen(keres, timeout=idokorlat) as valasz:
        return valasz.read()


def _szam(szoveg):
    """Magyar tizedesvesszős szám; üres vagy '..' -> None."""
    szoveg = szoveg.strip().replace("\xa0", "").replace(" ", "")
    if szoveg in ("", "..", "-"):
        return None
    return float(szoveg.replace(",", "."))


def _ksh(nyers, gyakorisag):
    """KSH STADAT CSV -> {időszak: infláció %}. A KSH indexet közöl (előző év = 100), ebből 100-at vonunk le.

    A tábla ISO-8859-2 kódolású, pontosvesszővel tagolt; az első sor a cím, a második a fejléc.
    A havi táblában az év csak az év első sorában áll ("2023."), a többi sorban üres.
    """
    szoveg = nyers.decode("iso-8859-2")
    if szoveg.lstrip().startswith("<"):
        # Sok egymás utáni kérés után a KSH tűzfala egy ideig HTML-hibaoldalt ad CSV helyett.
        raise ValueError("a KSH szervere CSV helyett hibaoldalt adott (Request Rejected)")
    sorok = list(csv.reader(szoveg.splitlines(), delimiter=";"))
    fejlec = sorok[1]
    oszlop = next(i for i, nev in enumerate(fejlec) if nev.strip() == "Fogyasztóiár-index")
    eredmeny, ev = {}, None
    for sor in sorok[2:]:
        if len(sor) <= oszlop:
            continue
        if gyakorisag == "eves":
            idoszak, ertek = sor[0].strip(), _szam(sor[oszlop])
            if not idoszak.isdigit():
                continue
        else:
            if sor[0].strip():
                ev = sor[0].strip().rstrip(".")
            honap = sor[1].strip()
            if honap not in HONAPOK:
                continue
            idoszak, ertek = f"{ev}-{HONAPOK.index(honap) + 1:02d}", _szam(sor[oszlop])
        if ertek is not None:
            eredmeny[idoszak] = round(ertek - 100, 1)
    return eredmeny


def _eurostat(nyers):
    """Eurostat JSON-stat (egyetlen idősor) -> {időszak: érték}."""
    adat = json.loads(nyers)
    idok = adat["dimension"]["time"]["category"]["index"]
    sorszambol = {sorszam: ido for ido, sorszam in idok.items()}
    return {sorszambol[int(i)]: round(float(v), 1) for i, v in adat["value"].items()}


def _tartalek(forras, gyakorisag):
    """A mentett adatsor a data/tartalek.csv-ből, és a mentés dátuma."""
    sorozat, mentve = {}, "ismeretlen"
    with TARTALEK.open(encoding="utf-8-sig", newline="") as f:
        for sor in csv.DictReader(f, delimiter=";"):
            if sor["forras"] == forras and (len(sor["idoszak"]) == 7) == (gyakorisag == "havi"):
                sorozat[sor["idoszak"]] = float(sor["ertek"])
                mentve = sor["letoltve"]
    return sorozat, mentve


# ------------------------------------------------------------------ dokumentumok

def dokumentumok_letoltese(mappa=None):
    """Letölti a forrasok.csv-ben felsorolt jelentéseket (PDF), ha még nincsenek meg.

    A PDF-ek nem részei a csomagnak (nagyok, és nem a mi szellemi termékünk): az első
    futtatáskor töltődnek le a `dokumentumok/` mappába. A letöltött fájlok listáját adja vissza.
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
    print(inflacio("KSH", "2026-01", "2026-12"))
    print(inflacio("Eurostat", "2023", "2025"))
