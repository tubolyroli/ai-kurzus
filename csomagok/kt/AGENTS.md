# AGENTS.md

Záró projekt: a Költségvetési Tanács dokumentumainak állításait vetjük össze a tényadatokkal.
A dokumentumok listája a `forrasok.csv`. A szövegüket oldalanként a `data/szoveg.jsonl` tartalmazza, a `dokumentumok.py` függvényeivel olvasd be (ne a PDF-ből: a szkennelt PDF-ek szövegrétege hibás). A PDF-ek a `dokumentumok/` mappában vannak, ellenőrzéshez. A tényadatot az `adatlekeres.py` függvényei adják.
Az adatok jelentése az `adatszotar.md`-ben van.

## Munkamód

- Szerkesztés előtt mondd el a tervet 3 lépésben.
- Csak azt változtasd, amit a feladat kér.
- Ha nem vagy biztos valamiben, kérdezz, ne találgass. Ha feltételezéssel élsz, írd be a `feltetelezesek.md`-be.

## Adat és hivatkozás

- Tényadatot csak az `adatlekeres.py` függvényeivel kérj le; számot ne írj be kézzel.
- Minden dokumentumból vett számhoz add meg a forrást: melyik dokumentum, hányadik oldal.
- A szöveg nagy része gépi karakterfelismerésből (OCR) van, maradhat benne hiba: az idézett számot a PDF megadott oldalán ellenőrizni kell. Ha egy szám gyanús (például `%` helyett számjegyek, hiányzó tizedesvessző), jelezd.
- Ami nincs a dokumentumokban vagy az adatban, arra a válasz: nincs a forrásokban.

## Python

- A mappa saját környezetéből (`.venv`) dolgozz. Új csomag telepítése előtt kérdezz.
- Magyar változó- és függvénynevek, ékezet nélkül.

## Biztonság

- A `data/` mappa fájljait és a `forrasok.csv`-t ne írd felül és ne módosítsd.
- Soha ne commitolj `.env`-et, API-kulcsot, jelszót.
