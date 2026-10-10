"""Ellenőrző script (minta): a nyers adatból kiszámolja két példakérdés elvárt értékét, és összeveti a válasszal.

Az elvárt értéket ez a script számolja a KSH- és Eurostat-adatból, nem a nyelvi modell.
Így nem a modell ellenőrzi saját magát.

Futtatás a csomag mappájában:
    python ellenorzes.py              csak kiírja az elvárt értékeket (a tesztkérdések megírásához)
    python ellenorzes.py valasz.md    a válasz szövegében keresi az elvárt számokat

A válasz egy szövegfájl, benne `## A` és `## B` című szakasz (az ágensed ide írhatja a válaszait).
Kimenet: RENDBEN, HIBA vagy MÉG NINCS KÉSZ minden ellenőrzésre.
"""
import re
import sys
from pathlib import Path

from adatlekeres import inflacio

TURES = 0.05  # a válaszok egy tizedesre kerekítenek

# ---------------------------------------------------------------- A kérdés (csak adat)
# „Hány hónapban volt 20 százalék fölött az éves infláció a KSH szerint 2022-ben és 2023-ban,
#  és melyik hónapban volt a legmagasabb?”


def elvart_a():
    """A KSH havi adataiból: hány hónap volt 20% fölött, és a csúcs (hónap, érték)."""
    adat = inflacio("KSH", "2022-01", "2023-12")["adatok"]
    husz_folott = [honap for honap, ertek in adat.items() if ertek > 20]
    csucs = max(adat, key=adat.get)
    return {"honapok_szama": len(husz_folott), "csucs_honap": csucs, "csucs_ertek": adat[csucs]}


# ---------------------------------------------------------------- B kérdés (dokumentum + adat)
# „A 2023. szeptemberi Inflációs jelentés mekkora éves átlagos inflációt várt 2023-ra,
#  és beleesett-e a tényleges érték az előrejelzési sávba?”

# Az állítás a dokumentumból (ezt a RAG-nak kell megtalálnia):
# MNB Inflációs jelentés, 2023. szeptember, 12. oldal (a PDF 14. oldala):
# „Az infláció 2023-ban 17,6 – 18,1 százalék között alakulhat”
ELOREJELZES = (17.6, 18.1)

# Melyik adatsorral kell összevetni az MNB előrejelzését: "KSH" vagy "Eurostat"?
TENYADAT_FORRASA = None  # TODO: döntsd el, írd be ide, és írd le az indoklást az adatszotar.md-be


def elvart_b():
    """A 2023-as éves átlagos infláció a választott adatsorból, és hogy a sávba esik-e."""
    teny = inflacio(TENYADAT_FORRASA, "2023")["adatok"]["2023"]
    also, felso = ELOREJELZES
    return {"teny": teny, "savban": also - 1e-9 <= teny <= felso + 1e-9}


# ---------------------------------------------------------------- segédfüggvények

def szamok(szoveg):
    """A szövegben szereplő számok listája; a magyar tizedesvesszőt és az ezres szóközt is érti."""
    szoveg = re.sub(r"\b\d{4}-\d{2}(-\d{2})?\b", " ", szoveg)  # a dátumok (2023-08) ne számítsanak számnak
    szoveg = re.sub(r"\b\d+\.\s*oldal", " ", szoveg)  # az oldalszám (5. oldal) se
    talalatok = re.findall(r"[-−–]?\d{1,3}(?:[  ]\d{3})+(?:[.,]\d+)?|[-−–]?\d+(?:[.,]\d+)?", szoveg)
    return [float(t.replace(" ", "").replace(" ", "").replace("−", "-").replace("–", "-")
                  .replace(",", ".")) for t in talalatok]


def van_benne(szoveg, ertek):
    """Szerepel-e a szám a szövegben (előjeltől függetlenül, tűréssel)."""
    return any(abs(abs(sz) - abs(ertek)) <= TURES for sz in szamok(szoveg))


def szakasz(szoveg, betu):
    """A `## <betu>` című szakasz szövege a következő `## ` címig."""
    talalat = re.search(rf"^##\s*{betu}\b.*?$(.*?)(?=^##\s|\Z)", szoveg, re.M | re.S)
    return talalat.group(1) if talalat else ""


def kiir(jo, leiras):
    print(f"{'RENDBEN' if jo else 'HIBA   '}  {leiras}")


def main():
    valasz = Path(sys.argv[1]).read_text(encoding="utf-8-sig") if len(sys.argv) > 1 else None

    a = elvart_a()
    print(f"A elvárt: {a['honapok_szama']} hónap 20% fölött; csúcs: {a['csucs_honap']}, {a['csucs_ertek']}%")
    if valasz is not None:
        resz = szakasz(valasz, "A")
        kiir(van_benne(resz, a["honapok_szama"]), f"A: a hónapok száma ({a['honapok_szama']})")
        kiir(van_benne(resz, a["csucs_ertek"]), f"A: a csúcsérték ({a['csucs_ertek']})")

    if TENYADAT_FORRASA is None:
        print("MÉG NINCS KÉSZ  B: töltsd ki a TENYADAT_FORRASA változót (\"KSH\" vagy \"Eurostat\")")
        return
    b = elvart_b()
    print(f"B elvárt: tényadat 2023-ra {b['teny']}% ({TENYADAT_FORRASA}); "
          f"az előrejelzési sávba ({ELOREJELZES[0]}–{ELOREJELZES[1]}) {'beleesik' if b['savban'] else 'nem esik bele'}")
    if valasz is not None:
        resz = szakasz(valasz, "B")
        kiir(van_benne(resz, ELOREJELZES[0]) and van_benne(resz, ELOREJELZES[1]), "B: az előrejelzési sáv")
        # A tényadatot a sáv nélkül keressük: ha a tény épp a sáv széle, a sáv idézése nem számíthat találatnak.
        also, felso = (str(x).replace(".", "[.,]") for x in ELOREJELZES)
        sav_nelkul = re.sub(rf"{also}\s*(?:%|százalék)?\s*(?:[-–—]|és)\s*{felso}", " ", resz)
        kiir(van_benne(sav_nelkul, b["teny"]), f"B: a tényadat ({b['teny']})")
        print("         (Hogy a válasz következtetése, a „beleesik / nem esik bele”, helyes-e, azt olvasd el te.)")


if __name__ == "__main__":
    main()
