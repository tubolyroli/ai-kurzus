"""Gépcsekk az első órára: megnézi, hogy a Python, a Git és a netkapcsolat rendben van-e."""
import platform
import shutil
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

eredmenyek = []


def ellenoriz(nev, sikerult, tipp=""):
    """Kiír egy RENDBEN/HIBA sort, és megjegyzi az eredményt."""
    eredmenyek.append(sikerult)
    if sikerult:
        print(f"RENDBEN  {nev}")
    else:
        print(f"HIBA     {nev}\n         -> {tipp}")


ellenoriz(
    f"Python {platform.python_version()}",
    sys.version_info >= (3, 12),
    "Régi a Python. Telepítsd a legújabbat a python.org-ról.",
)

git = shutil.which("git")
ellenoriz("Git telepítve", git is not None,
          "Nem találom a gitet. Telepítsd, aztán indítsd újra a VS Code-ot.")

if git:
    for kulcs, magyarul in [("user.name", "név"), ("user.email", "e-mail")]:
        ertek = subprocess.run([git, "config", "--global", kulcs],
                               capture_output=True, text=True).stdout.strip()
        ellenoriz(f"Git-{magyarul}: {ertek or '(nincs beállítva)'}", bool(ertek),
                  f'Futtasd a terminálban: git config --global {kulcs} "..."')

# A python.org-os macOS-Python tanúsítványok nélkül érkezik; ez itt derül ki.
try:
    urllib.request.urlopen("https://www.python.org", timeout=10)
    ellenoriz("HTTPS-kapcsolat", True)
except urllib.error.URLError as hiba:
    if isinstance(hiba.reason, ssl.SSLCertVerificationError):
        tipp = ("Macen: Finder > Alkalmazások > Python 3.14 mappa, "
                "dupla katt az Install Certificates.command fájlra.")
    else:
        tipp = f"Nincs internet, vagy tűzfal blokkolja. ({hiba.reason})"
    ellenoriz("HTTPS-kapcsolat", False, tipp)

print()
if all(eredmenyek):
    print("Minden RENDBEN. Készen állsz az első órára!")
else:
    print("Van HIBA. Kövesd a tippet, vagy hozd el így az órára, megoldjuk ott.")
