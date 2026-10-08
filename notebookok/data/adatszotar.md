# Adatszótár: `inflacio_kategoriak_2024.csv`

Mit jelentenek az adatok. Ha valami itt nincs leírva, ne találgass: kérdezz.

## Forrás

Eurostat, *HICP – monthly data (annual rate of change)*, `prc_hicp_manr`, Magyarország, 2024.
A HICP a harmonizált fogyasztói árindex: uniós módszertan, ezért kissé eltér a KSH által közölt fogyasztói árindextől (KSH-CPI). A kettőt ne keverd.

## Formátum

- Elválasztó: pontosvessző (`;`). Kódolás: UTF-8. Tizedesjel: pont.
- Az üres `inflacio_ev_ev` hiányzó adatot jelent, nem nullát.

| Oszlop | Jelentés | Mértékegység |
| :--- | :--- | :--- |
| `honap` | a megfigyelés hónapja, `ÉÉÉÉ-HH` formában | – |
| `kategoria` | fogyasztási kategória (COICOP) | – |
| `inflacio_ev_ev` | árváltozás az előző év azonos hónapjához képest | % |

## Ismétlődő sorok

A fájl több kivonatból áll össze, ezért egy hónap–kategória pár **többször is szerepelhet**. Ilyenkor az értékek azonosak: minden hónapot kategóriánként **egyszer** vegyél figyelembe.

## Kategóriák

A kategórianevek nem egységesek. Elemzés előtt minden változatot a kanonikus névre kell cserélni. Ha a táblázatban nem szereplő nevet találsz, állj meg és szólj.

| Kanonikus név | Előforduló változatok |
| :--- | :--- |
| Összesen | `Osszesen` |
| Élelmiszer | `Elelmiszer` |
| Szeszes ital, dohány | |
| Ruházat | |
| Lakhatás, energia | `Lakhatas, energia` |
| Lakberendezés | |
| Egészségügy | |
| Közlekedés | `Kozlekedes` |
| Hírközlés | |
| Szabadidő, kultúra | |
| Oktatás | |
| Vendéglátás, szállás | |
| Egyéb | |

Az **Összesen** a teljes fogyasztói kosár, a kategóriák *súlyozott* átlaga. A súlyok nincsenek az adatban, ezért az Összesent a kategóriákból kiszámolni nem lehet.
