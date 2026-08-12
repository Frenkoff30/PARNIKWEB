# Parník Praha — Design System (MASTER)

> Global Source of Truth. Redesign konceptu **„PLAVBA"** — web sám je plavba po Vltavě.
> Vygenerováno pomocí `ui-ux-pro-max` a kurátorsky upraveno (viz *Odchylky*).

---

## 1. Koncept

**„Web je loď."** Návštěvník nelistuje stránkou — *pluje*. Stránka je jedna souvislá
plavba od nalodění po návrat, rozdělená na kapitoly (I–VII). Na pozadí se v rytmu
scrollu posouvá panorama Prahy, dole je pořád voda, nahoře mosazná lišta můstku.

Barevná dramaturgie kopíruje denní dobu plavby:
**úsvit (I) → den (II–III) → soumrak (IV–V) → noc (VI–VII)**.

---

## 2. Pattern

| Položka | Hodnota |
|---|---|
| Landing pattern | **Scroll-Triggered Storytelling** (`landing.csv`) |
| Pořadí sekcí | Hero → Ticker → Nabídka → Trasa → Na palubě → Pronájem → Certifikát → Galerie → Poptávka |
| CTA placement | Above the fold + mini-CTA na konci každé kapitoly + finální climax CTA (formulář) |
| Progress indicator | **Povinný** — mosazná lišta nahoře + kapitolový rail vpravo |
| Mobil | Bez scroll-jackingu; horizontální panorama degraduje na vertikální timeline |

## 3. Style

| Položka | Hodnota |
|---|---|
| Základ | **Parallax Storytelling** + **Editorial Grid / Magazine** (`styles.csv`) |
| Skin | Art-deco / Belle Époque parník — mosaz, teak, krémový papír, noční Vltava |
| Klíčové efekty | Vrstvený parallax (3 vrstvy), sticky horizontální panorama, SVG vlny, mosazný lesk, portholes, jemné houpání paluby |
| Complexity | High |

**Signature detaily**
- `.deck` — silueta zábradlí a přídě v popředí hera (dojem „stojím na palubě")
- `.sway` — houpání ±0.35° / 9 s, jen na popředí hera, vypnuto při `reduced-motion`
- `.porthole` — kruhová maska s mosazným prstencem a nýty
- `.rivets` — `repeating-radial-gradient` nýtů na mosazných lištách
- `.waves` — 3 vrstvy SVG vln s rozdílnou rychlostí
- `.brass-shine` — přejezd lesku přes CTA a certifikát

## 4. Barvy

| Role | Token | Hex | Poznámka |
|---|---|---|---|
| Noc / hlavní tmavá | `--night` | `#08171F` | pozadí nočních kapitol |
| Trup lodi | `--hull` | `#0E2833` | karty na tmavém |
| Hloubka | `--deep` | `#123A49` | přechody, hairlines |
| Vltava | `--vltava` | `#1C5A67` | voda, sekundární |
| Mosaz | `--brass` | `#C9A227` | primární akcent |
| Mosaz světlá | `--brass-lt` | `#EBD292` | gradienty, hover |
| Mosaz tmavá | `--brass-dk` | `#7E6412` | stíny, borders na světlém |
| Krém / papír | `--cream` | `#F4EDE0` | světlé pozadí, text na tmavém |
| Krém tlumený | `--cream-2` | `#D9CEBB` | sekundární text na tmavém (9.4:1) |
| Inkoust | `--ink` | `#0B1418` | text na světlém (16:1) |
| Inkoust tlumený | `--ink-2` | `#42555C` | sekundární text na světlém (7.2:1) |
| Teak | `--teak` | `#7A4B2A` | dřevo, footer |

**CTA:** mosazný gradient `--brass-lt → --brass` s textem `--night` → kontrast **9.6:1**.

> Kontrast ověřen pro všechny páry text/pozadí na min. **4.5:1** (WCAG AA), většina AAA.

## 5. Typografie

Pairing **„Classic Elegant"** (`typography.csv`): **Playfair Display** + **Inter**.

| Role | Font | Nastavení |
|---|---|---|
| Display / H1–H3 | Playfair Display 600/700 | `letter-spacing: -0.02em`, `line-height: 1.05` |
| Eyebrow / štítky | Playfair Display 600 | `uppercase`, `letter-spacing: .22em` |
| Body | Inter 400 | `16–18px`, `line-height: 1.7`, max `68ch` |
| Meta / časy | Inter 500 | `font-variant-numeric: tabular-nums` |

Škála: `clamp()` fluid — H1 `clamp(2.75rem, 7vw, 6.5rem)`.

## 6. Prostor & mřížka

- Container `--maxw: 1240px`, gutter `clamp(1.25rem, 4vw, 3rem)`
- Vertikální rytmus sekcí: `clamp(5rem, 11vh, 9rem)`
- Spacing scale: `4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 / 144 px`
- Radius: `--r-sm: 4px`, `--r: 10px`, `--r-lg: 20px`, porthole `50%`
- Z-index scale: `10` obsah · `20` sticky · `30` nav · `40` overlay · `50` menu

## 7. Pohyb

| Pravidlo | Hodnota |
|---|---|
| Micro-interakce | 180–260 ms, `cubic-bezier(.22,.61,.36,1)` (ease-out) |
| Reveal on scroll | 600 ms, `translateY(28px) → 0`, stagger 70 ms |
| Parallax / panorama | řízeno `IntersectionObserver` + `requestAnimationFrame`, jen `transform` |
| Nekonečné animace | pouze vlny a ticker (dekorativní, pomalé, `will-change: transform`) |
| `prefers-reduced-motion` | **vypíná** parallax, houpání, ticker i vlny; panorama přepne na statické |

## 8. Odchylky od vygenerovaného systému (a proč)

| Vygenerováno | Použito | Důvod |
|---|---|---|
| Style: **Liquid Glass** | Parallax Storytelling + Editorial Grid s art-deco skinem | Liquid Glass je bezčasový SaaS look; parník na Vltavě má historii a řemeslo. Glass má navíc dle `styles.csv` *Moderate-Poor* performance a problém s kontrastem. |
| Colors: `#1E3A8A / #3B82F6 / #F97316` (sky blue + booking orange) | Vlastní paleta noční Vltavy + mosaz | Bootstrap-modrá + oranžová = generická cestovka. Mosaz/teak/krém je tematické a dražší na pohled. Kontrast zůstává ≥ AA. |
| Typography: Playfair Display SC + Karla | Playfair Display + Inter | Stejná rodina display fontu, ale Inter má lepší čitelnost v malých velikostech a tabulární číslice pro časy odjezdů. |
| Pattern: Hero → Features → CTA | Scroll storytelling se 7 kapitolami | Zadání: „ať je web jako loď" → lineární narativ plavby. |

**Anti-patterns k vyhnutí** (z generovaného systému): laciné vizuály, rychlé animace.
Doplněno: žádné emoji jako ikony, žádný scroll-jacking, žádné auto-play video se zvukem.

## 9. Pre-Delivery Checklist

- [x] Žádné emoji jako ikony — vše inline SVG (Lucide-style, 24×24 viewBox)
- [x] `cursor: pointer` na všech klikatelných prvcích
- [x] Hover přechody 180–260 ms, bez layout shiftu
- [x] Kontrast textu ≥ 4.5:1 v obou režimech sekcí
- [x] Viditelný `:focus-visible` ring (mosazný, 2px + offset)
- [x] `prefers-reduced-motion` respektován globálně
- [x] Responzivní 375 / 768 / 1024 / 1440 px, bez horizontálního scrollu
- [x] `alt` u všech obsahových obrázků, `aria-label` u ikonových tlačítek
- [x] `<label for>` u všech polí formuláře, chyby u pole + `aria-live`
- [x] Obrázky `loading="lazy"` + `width`/`height` (rezervace místa)
