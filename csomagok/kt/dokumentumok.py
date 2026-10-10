"""A KT-dokumentumok szövege oldalanként, a `data/szoveg.jsonl`-ből.

A KT véleményeinek többsége aláírt, beszkennelt PDF. A PDF-be ágyazott szövegréteg ezeknél rossz
(például „JJ ,5” áll a „77,5” helyén), ezért a szkennelt oldalakat újra felismertettem (OCR), és a
szöveget oldalanként a `data/szoveg.jsonl`-be tettem. A digitális oldalak szövege a PDF-ből jön.
Gépi felismerés: maradhat benne hiba, ezért egy idézett számot mindig nézz meg a PDF-ben is.

Egy oldal egy szótár, ugyanolyan, mint a 3. alkalom `jelentes_oldalai()` függvényénél, csak a
`bekezdesek` helyett nyers `blokkok` vannak (a pymupdf `blokk[4]`-ének megfelelője):

    {"fajl": "kt-2024-11-07.pdf", "jelentes": "2024-11-07", "pdf_oldal": 5, "oldal": 5,
     "szoveg_forrasa": "ocr", "blokkok": ["A Tanács 2024. november 7-én ...", ...]}

Használat:
    from dokumentumok import osszes_oldal, dokumentum_oldalai, oldal_szovege
    oldalak = osszes_oldal()                          # minden dokumentum, a forrasok.csv sorrendjében
    oldal_szovege("kt-2024-11-07.pdf", 5)             # egy oldal szövege egyben (idézet ellenőrzéséhez)

Ha a `forrasok.csv`-ben olyan dokumentum van, amely nincs a `szoveg.jsonl`-ben (például frissítés után),
a függvény a `dokumentumok/` mappába letöltött PDF szövegrétegét olvassa (ehhez kell a pymupdf).
"""
import csv
import json
from pathlib import Path

MAPPA = Path(__file__).resolve().parent
SZOVEG = MAPPA / "data" / "szoveg.jsonl"
FORRASOK = MAPPA / "forrasok.csv"
DOKUMENTUMOK = MAPPA / "dokumentumok"

_tar = {}  # fájlnév -> oldalak; a jsonl-t egy futáson belül csak egyszer olvassuk be


def _forrasok():
    with FORRASOK.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _szovegfajl():
    """A szoveg.jsonl oldalai dokumentumonként."""
    if not _tar and SZOVEG.exists():
        with SZOVEG.open(encoding="utf-8") as f:
            for sor in f:
                oldal = json.loads(sor)
                _tar.setdefault(oldal["fajl"], []).append(oldal)
    return _tar


def _pdf_oldalai(sor):
    """Ha a dokumentum nincs a szoveg.jsonl-ben: a letöltött PDF szövegrétege, ugyanilyen alakban."""
    import pymupdf  # csak itt kell, ezért itt töltjük be
    pdf = DOKUMENTUMOK / sor["fajl"]
    if not pdf.exists():
        raise FileNotFoundError(f"{sor['fajl']} nincs a szoveg.jsonl-ben, és a {pdf} sincs meg. "
                                "Töltsd le: from adatlekeres import dokumentumok_letoltese; dokumentumok_letoltese()")
    eltolas = int(sor["oldal_eltolas"])
    oldalak = []
    for i, oldal in enumerate(pymupdf.open(pdf), start=1):
        blokkok = [b[4].strip() for b in oldal.get_text("blocks") if b[6] == 0 and b[4].strip()]
        oldalak.append({"fajl": sor["fajl"], "jelentes": sor["jelentes"], "pdf_oldal": i, "oldal": i - eltolas,
                        "szoveg_forrasa": "pdf", "blokkok": blokkok})
    return oldalak


def dokumentum_oldalai(fajl):
    """Egy dokumentum oldalai (lista), a fájlneve alapján, pl. "kt-2024-11-07.pdf"."""
    tar = _szovegfajl()
    if fajl in tar:
        return tar[fajl]
    sor = next((s for s in _forrasok() if s["fajl"] == fajl), None)
    if sor is None:
        raise KeyError(f"nincs ilyen dokumentum a forrasok.csv-ben: {fajl!r}")
    tar[fajl] = _pdf_oldalai(sor)
    return tar[fajl]


def osszes_oldal():
    """A forrasok.csv minden dokumentumának minden oldala, egy listában."""
    return [oldal for sor in _forrasok() for oldal in dokumentum_oldalai(sor["fajl"])]


def oldal_szovege(fajl, pdf_oldal):
    """Egy oldal szövege egyetlen szövegként (a blokkok szóközzel összefűzve, a sortörések nélkül)."""
    oldal = dokumentum_oldalai(fajl)[pdf_oldal - 1]
    return " ".join(" ".join(oldal["blokkok"]).split())


if __name__ == "__main__":
    oldalak = osszes_oldal()
    print(f"{len(oldalak)} oldal, ebből {sum(o['szoveg_forrasa'] == 'ocr' for o in oldalak)} OCR-ből")
    print(oldal_szovege("kt-2024-11-07.pdf", 5)[:300], "…")
