# Parník Praha, redesign „PLAVBA"

Návrh redesignu webu [parnik.cz](https://www.parnik.cz/).
Statický web bez buildu. Stačí otevřít `index.html` a jede.

---

## Koncept

**Web je loď.** Návštěvník nelistuje stránkou, *pluje*. Homepage je jedna souvislá
plavba po Vltavě, podrobnosti jsou na samostatných podstránkách.

Barevná dramaturgie kopíruje denní dobu plavby:

```
úsvit (hero) > den (nabídka plaveb) > noc (trasa) > bílá (kam dál) > soumrak (rezervace)
```

### Signature prvky

| Prvek | Co dělá |
|-------|---------|
| **Panorama trasy** | Sticky sekce 460 vh. Vertikální scroll posouvá horizontální SVG panorama Prahy. Loď stojí, Praha plyne kolem. Zastávky (Čechův most, Hrad, Karlův most, Národní divadlo, Tančící dům, Vyšehrad) se prolínají podle pozice. |
| **Paluba v popředí hera** | Silueta zábradlí s mosazným madlem a teakovým čepcem, jemné houpání 0,3 stupně za 9 s. Dojem, že stojíte na palubě a díváte se přes zábradlí na vodu. |
| **Lodní lano** | Scroll progress nahoře. Mosazné lano s parníkem, který po něm pluje. |
| **Lodní lístky** | Nabídka plaveb jako perforované jízdenky s mosazným hřbetem a časy odjezdů. |
| **Odlesk hladiny** | Nad hřebenem vlny běží tenká mosazná linka ve stejném rytmu jako vlna. Měsíční svit na vodě. |
| **Portholes** | Kruhové masky s mosazným prstencem místo generických obrázkových karet. |
| **Vlnové předěly** | Sekce oddělené SVG vlnou přes `mask`, takže barva se dědí z tokenu. |
| **Dárkový certifikát** | Reálně vypadající certifikát s deco rámečkem a přejezdem lesku. |

Kompletní design system včetně odůvodnění odchylek: [`design-system/MASTER.md`](design-system/MASTER.md).

---

## Struktura

```
parnikWEB/
├─ index.html                 hero + nabídka plaveb + trasa + rozcestník
├─ na-palube.html             salon, bar, kuchyně, horní paluba
├─ pronajem.html              soukromé plavby, flotila, postup
├─ certifikaty.html           dárkové certifikáty, jak to funguje
├─ galerie.html               fotogalerie
├─ kontakt.html               rezervace, poptávkový formulář, kontakty
├─ assets/
│  ├─ css/style.css           design tokeny a všechny komponenty
│  └─ js/main.js              scroll engine, menu, validace formuláře
├─ design-system/MASTER.md    design system (zdroj pravdy)
├─ scripts/pano.py           generátor SVG panoramatu Prahy
└─ skills/ui-ux-pro-max/      skill použitý pro generování systému
```

Panorama v sekci Trasa je vygenerované skriptem `scripts/pano.py` a inlinované
v `index.html`. Skript je deterministický (`seed=7`), takže se dá kdykoliv
přegenerovat se stejným výsledkem. Není součástí buildu, pouští se ručně jen
při změně panoramatu.

Žádné `npm install`, žádný build krok, nula runtime závislostí.

---

## Spuštění

```bash
python -m http.server 5173
```

Pak otevřít <http://localhost:5173>.

---

## Technické poznámky

**Stack:** vanilla HTML, CSS a JS. Pro prezentaci s takhle custom vizuálem nemá
framework co nabídnout, jen by přidal build, závislosti a hydrataci. Takhle je to
hostovatelné kdekoliv (GitHub Pages, Netlify, libovolný FTP).

**Výkon**
* Vše scroll-driven běží v **jedné** `requestAnimationFrame` smyčce, animuje se
  jen `transform` a `opacity`, žádný layout thrashing.
* Obrázky `loading="lazy"` a `width`/`height` proti CLS, hero má `fetchpriority="high"`.
* Ikony jsou inline SVG. Žádná ikonová knihovna, žádný extra request.
* Fonty přes `preconnect` a `display=swap`.

**Vlny.** Tvar vlny má periodu 720 (resp. 480) jednotek v `viewBox` širokém 2880 a
posouvá se o přesně 1440, tedy o celý počet period. Proto se tiluje bez viditelného
švu. Překlopení vlny v patičce je na kontejneru, ne na `<svg>`, protože animace
`drift` nastavuje `transform` a přepsala by `scaleY(-1)`.

**Přístupnost**
* Kontrast ověřen skriptem na všech textových uzlech se správným kompozitováním
  průhledných vrstev. Na homepage 136 uzlů, nula pod limitem WCAG AA.
* `prefers-reduced-motion` vypíná parallax, houpání, vlny i panorama.
  Trasa se přepne na statickou vertikální timeline.
* Focus ring viditelný všude, skip-link, focus trap v mobilním menu, `Esc` zavírá.
* Formulář: `<label for>` u všech polí, chyby u pole a `aria-live`, `aria-invalid`.
* **Bez JS zůstane celá stránka čitelná.** `.reveal` se aktivuje až po přidání
  třídy `.js` na `<html>`.

**Responzivita**
* Testováno na 375, 768, 1024 a 1440 px, bez horizontálního scrollu.
* Pod 900 px se panorama trasy nahrazuje vertikální timeline, žádný scroll-jacking
  na mobilu.

---

## Co doplnit před ostrým nasazením

1. **Fotky.** Teď jsou použité stock fotky z Unsplash načítané přes CDN jako
   vizuální placeholder. Nahradit reálnými fotkami lodí a akcí a naservírovat je
   lokálně jako WebP se `srcset`.
2. **Ceny.** Původní web ceny na homepage neuvádí, v návrhu proto nejsou.
   Doporučuju je doplnit, je to nejčastější důvod odchodu z rezervačního toku.
3. **Napojení formuláře.** V `assets/js/main.js` je poptávkový formulář zatím
   demo (validace a simulované odeslání). Reálný endpoint se napojí v
   `form.addEventListener('submit', …)`, hledej komentář `TODO`.
   Doplnit i antispam (honeypot nebo Turnstile).
4. **Rezervační systém.** Tlačítko „Rezervovat" míří na poptávkový formulář.
   Pokud existuje rezervační engine, přesměrovat na něj.
5. **Údaje o flotile.** Tabulka lodí a kapacit na stránce Pronájem je orientační,
   „až 300 hostů" je odhad. Nechat potvrdit od klienta.
6. **Jazykové mutace.** CZ/EN/DE přepínač v patičce je zatím nefunkční, původní
   web mutace má.
7. **Mapa nalodění**, cookie lišta, GDPR stránka, `sitemap.xml`, analytika.

---

## Zdroje obsahu

Texty, časy odjezdů a kontakty vycházejí z aktuálního obsahu
[parnik.cz](https://www.parnik.cz/). Kontakty: `+420 604 696 969`,
`+420 773 903 903`, `info@parnik.cz`.
