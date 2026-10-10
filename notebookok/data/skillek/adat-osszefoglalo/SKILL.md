---
name: adat-osszefoglalo
description: Egy gazdasági mutató (pl. munkanélküliség, infláció) alakulásának rövid összefoglalója egy időszakra, táblázattal és forrással. Akkor használd, ha egy idősort kell összefoglalni.
---

# Adat-összefoglaló

## Lépések

1. Ha a kérdés relatív időszakot mond („az utóbbi 5 évben”), előbb kérd le a mai dátumot (`mai_datum`). Az időszak vége a legutolsó év, amelyre már van adat (az adatlekérés eredménye megmondja, mi érhető el); az eleje ehhez igazodjon. Példa: ha ma 2026 van, és az éves adat 2025-ig van meg, az „utóbbi 5 év” 2021–2025. Ha kevesebb évet kaptál, mint amennyit a kérdés kér, kérd le újra a helyes időszakot.
2. Az adatot eszközzel kérd le. Számot ne írj fejből.
3. A változást a `szamol` eszközzel számold ki. Ha a mutató maga is százalék (ráta, infláció), a változást százalékpontban add meg.

## A válasz formája

- Egy Markdown-táblázat két oszloppal: `| Év | Érték (%) |`, minden évvel, egy tizedesre, tizedesvesszővel (4,4).
- Utána legfeljebb három mondat: a kezdő és a záró érték, a változás százalékpontban, a legmagasabb és a legalacsonyabb év.
- Ha egy év hiányzik az adatból, ne pótold: írd ki, melyik hiányzik.
- Az utolsó sor: `Forrás: <az adat forrása és kódja, ahogy az eszköz megadta>, <élő vagy mentett adat>.`
