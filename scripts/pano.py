# -*- coding: utf-8 -*-
"""Generator panoramatu Prahy pro sekci Trasa. Deterministicky (seed)."""
import random, io

W, H = 5400, 780
WL = 600                      # vodni hladina
random.seed(7)

FAR   = "#0f3242"
MID   = "#0a2432"
NEAR  = "#061620"
DARK  = "#041016"
GLOW  = "#EBD292"

out = []
a = out.append


def win(x, y, w, h, op):
    return '<rect x="%g" y="%g" width="%g" height="%g" opacity="%.2f"/>' % (x, y, w, h, op)


def window_grid(x, y, cols, rows, gx, gy, w=9, h=15, chance=.62):
    """Mrizka sviticich oken."""
    s = []
    for c in range(cols):
        for r in range(rows):
            if random.random() < chance:
                s.append(win(x + c * gx, y + r * gy, w, h, random.choice([.28, .4, .55, .7])))
    return "".join(s)


def townhouses(x0, x1, base, hmin, hmax, unit=(46, 78), fill=None, windows=True):
    """Rada mestskych domu s sedlovymi strechami."""
    body, wins = [], []
    x = x0
    while x < x1:
        w = random.randint(*unit)
        if x + w > x1:
            w = x1 - x
        if w < 22:
            break
        h = random.randint(hmin, hmax)
        top = base - h
        roof = random.randint(14, 30)
        body.append('M%g %g V%g l%g %g l%g %g V%g Z' % (
            x, base, top, w / 2.0, -roof, w / 2.0, roof, base))
        # komin
        if random.random() < .45:
            cw, ch = 7, random.randint(14, 24)
            cx = x + w * random.choice([.24, .72])
            body.append('M%g %g h%g v%g h%g Z' % (cx, top - roof * .4, cw, -ch, -cw))
        if windows and w > 34 and h > 44:
            cols = max(1, int((w - 16) // 20))
            rows = max(1, int((h - 22) // 26))
            wins.append(window_grid(x + 10, top + 16, cols, rows, 20, 26, 8, 12, .5))
        x += w + random.randint(2, 9)
    g = '<path d="%s"/>' % "".join(body)
    if wins:
        g += '<g fill="%s">%s</g>' % (GLOW, "".join(wins))
    return g


# ---------------------------------------------------------------- obloha
a('<rect width="%d" height="%d" fill="url(#sky)"/>' % (W, H))

stars = []
for _ in range(150):
    sx = random.uniform(0, W)
    sy = random.uniform(20, 330)
    r = random.choice([1.4, 1.8, 2.2, 2.8])
    stars.append('<circle cx="%.0f" cy="%.0f" r="%.1f" opacity="%.2f"/>' % (
        sx, sy, r, random.uniform(.18, .6)))
a('<g fill="#EBD292">%s</g>' % "".join(stars))

# mesic
a('<g><circle cx="1180" cy="150" r="96" fill="#EBD292" opacity=".07"/>'
  '<circle cx="1180" cy="150" r="58" fill="#EBD292" opacity=".13"/>'
  '<circle cx="1180" cy="150" r="30" fill="#F6E7BE" opacity=".85"/>'
  '<circle cx="1166" cy="140" r="30" fill="url(#sky)" opacity=".55"/></g>')

# ------------------------------------------------------- vzdalene vrstvy
hills = ['M0 %d' % WL, 'V486']
x = 0
while x < W:
    step = random.randint(230, 420)
    y = random.randint(452, 512)
    hills.append('L%d %d' % (min(x + step, W), y))
    x += step
hills.append('L%d %d Z' % (W, WL))
a('<path d="%s" fill="%s" opacity=".5"/>' % (" ".join(hills), FAR))

a('<g fill="%s" opacity=".62">%s</g>' % (FAR, townhouses(0, W, 512, 34, 82, (34, 62), windows=False)))

# ------------------------------------------------------------- SKYLINE
sky = []
s = sky.append

# --- mestska zastavba mezi dominantami
s('<g fill="%s">' % MID)
for x0, x1 in [(0, 240), (800, 1040), (1830, 2170), (3060, 3180), (3620, 3780), (4160, 4460), (5080, W)]:
    s(townhouses(x0, x1, WL, 56, 128))
s('</g>')

s('<g fill="%s">' % NEAR)

# --- CECHUV MOST  (x 250..790)
s('<path fill-rule="evenodd" d="M244 502h552v98H244z'
  'M282 600a68 56 0 0 1 136 0z'
  'M452 600a68 56 0 0 1 136 0z'
  'M622 600a68 56 0 0 1 136 0z"/>')
for px in (262, 432, 602, 772):
    s('<path d="M%g 502v-64h16v64z"/>' % px)
    s('<path d="M%g 438l8-22 8 22z"/>' % px)
    s('<path d="M%g 424c-10-6-16-16-14-26 6 6 12 9 22 9s16-3 22-9c2 10-4 20-14 26z"/>' % (px - 6))
s('<g fill="%s">' % GLOW)
for px in (347, 517, 687):
    s('<circle cx="%g" cy="470" r="7" opacity=".5"/>' % px)
    s('<rect x="%g" y="470" width="4" height="32" opacity=".28"/>' % (px - 2))
s('</g>')

# --- PRAZSKY HRAD  (x 1050..1800)
s('<path d="M1010 600l110-140 690-10 90 150z"/>')
s('<path d="M1094 600V462h672v138z"/>')          # palac
s('<path d="M1086 462h688v-20h-688z"/>')          # rimsa
s('<path d="M1086 442h688v-10h-688z"/>')
# katedrala sv. Vita
s('<path d="M1296 462V330h206v132z"/>')           # hlavni lod
s('<path d="M1290 330l106-46 106 46z"/>')         # strecha
s('<path d="M1394 284v-30h8v30z"/>')
# zapadni veze
for tx in (1300, 1452):
    s('<path d="M%g 336V210h50v126z"/>' % tx)
    s('<path d="M%g 210l25-84 25 84z"/>' % tx)
    s('<path d="M%g 126v-26h6v26z"/>' % (tx + 22))
# velka jizni vez
s('<path d="M1530 462V254h62v208z"/>')
s('<path d="M1524 254l37-52 37 52z"/>')
s('<path d="M1552 202v-16h18v16z"/><path d="M1557 186l4-22 4 22z"/>')
# opery
for bx in range(1112, 1290, 42):
    s('<path d="M%g 462v-54h9v54z"/>' % bx)
s('<g fill="%s">' % GLOW)
s('<circle cx="1399" cy="386" r="21" opacity=".3"/>')
s('<circle cx="1399" cy="386" r="13" opacity=".45"/>')
s(window_grid(1120, 488, 12, 3, 42, 34, 12, 20, .7))
s(window_grid(1600, 488, 4, 3, 42, 34, 12, 20, .7))
s('<path d="M1318 372h14v34a7 7 0 0 0-14 0z" opacity=".38"/>')
s('<path d="M1470 372h14v34a7 7 0 0 0-14 0z" opacity=".38"/>')
s('</g>')

# --- PETRINSKA ROZHLEDNA (x 1900)
s('<path d="M1840 600l150-128 160 128z"/>')
s('<path d="M2040 474l-9-118h-24l-9 118h10l7-110h8l7 110z"/>')
s('<path d="M2004 356h48v-20h-48z"/>')
s('<path d="M2018 336v-22h20v22z"/><path d="M2024 314l4-20 4 20z"/>')
s('<path d="M2000 410h56v6h-56z"/><path d="M2006 442h44v6h-44z"/>')

# --- KARLUV MOST (x 2260..3020)
s('<path fill-rule="evenodd" d="M2250 494h790v106h-790z'
  'M2300 600a52 64 0 0 1 104 0z'
  'M2424 600a52 64 0 0 1 104 0z'
  'M2548 600a52 64 0 0 1 104 0z'
  'M2672 600a52 64 0 0 1 104 0z'
  'M2796 600a52 64 0 0 1 104 0z'
  'M2920 600a52 64 0 0 1 104 0z"/>')
# Staromestska mostecka vez
s('<path d="M2256 494V286h84v208z"/>')
s('<path d="M2248 286l50-74 50 74z"/>')
s('<path d="M2244 292h12v-30l6-14 6 14v30h12z"/>')
s('<path d="M2336 292h12v-30l6-14 6 14v30h12z"/>')
s('<path d="M2292 212v-34h12v34z"/>')
s('<path d="M2286 494v-72a12 12 0 0 1 24 0v72z" fill="%s"/>' % DARK)
# Malostranske veze
s('<path d="M2952 494V300h70v194z"/>')
s('<path d="M2944 300l43-62 43 62z"/>')
s('<path d="M2940 306h10v-26l5-12 5 12v26h10z"/>')
s('<path d="M3016 306h10v-26l5-12 5 12v26h10z"/>')
s('<path d="M3034 494V368h52v126z"/>')
s('<path d="M3028 368l32-44 32 44z"/>')
s('<path d="M3022 494v-44a30 26 0 0 1 60 0v44z"/>')
s('<path d="M3038 494v-30a14 12 0 0 1 28 0v30z" fill="%s"/>' % DARK)
# sochy na zabradli
for sx in range(2372, 2940, 62):
    s('<path d="M%g 494v-24a6 6 0 0 1 12 0v24z"/>' % sx)
s('<g fill="%s">' % GLOW)
s('<path d="M2288 330h16v26h-16z" opacity=".35"/>')
s('<path d="M2978 344h16v24h-16z" opacity=".35"/>')
for lx in range(2340, 2960, 124):
    s('<circle cx="%g" cy="480" r="5" opacity=".45"/>' % lx)
s('</g>')

# --- NARODNI DIVADLO (x 3220..3600)
s('<path d="M3220 600V418h370v182z"/>')
s('<path d="M3252 418v-40h306v40z"/>')
s('<path d="M3246 378l58-34h202l58 34z"/>')
s('<path d="M3228 418v-46h44v46z"/><path d="M3538 418v-46h44v46z"/>')
# kvadrigy
for qx in (3232, 3542):
    s('<path d="M%g 372c6-14 14-18 22-18 6 0 10 4 14 4s6-6 4-12c8 4 12 12 8 22z"/>' % qx)
s('<g fill="%s">' % GLOW)
for wx in range(3244, 3570, 34):
    s('<path d="M%g 452h18v42a9 9 0 0 0-18 0z" opacity="%.2f"/>' % (wx, random.choice([.3, .45, .6])))
s('</g>')

# --- TANCICI DUM (x 3820..4110)
s('<path d="M3946 600V398h150v202z"/>')
s('<path d="M3938 398h166v-18h-166z"/>')
s('<path d="M3846 600c8-96 56-128 46-192-6-42 22-64 58-58v250z"/>')
s('<ellipse cx="4020" cy="372" rx="58" ry="14"/>')
s('<path d="M4012 372v-26h16v26z"/>')
s('<g fill="%s">' % GLOW)
for r in range(6):
    for c in range(4):
        s('<rect x="%g" y="%g" width="14" height="10" opacity="%.2f"/>' % (
            3958 + c * 34, 418 + r * 30, random.choice([.22, .34, .5])))
for r in range(5):
    s('<rect x="%g" y="%g" width="12" height="9" opacity=".26"/>' % (3878 + r * 3, 446 + r * 30))
s('</g>')

# --- VYSEHRAD (x 4520..5100)
s('<path d="M4470 600l170-158 400-14 130 172z"/>')
s('<path d="M4640 442h396v-16h-396z"/>')
s('<path d="M4700 426V352h250v74z"/>')            # bazilika lod
s('<path d="M4694 352l131-40 131 40z"/>')
for tx in (4744, 4872):
    s('<path d="M%g 356V246h40v110z"/>' % tx)
    s('<path d="M%g 246l20-102 20 102z"/>' % tx)
    s('<path d="M%g 144v-22h4v22z"/>' % (tx + 18))
# hradby
for bx in range(4660, 5030, 34):
    s('<path d="M%g 426v-20h18v20z"/>' % bx)
s('<g fill="%s">' % GLOW)
s('<circle cx="4825" cy="392" r="15" opacity=".32"/>')
s('<path d="M4756 288h14v22h-14z" opacity=".3"/>')
s('<path d="M4884 288h14v22h-14z" opacity=".3"/>')
s(window_grid(4720, 372, 5, 1, 44, 30, 12, 22, .8))
s('</g>')

s('</g>')  # /NEAR

skyline = "".join(sky)

# ------------------------------------------------------------- vystup
a('<g id="skyline">%s</g>' % skyline)

# odraz ve vode
a('<use href="#skyline" transform="translate(0 1200) scale(1 -1)" '
  'opacity=".22" mask="url(#reflFade)"/>')

# nabrezni zed a lampy
a('<path d="M0 %d h%d v22H0z" fill="%s"/>' % (WL - 22, W, DARK))
lamps = []
for lx in range(70, W, 176):
    lamps.append('<rect x="%g" y="%g" width="5" height="30" opacity=".35"/>' % (lx, WL - 52))
    lamps.append('<circle cx="%g" cy="%g" r="6" opacity=".55"/>' % (lx + 2.5, WL - 56))
    lamps.append('<circle cx="%g" cy="%g" r="16" opacity=".12"/>' % (lx + 2.5, WL - 56))
a('<g fill="%s">%s</g>' % (GLOW, "".join(lamps)))

# voda
a('<rect y="%d" width="%d" height="%d" fill="url(#water)"/>' % (WL, W, H - WL))
shim = []
for i in range(70):
    sx = random.uniform(0, W)
    sy = random.uniform(WL + 12, H - 14)
    lw = random.uniform(30, 150)
    shim.append('<rect x="%.0f" y="%.0f" width="%.0f" height="2" opacity="%.2f"/>' % (
        sx, sy, lw, random.uniform(.04, .16)))
a('<g fill="#EBD292">%s</g>' % "".join(shim))

defs = (
  '<defs>'
  '<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
  '<stop offset="0%%" stop-color="#061725"/>'
  '<stop offset="46%%" stop-color="#0e3346"/>'
  '<stop offset="82%%" stop-color="#1d5567"/>'
  '<stop offset="100%%" stop-color="#2c7183"/></linearGradient>'
  '<linearGradient id="water" x1="0" y1="0" x2="0" y2="1">'
  '<stop offset="0%%" stop-color="#07202c"/>'
  '<stop offset="100%%" stop-color="#04121a"/></linearGradient>'
  '<linearGradient id="reflGrad" x1="0" y1="%d" x2="0" y2="%d" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#fff" stop-opacity=".55"/>'
  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
  '<mask id="reflFade"><rect y="%d" width="%d" height="%d" fill="url(#reflGrad)"/></mask>'
  '</defs>' % (WL, H, WL, W, H - WL)
)

svg = ('<svg class="pano" viewBox="0 0 %d %d" preserveAspectRatio="xMinYMax slice" aria-hidden="true">'
       % (W, H)) + defs + "".join(out) + '</svg>'

io.open('pano.svg', 'w', encoding='utf-8').write(svg)
print('OK, delka:', len(svg))
