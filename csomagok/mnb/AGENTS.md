# AGENTS.md

Záró projekt: az MNB Inflációs jelentéseinek állításait vetjük össze a tényadatokkal.
A jelentések a `dokumentumok/` mappában vannak (lista: `forrasok.csv`), a tényadatot az `adatlekeres.py` függvényei adják.
Az adatok jelentése az `adatszotar.md`-ben van.

## Munkamód

- Szerkesztés előtt mondd el a tervet 3 lépésben.
- Csak azt változtasd, amit a feladat kér.
- Ha nem vagy biztos valamiben, kérdezz, ne találgass. Ha feltételezéssel élsz, írd be a `feltetelezesek.md`-be.

## Adat és hivatkozás

- Tényadatot csak az `adatlekeres.py` függvényeivel kérj le; számot ne írj be kézzel.
- Minden dokumentumból vett számhoz add meg a forrást: melyik jelentés, hányadik (nyomtatott) oldal.
- Ami nincs a dokumentumokban vagy az adatban, arra a válasz: nincs a forrásokban.

## Python

- A mappa saját környezetéből (`.venv`) dolgozz. Új csomag telepítése előtt kérdezz.
- Magyar változó- és függvénynevek, ékezet nélkül.

## Biztonság

- A `data/` mappa fájljait és a `forrasok.csv`-t ne írd felül és ne módosítsd.
- Soha ne commitolj `.env`-et, API-kulcsot, jelszót.
