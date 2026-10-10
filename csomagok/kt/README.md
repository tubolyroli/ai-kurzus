# Projektcsomag: „Mit tervezett a költségvetés, és mi lett?”

Ebben a csomagban megkapod a záró projekt alapanyagát: a Költségvetési Tanács (KT) véleményeinek és kitekintéseinek szövegét oldalanként (2023. október – 2026. augusztus, 14 dokumentum), egy működő adatlekérő függvényt az Eurostat kormányzati hiány- és adósságadataihoz, egy adatszótár-vázat és egy ellenőrző script mintáját. A projekt alakja: **egy dokumentum állít valamit, az ágens a nyers adatból megnézi, mi lett belőle.** A RAG megtalálja az állítást (dokumentum, oldal), az ágens lekéri a tényadatot, számol és összevet, az ellenőrző script pedig a nyers adatból újraszámolja az elvárt értéket.

## Mi van benne

| Fájl | Mi ez |
| :--- | :--- |
| `forrasok.csv` | a 14 dokumentum listája: fájlnév, dátum, letöltési cím, cím, oldalszám-eltolás |
| `data/szoveg.jsonl` | a 14 dokumentum szövege oldalanként (ebből dolgozz, ne a PDF-ből; lásd lent) |
| `dokumentumok.py` | `osszes_oldal()`, `dokumentum_oldalai()`, `oldal_szovege()`: a szöveg betöltése |
| `adatlekeres.py` | `kormanyzati_adat()`: hiány és adósság az Eurostattól; `dokumentumok_letoltese()`: a PDF-ek letöltése |
| `data/tartalek.csv` | mentett adat arra az esetre, ha nincs net (ne írd felül) |
| `adatszotar.md` | az adatszótár váza: mit jelentenek a dokumentumok és az adatok. **A `TODO`-kat nektek kell kitölteni.** |
| `ellenorzes.py` | ellenőrző script minta két példakérdésre |
| `AGENTS.md` | a projekt szabályai az AI-asszisztensnek (bővítsétek) |
| `requirements.txt` | a szükséges Python-csomagok (ugyanazok, mint a kurzus notebookjaihoz) |

**Egy fontos különbség az MNB-jelentésekhez képest:** a KT 14 dokumentumából 11 aláírt, beszkennelt PDF. A PDF-be ágyazott szöveg ezeknél rossz: például a 77,5 helyén `JJ ,5` áll, így a RAG éppen a számoknál tévedne. Ezért a szkennelt oldalakat újra felismertettem (OCR, Tesseract), és a szöveget oldalanként a `data/szoveg.jsonl`-be tettem; a 3 digitális kitekintés szövege a PDF-ből jön. **Ebből dolgozz, ne a PDF-ből.** Ez is gépi felismerés: ritkán maradhat benne hiba (főleg táblázatban és ábrán: egy elveszett tizedesvessző, egy `%` helyett szám). Ezért egy idézett számot mindig nézz meg a PDF-ben is, a megadott oldalon. Részletek az `adatszotar.md`-ben.

A PDF-ek nincsenek a zipben (az Országgyűlés honlapján elérhetők): az ellenőrzéshez töltöd le őket a `dokumentumok/` mappába. A `.gitignore` miatt ezek nem kerülnek a repótokba.

## Hogyan indulj

1. Csomagold ki a zipet, és a kapott `projekt-kt` mappát nyisd meg a VS Code-ban. Ez lesz a (közös) repótok kiindulópontja.
2. Hozd létre a környezetet, ahogy a notebookoknál: parancspaletta → `Python: Create Environment` → `Venv`, és pipáld be a `requirements.txt`-t.
3. A VS Code termináljában töltsd le a PDF-eket (kb. 25 MB). A munkához a szöveg már megvan, a PDF az idézett számok ellenőrzéséhez kell:

   ```
   python -c "from adatlekeres import dokumentumok_letoltese; dokumentumok_letoltese()"
   ```

4. Próbáld ki az adatlekérést:

   ```
   python adatlekeres.py
   ```

5. Futtasd az ellenőrző scriptet: `python ellenorzes.py`. Az A kérdésre kiírja az elvárt értéket, a B-re azt, hogy `MÉG NINCS KÉSZ`. Hogy miért, azt az `ellenorzes.py` és az `adatszotar.md` megmondja.

## A dokumentumok szövege

A `data/szoveg.jsonl` minden sora egy oldal, ugyanolyan szótár, mint a 3. alkalom `jelentes_oldalai()` függvényénél, csak a bekezdések helyett nyers blokkok vannak benne (amit a pymupdf `get_text("blocks")` adna, `blokk[4]`):

```python
from dokumentumok import osszes_oldal, oldal_szovege

oldalak = osszes_oldal()     # 489 oldal, a forrasok.csv sorrendjében
oldalak[4]
# {"fajl": "kt-2023-10-03.pdf", "jelentes": "2023-10-03", "pdf_oldal": 5, "oldal": 5,
#  "szoveg_forrasa": "ocr", "blokkok": ["A Tanács 6/2023.10.03. sz. határozatával …", …]}

oldal_szovege("kt-2024-11-07.pdf", 5)   # egy oldal szövege egyben, pl. egy idézet ellenőrzéséhez
```

A `szoveg_forrasa` `"ocr"` (szkennelt oldal, újra felismerve) vagy `"pdf"` (digitális oldal). Az `oldal` a nyomtatott oldalszám (a KT-dokumentumokban megegyezik a PDF-oldallal). A 3. alkalom kódja két sor cseréjével működik rajta: az `oldal_bekezdesei`-ben a `for blokk in oldal.get_text("blocks"):` helyett `for blokk in oldal["blokkok"]:`, és `tisztit(blokk[4])` helyett `tisztit(blokk)`. A `jelentes_oldalai` itt nem kell: az oldalakat az `osszes_oldal()` adja. Az élőfej itt `A Tanács … sz. határozatával elfogadva`. Vigyázz: a 3. alkalom szűrője kidobja az öt szónál rövidebb blokkokat, a KT-nál viszont a táblázatok sorai is blokkok, és ezekben vannak a számok.

Ha a `forrasok.csv`-be olyan dokumentum kerül, amely nincs a `szoveg.jsonl`-ben, a `dokumentumok.py` a letöltött PDF szövegrétegét olvassa helyette, ugyanebben az alakban.

## Az adatlekérő függvény

```python
from adatlekeres import kormanyzati_adat

kormanyzati_adat("egyenleg", "2025")                               # egy év, a GDP %-ában
kormanyzati_adat("adossag", "2020", "2025")                        # hat év
kormanyzati_adat("egyenleg", "2025", mertekegyseg="millio_ft")     # millió forintban
```

Az első paraméter a mutató (`"egyenleg"` vagy `"adossag"`), utána az első és az utolsó év (`"ÉÉÉÉ"`), végül a mértékegység (`"gdp_szazalek"`, ez az alapértelmezés, vagy `"millio_ft"`). Egy rövid szótárat ad vissza, például:

```python
{"forras": "Eurostat, gov_10dd_edpt1 (Magyarország, kormányzati szektor)",
 "mutato": "a kormányzati szektor (S13) egyenlege, Eurostat B9: nettó hitelnyújtás (+) / nettó hitelfelvétel (-)",
 "mertekegyseg": "a GDP százalékában",
 "adat_honnan": "élő, letöltve 2026-10-10 00:12",
 "adatok": {"2025": -4.7}}
```

Ha valami nem stimmel (elírt paraméter, olyan év, amelyre nincs adat), a szótárban `hiba` kulcs van, és benne a magyarázat. Ezt szándékosan írtam így: a 9. alkalomtól ez a függvény lesz az ágensetek egyik eszköze, és az ágens a hibaüzenetből tud javítani. Ugyanezért kicsi a válasz: egyszerre legfeljebb 30 évet ad vissza, hogy beférjen a modell kontextusába.

**Ha nincs net**, vagy az Eurostat szervere épp nem válaszol, a függvény a `data/tartalek.csv`-ből dolgozik, és ezt ki is írja:

```
Nincs net, vagy nem érem el a forrást (URLError). A mentett adatot használom: data/tartalek.csv, mentve 2026-10-10.
```

A válaszban az `adat_honnan` mező mondja meg, melyik adatot kaptad. Ez itt különösen fontos, mert az Eurostat évente kétszer a korábbi évek adatát is felülvizsgálja (lásd `adatszotar.md`).

## Példakérdések

Ezek mintát adnak a saját 10 tesztkérdésetekhez. Az elvárt választ a futtatás *előtt* írjátok le, a számot script számolja.

- **A (csak adat):** Melyik évben volt a legalacsonyabb a kormányzati szektor GDP-arányos adóssága 2020 és 2025 között, és mennyi volt?
- **B (dokumentum és adat):** Mekkora hiánnyal számolt eredetileg a 2025. évi költségvetési törvény, mekkora lett a tényleges hiány, és mennyivel tért el a kettő?
- **C (csak dokumentum):** Hány százalékra emelte a kormány 2025 novemberében a 2025-ös hiánycélt?
- **D (előbb nézd meg, benne van-e egyáltalán a forrásokban):** Mekkora hiánnyal számol a 2027. évi központi költségvetésről szóló törvényjavaslat?

Az `ellenorzes.py` az A és a B kérdést ellenőrzi. A válaszfájl egy szöveges (Markdown) fájl, benne `## A` és `## B` című szakasz:

```
python ellenorzes.py              # csak az elvárt értékek
python ellenorzes.py valasz.md    # a válasz ellenőrzése: RENDBEN / HIBA
```

## Frissítési próba

A bemutató előtt két nappal kikerül egy frissítés: új sor(ok) a `forrasok.csv`-be (új KT-dokumentum), az új dokumentum szövege a `data/szoveg.jsonl`-be, és ha közben az Eurostat új adatot közölt, frissebb `data/tartalek.csv`. Ezeket a fájlokat kell lecserélnetek. A rendszereteknek ezzel utómunka nélkül kell lefutnia: új dokumentum letöltése, darabolás, index, ágens, ellenőrzés. Ha mégis kódot kellett módosítanotok, a dokumentációban leírjátok, mit és miért. Érdemes most úgy írni a kódot, hogy minden a `forrasok.csv`-ből induljon, és semmi ne legyen beégetve a 14 dokumentumról.

## Források

- Költségvetési Tanács, vélemények, határozatok és kitekintések, 2023–2026 (parlament.hu/web/koltsegvetesi-tanacs; a pontos címek a `forrasok.csv`-ben).
- Eurostat, *Government deficit/surplus, debt and associated data* (`gov_10dd_edpt1`), adat-API (JSON).
- A szkennelt dokumentumok szövege (`data/szoveg.jsonl`): saját karakterfelismerés, Tesseract 5.5 (magyar és angol modell), 2026. október.
