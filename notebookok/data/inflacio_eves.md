# Adatszótár: `inflacio_eves.csv`

Magyarország éves inflációja két hivatalos forrásból, 2015–2025. Ha valami itt nincs leírva, ne találgass: kérdezz.

## Forrás

- **KSH:** STADAT 1.1.1.1. *Főbb ármutatók* (`ara0001`), a „Fogyasztóiár-index” oszlop (előző év = 100,0). Letöltve: 2026-10-10.
- **Eurostat:** `prc_hicp_ainr` (*HICP, annual data*), Magyarország, összesen (`TOTAL`): az éves átlagos változás (`RCH_A_AVG`) és az éves átlagos index (`INX_A_AVG`). Letöltve: 2026-10-10.

## Formátum

- Elválasztó: pontosvessző (`;`). Kódolás: UTF-8. Tizedesjel: pont.

| Oszlop | Jelentés | Mértékegység |
| :--- | :--- | :--- |
| `ev` | az év | – |
| `ksh_fogyasztoiar` | a KSH fogyasztóiár-indexe (CPI): az éves átlagos árszínvonal változása az előző évhez képest. A KSH indexet közöl (pl. 117,6), ebből 100-at levontunk | % |
| `eurostat_hicp` | a harmonizált fogyasztóiár-index (HICP) éves átlagos változása az előző évhez képest | % |
| `eurostat_hicp_index` | a HICP éves átlagos szintje, 2025 = 100 | index |

## Amit tudni kell

- A KSH fogyasztóiár-indexe és az Eurostat HICP-je **nem ugyanaz**: más a súlyozás és a lefedettség. Általában közel vannak egymáshoz, de el is térhetnek (2023-ban 17,6% és 17,0%). Hogy egy állítást melyikkel kell összevetni, azt az állítás forrása dönti el: nézd meg, melyik mutatóról beszél.
- Az éves átlagos változást az éves átlagos árszínvonalból számolják, nem a 12 havi érték átlagaként.
- Két év közötti teljes változást az index hányadosából számolj (`uj / regi - 1`), ne az éves változások összeadásával.
