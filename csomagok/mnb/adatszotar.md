# Adatszótár: MNB-csomag

Mit jelentenek a dokumentumok és az adatok. Ha valami itt nincs leírva, ne találgass: kérdezz, és írd be a választ ide (forrással).

Ez egy váz. A `TODO`-val jelölt részeket nektek kell kitölteni (párban), a dokumentumok és az adatforrások leírása alapján.

## Dokumentumok

Az MNB negyedéves Inflációs jelentései, 2023. júniustól 2026. júniusig, 13 PDF. A fájlok nincsenek a csomagban: az `adatlekeres.dokumentumok_letoltese()` tölti le őket a `dokumentumok/` mappába.

`forrasok.csv` (pontosvessző, UTF-8):

| Oszlop | Jelentés |
| :--- | :--- |
| `fajl` | a PDF neve a `dokumentumok/` mappában |
| `jelentes` | a jelentés hónapja, `ÉÉÉÉ-HH` (március, június, szeptember, december) |
| `url` | letöltési cím (mnb.hu) |
| `cim` | a jelentés címe, hivatkozáshoz |
| `oldal_eltolas` | PDF-oldalszám mínusz nyomtatott oldalszám |

- **Oldalszám:** a nyomtatott oldalszám = PDF-oldal − 2 (minden számozott oldalon). A borító, a belső borító és a hátsó lapok számozatlanok. Hivatkozáskor a nyomtatott oldalszámot add meg, ha van; ha nincs, a PDF-oldalt („PDF 5. oldal”).
- **Előrejelzések:** a jelentések az éves átlagos inflációt általában sávként adják meg (pl. „17,6 – 18,1 százalék”), egy-egy évre előre. Ugyanabban a jelentésben múltbeli tényadat és előrejelzés is áll: a válaszban mindig mondd meg, melyik jelentésből és melyik évre szól a szám.

## Adatok: `inflacio(forras, tol, ig)`

Két adatsor, mindkettő Magyarországra, havi és éves bontásban. A függvény először a netről kéri le az adatot; ha nem sikerül, a `data/tartalek.csv`-ből dolgozik, és ezt kiírja. A visszaadott szótár `adat_honnan` mezője mondja meg, melyik történt.

| Forrás (`forras`) | Mi ez | Honnan | Havi adat | Éves adat |
| :--- | :--- | :--- | :--- | :--- |
| `KSH` | fogyasztóiár-index | KSH STADAT: `ara0039` (havi), `ara0001` (éves) | 2022-01-től | 2010-től |
| `Eurostat` | harmonizált fogyasztóiár-index (HICP) | Eurostat: `prc_hicp_minr` (havi), `prc_hicp_ainr` (éves), összesen (`TOTAL`) | 2022-01-től | 2010-től |

| Mező | Jelentés | Mértékegység | Gyakoriság |
| :--- | :--- | :--- | :--- |
| `idoszak` | `ÉÉÉÉ-HH` havi, `ÉÉÉÉ` éves adatnál | – | havi / éves |
| érték (havi) | az árszínvonal változása az előző év azonos hónapjához képest | % | havi |
| érték (éves) | az éves átlagos árszínvonal változása az előző év átlagához képest | % | éves |

- A KSH a táblázataiban indexet közöl (előző év = 100,0), például `116,4`. A függvény ebből 100-at levon: `16,4` (%).
- Az éves átlagot a KSH és az Eurostat az éves átlagos árszínvonalból számolja, nem a 12 havi érték számtani átlagaként. A kettő általában közel van, de eltérhet: éves kérdésre az éves adatot használd.
- **Frissesség:** a KSH a következő hónap első felében közli a havi adatot, az Eurostat általában néhány nappal később. Ezért előfordul, hogy a legutolsó hónap csak a KSH-nál van meg.
- A `data/tartalek.csv` oszlopai: `forras;idoszak;ertek;letoltve` (pont a tizedesjel). A `letoltve` a mentés napja. Ezt a fájlt ne írd felül.

## Melyik adatsor mihez?

TODO: Az MNB Inflációs jelentéseinek előrejelzéseit és tényadatait melyik adatsorral kell összevetni, a `KSH`- vagy az `Eurostat`-sorral? Miből derül ki? Írd ide a választ, és hogy honnan tudod (dokumentum, oldal).

TODO: Mikor (melyik kérdéstípusnál) kell a másik adatsor, ha egyáltalán kell?
