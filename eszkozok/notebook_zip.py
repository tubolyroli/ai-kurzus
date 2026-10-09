"""Renderelés után becsomagolja a notebookokat az adataikkal együtt.

- `notebookok.zip`: minden, az első órára és újrakezdéshez (mappastruktúrával: notebookok/…).
- `NN-valami.zip` (heti csomag): az adott órai notebook és a kurzus saját fájljai (kurzus.py,
  data/, requirements.txt, .env.pelda). A hallgató ezt bemásolja a saját notebookok mappájába;
  a korábbi, kitöltött notebookjait és a saját AGENTS.md-jét nem tartalmazza, így nem írja felül.

A Quarto post-render lépésként futtatja, helyben és a GitHub Actionsben is.
"""
import zipfile
from pathlib import Path

GYOKER = Path(__file__).resolve().parent.parent
FORRAS = GYOKER / "notebookok"
CEL = GYOKER / "_site" / "notebookok" / "notebookok.zip"

# Csak ami a hallgatónak kell: notebookok, a közös kurzus.py, a data/ mappa, requirements.txt, AGENTS.md, .env.pelda.
kell = [p for p in FORRAS.rglob("*")
        if p.is_file()
        and (not p.name.startswith(".") or p.name == ".env.pelda")
        and ".ipynb_checkpoints" not in p.parts and "__pycache__" not in p.parts
        and p.suffix != ".pdf"  # a forrás-PDF-eket a notebook tölti le, nem a zip viszi
        and "cache" not in p.relative_to(FORRAS).parts  # a gyorsítótárat a notebook újraszámolja
        and (p.suffix in (".ipynb", ".py") or p.name in ("requirements.txt", "AGENTS.md", ".env.pelda")
             or "data" in p.relative_to(FORRAS).parts)]

CEL.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(CEL, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(kell):
        z.write(p, Path("notebookok") / p.relative_to(FORRAS))
print(f"notebookok.zip: {len(kell)} fájl")

# Heti csomagok: egy órai notebook + a közös, felülírható fájlok, mappa nélkül a zip gyökerében.
kozos = [p for p in kell if p.suffix != ".ipynb" and p.name != "AGENTS.md"]
orai = sorted(p for p in FORRAS.glob("[0-9][0-9]-*.ipynb"))
for nb in orai:
    with zipfile.ZipFile(CEL.parent / f"{nb.stem}.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(nb, nb.name)
        for p in sorted(kozos):
            z.write(p, p.relative_to(FORRAS))
print(f"heti csomagok: {', '.join(nb.stem + '.zip' for nb in orai)}")
