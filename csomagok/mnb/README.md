# Projektcsomag: „Mit ígért az MNB, és mi lett?”

Ebben a csomagban megkapod a záró projekt alapanyagát: az MNB Inflációs jelentéseit (2023. június – 2026. június, 13 jelentés), egy működő adatlekérő függvényt a KSH és az Eurostat inflációs adataihoz, egy adatszótár-vázat és egy ellenőrző script mintáját. A projekt alakja: **egy dokumentum állít valamit, az ágens a nyers adatból megnézi, mi lett belőle.** A RAG megtalálja az állítást (jelentés, oldal), az ágens lekéri a tényadatot, számol és összevet, az ellenőrző script pedig a nyers adatból újraszámolja az elvárt értéket.

## Mi van benne

| Fájl | Mi ez |
| :--- | :--- |
| `forrasok.csv` | a 13 jelentés listája: fájlnév, dátum, letöltési cím, cím, oldalszám-eltolás |
| `adatlekeres.py` | `inflacio()`: tényadat a KSH-tól vagy az Eurostattól; `dokumentumok_letoltese()`: a PDF-ek letöltése |
| `data/tartalek.csv` | mentett adat arra az esetre, ha nincs net (ne írd felül) |
| `adatszotar.md` | az adatszótár váza: mit jelentenek a dokumentumok és az adatok. **A `TODO`-kat nektek kell kitölteni.** |
| `ellenorzes.py` | ellenőrző script minta két példakérdésre |
| `AGENTS.md` | a projekt szabályai az AI-asszisztensnek (bővítsétek) |
| `requirements.txt` | a szükséges Python-csomagok (ugyanazok, mint a kurzus notebookjaihoz) |

A PDF-ek nincsenek a zipben (nagyok, és az MNB honlapján elérhetők): az első lépésben töltöd le őket a `dokumentumok/` mappába. A `.gitignore` miatt ezek nem kerülnek a repótokba.

## Hogyan indulj

1. Csomagold ki a zipet a `notebookok` mappád mellé (ne bele: az egy másik Git-repó), és a kapott `projekt-mnb` mappát nyisd meg a VS Code-ban. Ez lesz a (közös) repótok kiindulópontja.
2. Hozd létre a környezetet, ahogy a notebookoknál: parancspaletta → `Python: Create Environment` → `Venv`, és pipáld be a `requirements.txt`-t.
3. A VS Code termináljában töltsd le a jelentéseket (kb. 30 MB):

   ```
   python -c "from adatlekeres import dokumentumok_letoltese; dokumentumok_letoltese()"
   ```

4. Próbáld ki az adatlekérést:

   ```
   python adatlekeres.py
   ```

5. Futtasd az ellenőrző scriptet: `python ellenorzes.py`. Az A kérdésre kiírja az elvárt értéket, a B-re azt, hogy `MÉG NINCS KÉSZ`. Hogy miért, azt az `ellenorzes.py` és az `adatszotar.md` megmondja.

## Az adatlekérő függvény

```python
from adatlekeres import inflacio

inflacio("KSH", "2023-08")              # egy hónap
inflacio("Eurostat", "2023", "2025")    # éves átlagok, három év
```

Az első paraméter a forrás (`"KSH"` vagy `"Eurostat"`), a második és a harmadik az időszak: `"ÉÉÉÉ-HH"` havi, `"ÉÉÉÉ"` éves adatnál. Egy rövid szótárat ad vissza, például:

```python
{"forras": "KSH, fogyasztóiár-index (STADAT ara0039 / ara0001)",
 "mertekegyseg": "%, az előző év azonos hónapjához képest",
 "adat_honnan": "élő, letöltve 2026-10-10 00:12",
 "adatok": {"2023-08": 16.4}}
```

Ha valami nem stimmel (elírt forrásnév, olyan időszak, amelyre nincs adat), a szótárban `hiba` kulcs van, és benne a magyarázat. Ezt szándékosan írtam így: a 9. alkalomtól ez a függvény lesz az ágensetek egyik eszköze, és az ágens a hibaüzenetből tud javítani. Ugyanezért kicsi a válasz: egyszerre legfeljebb 60 időszakot ad vissza, hogy beférjen a modell kontextusába.

**Ha nincs net**, vagy a KSH szervere épp nem válaszol (sok egymás utáni kérésre egy időre letilt), a függvény a `data/tartalek.csv`-ből dolgozik, és ezt ki is írja:

```
Nincs net, vagy nem érem el a forrást (URLError). A mentett adatot használom: data/tartalek.csv, mentve 2026-10-10.
```

A mentett adat nem a legfrissebb, de a kérdéseitek többségéhez elég. A válaszban az `adat_honnan` mező mondja meg, melyik adatot kaptad.

## Példakérdések

Ezek mintát adnak a saját 10 tesztkérdésetekhez. Az elvárt választ a futtatás *előtt* írjátok le, a számot script számolja.

- **A (csak adat):** Hány hónapban volt 20 százalék fölött az éves infláció a KSH szerint 2022-ben és 2023-ban, és melyik hónapban volt a legmagasabb?
- **B (dokumentum és adat):** A 2023. szeptemberi Inflációs jelentés mekkora éves átlagos inflációt várt 2023-ra, és beleesett-e a tényleges érték az előrejelzési sávba?
- **C (csak dokumentum):** Mekkora az MNB középtávú inflációs célja?
- **D (előbb nézd meg, benne van-e egyáltalán a forrásokban):** Mekkora éves átlagos inflációt vár az MNB 2029-re?

Az `ellenorzes.py` az A és a B kérdést ellenőrzi. A válaszfájl egy szöveges (Markdown) fájl, benne `## A` és `## B` című szakasz:

```
python ellenorzes.py              # csak az elvárt értékek
python ellenorzes.py valasz.md    # a válasz ellenőrzése: RENDBEN / HIBA
```

## Frissítési próba

A bemutató előtt két nappal kikerül egy frissítés: új sor(ok) a `forrasok.csv`-be (új jelentés) és frissebb `data/tartalek.csv`. Ezt a két fájlt kell lecserélnetek. A rendszereteknek ezzel utómunka nélkül kell lefutnia: új jelentés letöltése, darabolás, index, ágens, ellenőrzés. Ha mégis kódot kellett módosítanotok, a dokumentációban leírjátok, mit és miért. Érdemes most úgy írni a kódot, hogy minden a `forrasok.csv`-ből induljon, és semmi ne legyen beégetve a 13 jelentésről.

## Források

- MNB, Inflációs jelentés, 2023. június – 2026. június (mnb.hu; a pontos címek a `forrasok.csv`-ben).
- KSH STADAT, 1.2.1.1. A főbb ármutatók, havonta (`ara0039`); 1.1.1.1. Főbb ármutatók (`ara0001`).
- Eurostat, HICP – ECOICOP ver. 2, havi (`prc_hicp_minr`) és éves (`prc_hicp_ainr`) adatok, adat-API (JSON).
