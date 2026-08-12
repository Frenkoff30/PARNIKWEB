# Parník Praha, Design System (MASTER)

> Global Source of Truth. Redesign konceptu **„PLAVBA"**, kde web sám je plavba po Vltavě.
> Vygenerováno pomocí `ui-ux-pro-max` a kurátorsky upraveno (viz *Odchylky*).

---

## 1. Koncept

**„Web je loď."** Návštěvník nelistuje stránkou, *pluje*. Homepage je jedna souvislá
plavba, podrobnosti jsou na samostatných podstránkách. Na pozadí se v rytmu scrollu
posouvá panorama Prahy, dole je pořád voda, nahoře mosazná lišta můstku.

Barevná dramaturgie kopíruje denní dobu plavby:
**úsvit (hero) > den (nabídka) > noc (trasa) > bílá (rozcestník) > soumrak (rezervace)**.

---

## 2. Informační architektura

| Stránka | Obsah |
|---------|-------|
| `index.html` | Hero, nabídka plaveb (lodní lístky), trasa (panorama), rozcestník, CTA |
| `na-palube.html` | Vybavení (portholes), paluby (bento), citace |
| `pronajem.html` | Soukromé plavby, chips, flotila (tabulka), postup ve 4 krocích |
| `certifikaty.html` | Certifikát, jak to funguje |
| `galerie.html` | Fotogalerie |
| `kontakt.html` | Poptávkový formulář, kontaktní karta |

Homepage drží jen tři kapitoly příběhu (nalodění, nabídka, trasa) a předává dál.
Zbytek je na prokliky, aby web zůstal přehledný.

## 3. Pattern

| Položka | Hodnota |
|---------|---------|
| Landing pattern | **Scroll-Triggered Storytelling** (`landing.csv`) |
| CTA placement | Above the fold, mini-CTA na konci každé sekce, finální CTA band |
| Progress indicator | **Povinný**, mosazná lišta nahoře a sekční rail vpravo |
| Mobil | Bez scroll-jackingu, horizontální panorama degraduje na vertikální timeline |

## 4. Style

| Položka | Hodnota |
|---------|---------|
| Základ | **Parallax Storytelling** a **Editorial Grid / Magazine** (`styles.csv`) |
| Skin | Art-deco / Belle Époque parník: mosaz, teak, bílá, krémový papír, noční Vltava |
| Klíčové efekty | Vrstvený parallax, sticky horizontální panorama, SVG vlny, mosazný lesk, portholes, houpání paluby |

**Signature detaily**
* `.hero__deck` silueta zábradlí (mosazné madlo, teakový čepec, sloupky) v popředí hera
* `.sway` houpání 0,3 stupně za 9 s, jen na popředí hera, vypnuto při `reduced-motion`
* `.porthole` kruhová maska s mosazným prstencem
* `.rivets` nýty na mosazné liště přes `repeating-radial-gradient`
* `.waves` dvě vrstvy SVG vln plus `.waves__glint`, tenká mosazná linka driftující ve stejném rytmu jako vrstva A, tedy odlesk na hřebenu
* `[class*="cut--"]` vlnový předěl mezi sekcemi přes `mask`, barvu bere z tokenu
* `.btn--brass::after` přejezd lesku přes CTA a certifikát

## 5. Barvy

| Role | Token | Hex | Poznámka |
|------|-------|-----|----------|
| Noc | `--night` | `#08171F` | pozadí nočních sekcí |
| Trup lodi | `--hull` | `#0E2833` | karty na tmavém, patička |
| Hloubka | `--deep` | `#123A49` | přechody, vlny |
| Vltava | `--vltava` | `#1C5A67` | druhá vrstva vln |
| Mosaz | `--brass` | `#C9A227` | primární akcent **jen na tmavém** |
| Mosaz světlá | `--brass-lt` | `#EBD292` | gradienty, hover |
| Mosaz tmavá | `--brass-dk` | `#7E6412` | akcent **na světlém** (5,7:1 na bílé) |
| Bílá | `--white` | `#FFFFFF` | rozcestník, podstránkové sekce |
| Krém | `--cream` | `#F4EDE0` | nabídka plaveb, text na tmavém |
| Krém tlumený | `--cream-2` | `#D9CEBB` | sekundární text na tmavém (9,4:1) |
| Inkoust | `--ink` | `#0B1418` | text na světlém (18,6:1 na bílé) |
| Inkoust tlumený | `--ink-2` | `#42555C` | sekundární text na světlém (7,4:1) |
| Teak | `--teak` | `#7A4B2A` | dřevo zábradlí |

**CTA:** mosazný gradient `--brass-lt` do `--brass` s textem `--night`, kontrast **9,6:1**.

> Pravidlo: `--brass` je čitelná jen na tmavém pozadí. Na bílé a krémové se používá
> výhradně `--brass-dk`. Kontrast ověřen skriptem na všech textových uzlech.

## 6. Typografie

Pairing **„Classic Elegant"** (`typography.csv`): **Playfair Display** a **Inter**.

| Role | Font | Nastavení |
|------|------|-----------|
| Display, H1 až H3 | Playfair Display 600/700 | `letter-spacing: -0.02em`, `line-height: 1.06` |
| Eyebrow, štítky | Playfair Display 600 | `uppercase`, `letter-spacing: .22em` |
| Body | Inter 400 | 16 až 17 px, `line-height: 1.7`, max 68 znaků na řádek |
| Meta, časy | Inter 500 | `font-variant-numeric: tabular-nums` |

Škála fluid přes `clamp()`, H1 `clamp(2.75rem, 7.2vw, 6.5rem)`.

## 7. Prostor a mřížka

* Container `--maxw: 1240px`, gutter `clamp(1.25rem, 4vw, 3rem)`
* Vertikální rytmus sekcí `clamp(5rem, 11vh, 9rem)`
* Radius `--r-sm: 4px`, `--r: 10px`, porthole `50%`
* Z-index scale: `10` obsah, `20` sticky, `30` nav, `40` overlay, `50` menu

## 8. Pohyb

| Pravidlo | Hodnota |
|----------|---------|
| Micro-interakce | 180 až 260 ms, `cubic-bezier(.22,.61,.36,1)` |
| Reveal on scroll | 600 ms, `translateY(28px)` na 0, stagger 70 ms |
| Parallax, panorama | `IntersectionObserver` a jedna `requestAnimationFrame` smyčka, jen `transform` |
| Nekonečné animace | pouze vlny a odlesk hladiny, pomalé, dekorativní |
| `prefers-reduced-motion` | **vypíná** parallax, houpání i vlny, panorama přepne na statické |

**Panorama.** Generuje se skriptem `scripts/pano.py` (deterministicky, `seed=7`),
aby geometrie seděla. Tři hloubkové vrstvy, městská zástavba mezi dominantami,
svítící okna, nábřežní lampy a zrcadlový odraz skyline ve vodě přes `<use>` s
maskou. Výsledné SVG je inlinované v `index.html`, skript se pouští jen když se
panorama mění.

**Vlny.** Perioda tvaru je 720 (vrstva A) a 480 (vrstva B) jednotek ve `viewBox`
širokém 2880. Posun je přesně 1440, tedy celý počet period v obou vrstvách, proto
se tvar tiluje bez švu. Překlopení v patičce patří na kontejner `.waves--footer`,
ne na `<svg>`, jinak ho přepíše `transform` z animace `drift`.

## 9. Odchylky od vygenerovaného systému

| Vygenerováno | Použito | Důvod |
|--------------|---------|-------|
| Style **Liquid Glass** | Parallax Storytelling a Editorial Grid s art-deco skinem | Liquid Glass je bezčasový SaaS look, parník na Vltavě má historii a řemeslo. Glass má navíc dle `styles.csv` *Moderate-Poor* performance a problém s kontrastem. |
| Colors `#1E3A8A / #3B82F6 / #F97316` | Vlastní paleta noční Vltavy, mosaz, bílá | Bootstrap modrá s oranžovou je generická cestovka. Mosaz, teak a krém působí dráž a tematicky. |
| Typography Playfair Display SC a Karla | Playfair Display a Inter | Stejná rodina display fontu, ale Inter má lepší čitelnost v malých velikostech a tabulární číslice pro časy odjezdů. |
| Pattern Hero > Features > CTA | Scroll storytelling na homepage a samostatné podstránky | Zadání: web má být jako loď, k tomu přehlednost. |

**Anti-patterns k vyhnutí:** laciné vizuály, rychlé animace, emoji jako ikony,
scroll-jacking, auto-play video se zvukem, `--brass` jako text na světlém pozadí.

## 10. Pre-Delivery Checklist

- [x] Žádné emoji jako ikony, vše inline SVG s viewBox 24x24
- [x] `cursor: pointer` na všech klikatelných prvcích
- [x] Hover přechody 180 až 260 ms, bez layout shiftu
- [x] Kontrast ověřen na všech textových uzlech s kompozitováním průhledných vrstev
- [x] Viditelný `:focus-visible` ring, mosazný, 2 px s offsetem
- [x] `prefers-reduced-motion` respektován globálně
- [x] Responzivní 375 / 768 / 1024 / 1440 px, bez horizontálního scrollu
- [x] `alt` u všech obsahových obrázků, `aria-label` u ikonových tlačítek
- [x] `<label for>` u všech polí formuláře, chyby u pole a `aria-live`
- [x] Obrázky `loading="lazy"` a `width`/`height` proti CLS
- [x] Obsah čitelný i bez JS
