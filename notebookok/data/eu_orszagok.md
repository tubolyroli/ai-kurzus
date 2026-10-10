# Adatszótár: `eu_orszagok.csv`

A 27 EU-tagállam reál-GDP-je és éves inflációja, 2019–2025. A 9. alkalom ágensének helyi tartaléka: ha nincs net, az eszközök ebből dolgoznak. Ha valami itt nincs leírva, ne találgass: kérdezz.

## Forrás

- **Reál-GDP:** Eurostat `nama_10_gdp` (*GDP and main components*), bruttó hazai termék piaci áron (`B1GQ`), láncolt volumen, 2020-as referenciaév, millió euró (`CLV20_MEUR`). Letöltve: 2026-10-10.
- **Infláció:** Eurostat `prc_hicp_ainr` (*HICP, annual data*), összesen (`TOTAL`), éves átlagos változás (`RCH_A_AVG`). Letöltve: 2026-10-10.
- A letöltő script: `tanari/adat_09_10.py` (a tanári anyagban).

## Formátum

- Elválasztó: pontosvessző (`;`). Kódolás: UTF-8. Tizedesjel: pont.

| Oszlop | Jelentés | Mértékegység |
| :--- | :--- | :--- |
| `orszag` | az ország kétbetűs Eurostat-kódja (Görögország: `EL`, nem `GR`) | – |
| `nev` | az ország magyar neve | – |
| `ev` | az év | – |
| `gdp_volumen` | a reál-GDP (az árváltozástól megtisztított GDP), láncolt volumen, 2020-as áron | millió euró |
| `hicp` | a harmonizált fogyasztóiár-index éves átlagos változása az előző évhez képest | % |
| `letoltve` | a letöltés napja | dátum |

## Amit tudni kell

- **Két év közötti reálnövekedés:** a volumen hányadosából számolj (`gdp_volumen[ig] / gdp_volumen[tol] - 1`), ne az éves növekedési ütemek összeadásával. A láncolt volumen országon belül, időben hasonlítható össze; országok között a szintje nem (a változása igen).
- **A legutolsó év előzetes adat** (az Eurostatnál `p` jelzéssel), és a korábbi évek adatát is felülvizsgálják: az élő lekérés eltérhet ettől a táblától.
- A HICP az Eurostat uniós módszertanú indexe; Magyarországra nem azonos a KSH fogyasztóiár-indexével (lásd `inflacio_eves.md`).
