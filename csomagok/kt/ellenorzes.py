"""Ellenőrző script (minta): a nyers adatból kiszámolja két példakérdés elvárt értékét, és összeveti a válasszal.

Az elvárt értéket ez a script számolja az Eurostat-adatból, nem a nyelvi modell.
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

from adatlekeres import kormanyzati_adat

TURES = 0.05  # a válaszok egy tizedesre kerekítenek

# ---------------------------------------------------------------- A kérdés (csak adat)
# „Melyik évben volt a legalacsonyabb a kormányzati szektor GDP-arányos adóssága
#  2020 és 2025 között, és mennyi volt?”


def elvart_a():
    """Az Eurostat éves adataiból: a legalacsonyabb adósságráta éve és értéke."""
    adat = kormanyzati_adat("adossag", "2020", "2025")["adatok"]
    ev = min(adat, key=adat.get)
    return {"ev": ev, "ertek": adat[ev]}


# ---------------------------------------------------------------- B kérdés (dokumentum + adat)
# „Mekkora hiánnyal számolt eredetileg a 2025. évi költségvetési törvény,
#  mekkora lett a tényleges hiány, és mennyivel tért el a kettő?”

# A tervezett hiány a dokumentumokból (ezt a RAG-nak kell megtalálnia), a GDP százalékában.
# Írd mellé kommentben, melyik dokumentum hányadik oldaláról származik, és szó szerint mit állít.
TERV = None  # TODO


def elvart_b():
    """A 2025-ös tényleges hiány (a GDP %-ában) és az eltérés a tervtől, százalékpontban."""
    egyenleg = kormanyzati_adat("egyenleg", "2025")["adatok"]["2025"]
    hiany = -egyenleg  # az Eurostat egyenlege hiány esetén negatív (lásd adatszotar.md)
    return {"teny": round(hiany, 1), "elteres": round(hiany - TERV, 1)}


# ---------------------------------------------------------------- segédfüggvények

def szamok(szoveg):
    """A szövegben szereplő számok listája; a magyar tizedesvesszőt és az ezres szóközt is érti."""
    szoveg = re.sub(r"\b\d{4}-\d{2}(-\d{2})?\b", " ", szoveg)  # a dátumok (2025-05-04) ne számítsanak számnak
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
    print(f"A elvárt: {a['ev']}, a GDP {a['ertek']}%-a")
    if valasz is not None:
        resz = szakasz(valasz, "A")
        kiir(a["ev"] in resz, f"A: az év ({a['ev']})")
        kiir(van_benne(resz, a["ertek"]), f"A: az adósságráta ({a['ertek']})")

    if TERV is None:
        print("MÉG NINCS KÉSZ  B: töltsd ki a TERV változót (a tervezett hiány a GDP %-ában, forrással)")
        return
    b = elvart_b()
    print(f"B elvárt: terv {TERV}%, tény {b['teny']}% (a GDP %-ában), eltérés {b['elteres']:+} százalékpont")
    if valasz is not None:
        resz = szakasz(valasz, "B")
        kiir(van_benne(resz, TERV), f"B: a terv ({TERV})")
        kiir(van_benne(resz, b["teny"]), f"B: a tényleges hiány ({b['teny']})")
        kiir(van_benne(resz, b["elteres"]), f"B: az eltérés ({b['elteres']:+} százalékpont)")


if __name__ == "__main__":
    main()
