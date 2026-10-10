# Adatszótár: `munkanelkuliseg.csv`

Éves munkanélküliségi ráta Magyarországon, néhány szomszédos országban és az EU-ban, 2015–2025. A 10. alkalom adatelemző ágensének helyi tartaléka: ha nincs net, az eszköz ebből dolgozik. Ha valami itt nincs leírva, ne találgass: kérdezz.

## Forrás

- Eurostat `une_rt_a` (*Unemployment by sex and age – annual data*), 15–74 évesek (`Y15-74`), összesen (`T`), a munkaerő százalékában (`PC_ACT`). Letöltve: 2026-10-10. A letöltő script: `tanari/adat_09_10.py`.

## Formátum

- Elválasztó: pontosvessző (`;`). Kódolás: UTF-8. Tizedesjel: pont.

| Oszlop | Jelentés | Mértékegység |
| :--- | :--- | :--- |
| `orszag` | Eurostat-kód: `HU`, `CZ`, `PL`, `SK`, `AT`, és `EU27_2020` (az EU 27 tagállama együtt) | – |
| `nev` | magyar név | – |
| `ev` | az év | – |
| `rata` | a munkanélküliségi ráta: a munkanélküliek aránya a munkaerőn (foglalkoztatottak + munkanélküliek) belül, éves átlag | % |
| `letoltve` | a letöltés napja | dátum |

## Amit tudni kell

- **A ráta változását százalékpontban** add meg (4,0%-ról 4,4%-ra: +0,4 százalékpont), ne százalékban.
- Az Eurostat rátája az ILO-definíció szerinti, a munkaerő-felmérésből számolt ráta. A KSH ugyanebből a felmérésből közöl adatot, a regisztrált álláskeresők száma (NFSZ) viszont más mutató: a kettő nem összevethető.
- Az éves adat a következő év tavaszán jelenik meg; a legutolsó év később még módosulhat.
