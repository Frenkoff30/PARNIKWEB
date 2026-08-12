# Parník Praha — redesign „PLAVBA"

Návrh redesignu webu [parnik.cz](https://www.parnik.cz/).
Statický web bez buildu — otevřít `index.html` a jede.

---

## Koncept

**Web je loď.** Návštěvník nelistuje stránkou, *pluje*. Stránka je jedna souvislá
plavba po Vltavě rozdělená na kapitoly I–VII. Na pozadí se v rytmu scrollu posouvá
panorama Prahy, dole je pořád voda, nahoře mosazná lišta můstku.

Barevná dramaturgie kopíruje denní dobu plavby:

```
úsvit (hero) → den (nabídka) → soumrak (na palubě) → noc (pronájem → rezervace)
```

### Signature prvky

| Prvek | Co dělá |
|---|---|
| **Panorama trasy** | Sticky sekce 460 vh — vertikální scroll posouvá horizontální SVG panorama Prahy. Loď stojí, Praha plyne kolem. Zastávky (Čechův most → Hrad → Karlův most → Národní divadlo → Tančící dům → Vyšehrad) se prolínají podle pozice. |
| **Paluba v popředí hera** | Silueta zábradlí + jemné houpání ±0,32° / 9 s. Dojem „stojím na palubě". |
| **Lodní lano** | Scroll progress nahoře — mosazné lano s parníkem, který po něm pluje. |
| **Kapitolový rail** | Vertikální rail vpravo (≥1280 px) s římskými čísly kapitol, jako značení palub. |
| **Lodní lístky** | Nabídka plaveb jako perforované jízdenky s mosazným hřbetem a časy odjezdů. |
| **Portholes** | Kruhové masky s mosazným prstencem místo generických obrázkových karet. |
| **Vlnové předěly** | Sekce oddělené SVG vlnou (přes `mask`, takže barva se dědí z tokenu). |
| **Dárkový certifikát** | Reálně vypadající certifikát s deco rámečkem a přejezdem lesku. |

Kompletní design system včetně odůvodnění odchylek: [`design-system/MASTER.md`](design-system/MASTER.md).

---

## Struktura

```
parnikWEB/
├─ index.html                 # celá stránka (jedna dlouhá plavba)
├─ assets/
│  ├─ css/style.css           # design tokeny + všechny komponenty
│  └─ js/main.js              # scroll engine, menu, validace formuláře
├─ design-system/MASTER.md    # design system (zdroj pravdy)
├─ skills/ui-ux-pro-max/      # skill použitý pro generování systému
└─ README.md
```

Žádné `npm install`, žádný build krok, nula runtime závislostí.

---

## Spuštění

Stačí otevřít `index.html`. Pro správné chování relativních cest doporučuji
lokální server:

```bash
python -m http.server 5173
```

Pak otevřít <http://localhost:5173>.

---

## Technické poznámky

**Stack:** vanilla HTML + CSS + JS. Pro jednostránkovou prezentaci s takhle
custom vizuálem nemá framework co nabídnout — přidal by build, závislosti a
hydrataci navíc. Takhle je to hostovatelné kdekoliv (GitHub Pages, Netlify,
libovolný FTP).

**Výkon**
- Vše scroll-driven běží v **jedné** `requestAnimationFrame` smyčce, animuje se
  jen `transform` a `opacity` (žádný layout thrashing).
- Obrázky `loading="lazy"` + `width`/`height` proti CLS; hero má `fetchpriority="high"`.
- Ikony jsou inline SVG — žádná ikonová knihovna, žádný extra request.
- Fonty přes `preconnect` + `display=swap`.

**Přístupnost**
- Kontrast textu ≥ 4,5:1 na světlých i tmavých sekcích (většina AAA).
- `prefers-reduced-motion` vypíná parallax, houpání, ticker, vlny i panorama
  (trasa se přepne na statickou vertikální timeline).
- Focus ring viditelný všude, skip-link, focus trap v mobilním menu, `Esc` zavírá.
- Formulář: `<label for>` u všech polí, chyby u pole + `aria-live`, `aria-invalid`.
- **Bez JS zůstane celá stránka čitelná** — `.reveal` se aktivuje až po přidání
  třídy `.js` na `<html>`.

**Responzivita**
- Testováno na 375 / 768 / 1024 / 1440 px, bez horizontálního scrollu.
- Pod 900 px se panorama trasy nahrazuje vertikální timeline (žádný scroll-jacking
  na mobilu).

---

## Co je potřeba doplnit před ostrým nasazením

1. **Fotky.** Aktuálně jsou použité stock fotky z Unsplash načítané přes CDN
   (Praha, gastro, oslavy) jako vizuální placeholder. Nahradit reálnými fotkami
   lodí a akcí a naservírovat je lokálně jako WebP + `srcset`.
2. **Ceny.** Původní web ceny na homepage neuvádí — v návrhu proto nejsou.
   Doporučuju je doplnit, je to nejčastější důvod odchodu z rezervačního toku.
3. **Napojení formuláře.** V `assets/js/main.js` je poptávkový formulář zatím
   demo (validace + simulované odeslání). Reálný endpoint se napojí v
   `form.addEventListener('submit', …)` — hledej komentář `DEMO:`.
   Doplnit i CSRF/antispam (honeypot nebo Turnstile).
4. **Rezervační systém.** Tlačítko „Rezervovat" míří na poptávkový formulář.
   Pokud existuje rezervační engine, přesměrovat na něj.
5. **Údaje o flotile.** Tabulka lodí a kapacit v sekci Pronájem je orientační
   a založená na tom, co web uvádí („až 300 hostů" je odhad) — nechat potvrdit
   od klienta.
6. **Jazykové mutace.** CZ/EN/DE přepínač v patičce je zatím nefunkční — původní
   web mutace má.
7. **Mapa nalodění**, cookie lišta, GDPR stránka, `sitemap.xml`, analytika.

---

## Zdroje obsahu

Texty, časy odjezdů a kontakty vycházejí z aktuálního obsahu
[parnik.cz](https://www.parnik.cz/). Kontakty: `+420 604 696 969`,
`+420 773 903 903`, `info@parnik.cz`.
