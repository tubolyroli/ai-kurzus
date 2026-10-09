"""A kurzus közös segédmodulja: nyelvimodell-hívás és az ellenőrző cellák függvényei.

A nyelvi modellt sima HTTP-kéréssel hívjuk egy OpenAI-kompatibilis végponton, SDK nélkül.
A beállítások a `.env` fájlból vagy környezeti változókból jönnek, így a szolgáltató
(helyi Ollama, OpenAI, Gemini, Anthropic stb.) a kód átírása nélkül cserélhető.
Alapértelmezés: a gépen futó Ollama.
"""
import inspect
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

ALAPBEALLITAS = {
    "LLM_BASE_URL": "http://localhost:11434/v1",  # helyi Ollama
    "LLM_API_KEY": "ollama",                       # az Ollama nem kér kulcsot, de a mező kötelező
    "LLM_MODEL": "gemma4:e4b",
    "EMBED_MODEL": "bge-m3",
}

# Az utolsó hívás tokenhasználata (prompt_tokens, completion_tokens), a költségbecsléshez.
utolso_hasznalat = {}


def _env_fajl():
    """Beolvassa a legközelebbi `.env` fájlt (a mappától felfelé keresve), ha van."""
    for mappa in [Path.cwd(), *Path.cwd().parents]:
        fajl = mappa / ".env"
        if fajl.is_file():
            ertekek = {}
            for sor in fajl.read_text(encoding="utf-8").splitlines():
                sor = sor.strip()
                if sor and not sor.startswith("#") and "=" in sor:
                    kulcs, ertek = sor.split("=", 1)
                    ertekek[kulcs.strip()] = ertek.strip().strip('"').strip("'")
            return ertekek
    return {}


def beallitas(nev):
    """Egy beállítás értéke: környezeti változó, ennek híján `.env`, ennek híján az alapértelmezés."""
    return os.environ.get(nev) or _env_fajl().get(nev) or ALAPBEALLITAS[nev]


def _keres(utvonal, adat):
    """POST-kérés a beállított végpontra; a választ szótárként adja vissza."""
    url = beallitas("LLM_BASE_URL").rstrip("/") + utvonal
    keres = urllib.request.Request(
        url,
        data=json.dumps(adat).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {beallitas('LLM_API_KEY')}"},
    )
    try:
        with urllib.request.urlopen(keres, timeout=600) as valasz:
            return json.loads(valasz.read())
    except urllib.error.URLError as hiba:
        if "localhost" in url or "127.0.0.1" in url:
            raise RuntimeError(
                f"Nem érem el a helyi modellt ({url}). Fut az Ollama? "
                "Indítsd el az Ollama alkalmazást, vagy a terminálban: ollama serve"
            ) from hiba
        raise


def chat(uzenetek, eszkozok=None, modell=None, homerseklet=0.0, gondolkodas=None, max_tokens=None):
    """Elküldi az üzenetlistát a modellnek, és visszaadja a válaszüzenetet (szótár).

    Az `eszkozok` az OpenAI-formátumú eszközleírások listája. A válaszban vagy szöveg
    (`content`), vagy eszközhívás (`tool_calls`) van. A gondolkodó modelleknél a
    `gondolkodas` szabályozza, gondolkodjon-e válasz előtt. A helyi Gemmánál csak a
    "none" számít: kikapcsolja (kb. ötször gyorsabb, de gyengébb válasz).
    """
    adat = {"model": modell or beallitas("LLM_MODEL"), "messages": uzenetek,
            "temperature": homerseklet, "seed": 42}
    if eszkozok:
        adat["tools"] = eszkozok
    if gondolkodas:
        adat["reasoning_effort"] = gondolkodas
    if max_tokens:
        adat["max_tokens"] = max_tokens  # a válasz hosszának felső korlátja (tokenben)
    valasz = _keres("/chat/completions", adat)
    utolso_hasznalat.clear()
    utolso_hasznalat.update(valasz.get("usage", {}))
    _csonkolas_figyelmeztetes(adat, utolso_hasznalat.get("prompt_tokens", 0))
    return valasz["choices"][0]["message"]


def _csonkolas_figyelmeztetes(adat, prompt_tokens):
    """Szól, ha a helyi modell levágta a kérést, mert nem fért a kontextusablakba.

    Az Ollama ilyenkor nem ad hibát: csendben eldobja a kérés elejét, és a modell úgy válaszol,
    mintha a levágott rész ott se lett volna. A régebbi Ollama az ablakot színültig töltötte
    (prompt_tokens = ablak − 1), az újabb (0.40-től) az ablak felére-háromnegyedére vágja vissza
    a kérést, így a tokenszámból önmagában nem látszik. Ezért ha a kérés legalább fél ablaknyi,
    megkérdezzük az Ollamát levágás nélkül is (`truncate: false`): ha nem fér bele, hibát ad,
    benne a kérés valódi hosszával. Ha a kérés belefér, ez egy gyors, gyorsítótárazott hívás.
    """
    url = beallitas("LLM_BASE_URL")
    if prompt_tokens < 1000 or not ("localhost" in url or "127.0.0.1" in url):
        return
    gyoker = url.rstrip("/").removesuffix("/v1")
    try:
        with urllib.request.urlopen(gyoker + "/api/ps", timeout=5) as v:
            futo = json.loads(v.read()).get("models", [])
    except (urllib.error.URLError, ValueError, OSError):
        return
    ablak = next((m.get("context_length") for m in futo if m.get("name") == adat["model"]), None)
    if not ablak or prompt_tokens < ablak // 2:
        return
    valodi = prompt_tokens if prompt_tokens >= ablak - 1 else _valodi_hossz(gyoker, adat)
    if valodi and valodi > prompt_tokens:
        print(f"FIGYELEM: a kérés nem fért a modell kontextusablakába ({ablak} token): {valodi} token volt, "
              f"ebből a modell csak az utolsó {prompt_tokens} tokent látta, az eleje levágódott.")
    elif prompt_tokens >= ablak - 1:
        print(f"FIGYELEM: a kérés nem fért a modell kontextusablakába ({ablak} token), az eleje levágódott. "
              "A modell a levágott részt nem látta.")


def _valodi_hossz(gyoker, adat):
    """A kérés tokenszáma levágás nélkül, ha nem fér az ablakba (az Ollama hibaüzenetéből); különben None."""
    proba = {"model": adat["model"], "messages": adat["messages"], "stream": False, "think": False,
             "truncate": False, "options": {"num_predict": 1, "temperature": 0, "seed": 42}}
    if adat.get("tools"):
        proba["tools"] = adat["tools"]
    keres = urllib.request.Request(gyoker + "/api/chat", data=json.dumps(proba).encode("utf-8"),
                                   headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(keres, timeout=600):
            return None                                   # belefért: nincs levágás
    except urllib.error.HTTPError as hiba:
        szoveg = hiba.read().decode("utf-8", "replace")
        talalat = re.search(r"request \((\d+) tokens\) exceeds", szoveg)
        return int(talalat.group(1)) if talalat else None
    except (urllib.error.URLError, ValueError, OSError):
        return None


def kerdez(kerdes, rendszer=None, modell=None, gondolkodas=None, max_tokens=None):
    """Egyetlen kérdés, egyetlen szöveges válasz. A `rendszer` a rendszerprompt."""
    uzenetek = [{"role": "system", "content": rendszer}] if rendszer else []
    uzenetek.append({"role": "user", "content": kerdes})
    return chat(uzenetek, modell=modell, gondolkodas=gondolkodas, max_tokens=max_tokens)["content"]


def embed(szovegek, modell=None):
    """Szövegek (vagy egyetlen szöveg) vektorrá alakítása; vektorok listáját adja vissza."""
    if isinstance(szovegek, str):
        szovegek = [szovegek]
    valasz = _keres("/embeddings", {"model": modell or beallitas("EMBED_MODEL"), "input": szovegek})
    return [elem["embedding"] for elem in sorted(valasz["data"], key=lambda e: e["index"])]


def letolt(url, cel):
    """Letölt egy fájlt, ha még nincs meg; a helyi útvonalát adja vissza.

    A nagy forrásfájlok (pl. MNB-jelentések PDF-ben) nem részei a kurzus csomagjának:
    az első futtatáskor töltődnek le, utána a helyi példány kerül elő.
    """
    cel = Path(cel)
    if not cel.exists():
        cel.parent.mkdir(parents=True, exist_ok=True)
        keres = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (kurzus-notebook)"})
        with urllib.request.urlopen(keres, timeout=300) as valasz:
            cel.write_bytes(valasz.read())
    return cel


# ---------------------------------------------------------------- ellenőrzés

def _szep(x):
    """Tört számot legfeljebb 4 értékes jeggyel ír ki, mást változatlanul."""
    return f"{x:.4g}" if isinstance(x, float) else repr(x)


def _hivo_valtozoi():
    """A notebook változói: annak a cellának a névtere, amelyik az ellenőrzést hívta."""
    return inspect.currentframe().f_back.f_back.f_globals


def ellenoriz(nev, vart, tures=0.01):
    """Megnézi, hogy a `nev` nevű változó értéke egyezik-e a várttal, és kiírja az eredményt."""
    kapott = _hivo_valtozoi().get(nev)
    if kapott is None:
        print(f"MÉG NINCS KÉSZ  {nev}")
        return
    if isinstance(vart, float) or isinstance(kapott, float):
        jo = isinstance(kapott, (int, float)) and abs(kapott - vart) <= tures
    else:
        jo = kapott == vart
    if jo:
        print(f"RENDBEN  {nev} = {_szep(kapott)}")
    else:
        print(f"HIBA     {nev} = {_szep(kapott)}, a helyes érték: {_szep(vart)}")


def ellenoriz_fuggveny(nev, esetek, tures=0.01):
    """Lefuttatja a `nev` nevű függvényt a megadott bemenetekre, és összeveti a várt kimenettel."""
    fuggveny = _hivo_valtozoi().get(nev)
    if not callable(fuggveny):
        print(f"MÉG NINCS KÉSZ  {nev}()")
        return
    for bemenet, vart in esetek:
        kapott = fuggveny(*bemenet)
        if isinstance(vart, float):
            jo = isinstance(kapott, (int, float)) and abs(kapott - vart) <= tures
        else:
            jo = kapott == vart
        print(f"{'RENDBEN' if jo else 'HIBA   '}  {nev}{bemenet} = {_szep(kapott)}"
              + ("" if jo else f", a helyes: {_szep(vart)}"))


def ellenoriz_feltetel(nev, feltetel, leiras):
    """Szöveges (pl. LLM-) válaszokhoz: a `feltetel` egy függvény, amely a változó értékét vizsgálja.

    Nem a modell dönti el, hogy jó-e a válasza: a feltételt mi írjuk meg előre
    (pl. „a válaszban szerepel a forrás oldalszáma”).
    """
    kapott = _hivo_valtozoi().get(nev)
    if kapott is None:
        print(f"MÉG NINCS KÉSZ  {nev}")
        return
    jo = bool(feltetel(kapott))
    print(f"{'RENDBEN' if jo else 'HIBA   '}  {nev}: {leiras}")
