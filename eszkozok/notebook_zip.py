"""Renderelés után becsomagolja a notebookokat az adataikkal együtt (_site/notebookok/notebookok.zip).

A Quarto post-render lépésként futtatja, helyben és a GitHub Actionsben is.
"""
import zipfile
from pathlib import Path

GYOKER = Path(__file__).resolve().parent.parent
FORRAS = GYOKER / "notebookok"
CEL = GYOKER / "_site" / "notebookok" / "notebookok.zip"

# Csak ami a hallgatónak kell: a notebookok, a data/ mappa és a requirements.txt.
kell = [p for p in FORRAS.rglob("*")
        if p.is_file()
        and not p.name.startswith(".")
        and ".ipynb_checkpoints" not in p.parts
        and (p.suffix == ".ipynb" or p.name == "requirements.txt" or "data" in p.relative_to(FORRAS).parts)]

CEL.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(CEL, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(kell):
        z.write(p, Path("notebookok") / p.relative_to(FORRAS))
print(f"notebookok.zip: {len(kell)} fájl")
