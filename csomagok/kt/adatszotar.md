# Adatszótár: KT-csomag

Mit jelentenek a dokumentumok és az adatok. Ha valami itt nincs leírva, ne találgass: kérdezz, és írd be a választ ide (forrással).

Ez egy váz. A `TODO`-val jelölt részeket nektek kell kitölteni (párban), a dokumentumok és az adatforrás leírása alapján.

## Dokumentumok

A Költségvetési Tanács (KT) véleményei, határozatai és hároméves kitekintései, 2023. októbertől 2026. augusztusig, 14 PDF: vélemények a költségvetési törvényjavaslatokról (tervezet és zárószavazás), a költségvetés évközi végrehajtásáról és a zárszámadásról (az előző év végrehajtásáról), valamint három kitekintés. A szövegük oldalanként a `data/szoveg.jsonl`-ben van (lent). A PDF-ek nincsenek a csomagban: az `adatlekeres.dokumentumok_letoltese()` tölti le őket a `dokumentumok/` mappába, ellenőrzéshez.

`forrasok.csv` (pontosvessző, UTF-8):

| Oszlop | Jelentés |
| :--- | :--- |
| `fajl` | a PDF neve a `dokumentumok/` mappában |
| `jelentes` | a dokumentum dátuma (a KT határozatáé), `ÉÉÉÉ-HH-NN` |
| `url` | letöltési cím (parlament.hu) |
| `cim` | a dokumentum címe, hivatkozáshoz |
| `oldal_eltolas` | PDF-oldalszám mínusz nyomtatott oldalszám |

- **Oldalszám:** a nyomtatott oldalszám megegyezik a PDF-oldallal (`oldal_eltolas` = 0). Az első oldal és a mellékletek egy része számozatlan.
- **Szkennelt dokumentumok:** a 11 vélemény és határozat aláírt, beszkennelt PDF. A PDF-be ágyazott szövegréteg ezeknél rossz (`JJ ,5` a `77,5` helyett, `száza|ék`, `áIlamháztartás`), ezért ne a PDF-ből olvasd a szöveget. A szkennelt oldalakat újra felismertettem (Tesseract, magyar és angol modell, 300 dpi), a számok írásjeleit két további felismeréssel összevetve. A három kitekintés (2024-01-05, 2025-02-24, 2025-12-18) eredeti digitális PDF, ezek szövege a PDF-ből jön.
- **Mennyire pontos:** folyó szövegben a számok szinte hibátlanok (szúrópróbán 48-ból 47 jó; a hibás egy lábjegyzetszám). Táblázatban és ábrán gyakoribb a hiba (szúrópróbán 26-ból 2 rossz): elveszett tizedesvessző (`3513` a `351,3` helyett), `%` helyett számjegyek (`100,09` a `100,0%` helyett), dőlt betűs táblázatsorban elrontott szám; az ábrák tengelyfeliratai és adatcímkéi gyakran olvashatatlanok. Ezért egy idézett számot mindig nézz meg a PDF megadott oldalán.
- **Szöveghibák:** ritkán egy-egy betű (`mig` a `míg` helyett), és a lábjegyzetszám egybeolvadhat a szöveggel (`2 196/2021.` a `²196/2021.` helyett).

`data/szoveg.jsonl` (UTF-8, soronként egy oldal, JSON; betöltés: `dokumentumok.py`):

| Mező | Jelentés |
| :--- | :--- |
| `fajl` | a PDF neve (mint a `forrasok.csv`-ben) |
| `jelentes` | a dokumentum dátuma, `ÉÉÉÉ-HH-NN` |
| `pdf_oldal` | a PDF-oldal sorszáma, 1-től |
| `oldal` | a nyomtatott oldalszám (`pdf_oldal` − `oldal_eltolas`) |
| `szoveg_forrasa` | `ocr` (szkennelt oldal, újra felismerve) vagy `pdf` (digitális oldal, a PDF szövegrétegéből) |
| `blokkok` | az oldal szövegblokkjai (nagyjából bekezdések, táblázatsorok) fentről lefelé; a sorok `\n`-nel, a sor végi elválasztás megmaradt |

- A vélemények szó szerint idézik a korábbi véleményeket (idézőjelben). Egy szám tehát több dokumentumban is előfordulhat: a válaszban mindig mondd meg, melyik dokumentumból és melyik évre szól.

## Adatok: `kormanyzati_adat(mutato, tol, ig, mertekegyseg)`

Forrás: Eurostat, `gov_10dd_edpt1` (*Government deficit/surplus, debt and associated data*), Magyarország, kormányzati szektor (`S13`), éves adat 2010-től. A függvény először a netről kéri le az adatot; ha nem sikerül, a `data/tartalek.csv`-ből dolgozik, és ezt kiírja. A visszaadott szótár `adat_honnan` mezője mondja meg, melyik történt.

| Paraméter | Érték | Eurostat-kód | Jelentés |
| :--- | :--- | :--- | :--- |
| `mutato` | `egyenleg` | `B9` | a kormányzati szektor egyenlege (nettó hitelnyújtás / nettó hitelfelvétel); **negatív érték = hiány** |
| `mutato` | `adossag` | `GD` | a kormányzati szektor konszolidált bruttó adóssága, év végén |
| `mertekegyseg` | `gdp_szazalek` | `PC_GDP` | a GDP százalékában |
| `mertekegyseg` | `millio_ft` | `MIO_NAC` | millió forint, folyó áron |

- **Mértékegység:** a dokumentumok többnyire milliárd forintban írnak. 1 milliárd forint = 1000 millió forint: az Eurostat 2022-es `-4 092 620,1` (millió Ft) értéke 4 092,6 milliárd forint hiány.
- **Gyakoriság és felülvizsgálat:** az Eurostat évente kétszer (április végén és október végén) közli és **felülvizsgálja** az adatot, a korábbi évekét is. Egy régebbi dokumentumban a „tényleges” érték ezért eltérhet attól, amit ma letöltesz. Ilyenkor nem a dokumentum téved: a válaszban mondd meg, melyik közlésből (milyen dátumú adatból) származik a szám.
- A `data/tartalek.csv` oszlopai: `mutato;mertekegyseg;ev;ertek;letoltve` (Eurostat-kódokkal, pont a tizedesjel). A `letoltve` a mentés napja. Ezt a fájlt ne írd felül.

## Melyik hiányszám mihez?

TODO: Pontosan milyen hiányfogalmat mér az Eurostat `B9` egyenlege (melyik szektor, milyen elszámolás)? A dokumentumok melyik hiányszámával vethető össze? Írd ide a választ, és hogy honnan tudod (dokumentum, oldal).

TODO: Mit tegyen az ágens, ha a kérdésből nem derül ki, melyik évre vagy melyik dokumentumra vonatkozik?
