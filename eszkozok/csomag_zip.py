"""Renderelés után becsomagolja a projektcsomagokat: `csomagok/<nev>/` -> `_site/csomagok/<nev>.zip`.

A zipben a csomag egy `projekt-<nev>/` mappában van, így kicsomagolva egyből a projektrepó
kiindulópontja. A letöltött dokumentumok (PDF), a gyorsítótár és a Python saját fájljai nem
kerülnek bele; a `.gitignore` igen.

A Quarto post-render lépésként futtatja, helyben és a GitHub Actionsben is.
"""
import zipfile
from pathlib import Path

GYOKER = Path(__file__).resolve().parent.parent
FORRAS = GYOKER / "csomagok"
CEL = GYOKER / "_site" / "csomagok"

KIHAGY_MAPPAK = {"dokumentumok", "cache", "__pycache__", ".ipynb_checkpoints", ".venv"}


def kell(p, csomag):
    """A csomag fájljai közül ami a hallgatónak kell (PDF, gyorsítótár, rejtett fájlok nélkül)."""
    reszek = p.relative_to(csomag).parts
    return (p.is_file()
            and not KIHAGY_MAPPAK & set(reszek)
            and p.suffix.lower() not in (".pdf", ".pyc")
            and (not p.name.startswith(".") or p.name == ".gitignore"))


CEL.mkdir(parents=True, exist_ok=True)
for csomag in sorted(d for d in FORRAS.iterdir() if d.is_dir()):
    fajlok = sorted(p for p in csomag.rglob("*") if kell(p, csomag))
    with zipfile.ZipFile(CEL / f"{csomag.name}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for p in fajlok:
            z.write(p, Path(f"projekt-{csomag.name}") / p.relative_to(csomag))
    print(f"{csomag.name}.zip: {len(fajlok)} fájl")
