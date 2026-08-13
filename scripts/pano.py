# -*- coding: utf-8 -*-
"""
Generator panoramatu Prahy pro sekci Trasa. Deterministicky (seed).

Pet vrstev, kazda se pri scrollu posouva svym data-depth. Odtud hloubka.

  sky   0.10  obloha, hvezdy, mesic, opar, zakladni hladina
  far   0.32  protejsi breh, mekky a svetly, bez detailu
  mid   0.58  stredni pasmo zastavby
  near  1.00  teren, dominanty, nabrezi, stromy, lode a odraz ve vode
  foam  1.06  trpytky na hladine

Terén a dominanty musi zustat v jedne vrstve, jinak by hrad odplul ze sveho
kopce. Vzdalene vrstvy proto stoji na rovine, jde o protejsi breh.

Pravidlo: nic nelevituje. Kazda stavba se kresli od strechy az na hladinu,
komin patri vzdy na hlavni telo domu.

Spusteni prepise vrstvy uvnitr <div class="route__stage"> v index.html.
"""
import random, io, os, re, sys

W, H = 5200, 780
WL = 600
random.seed(31)

HAZE = "#2b6076"
FAR  = "#22566a"
MID  = "#143a4a"
NEAR = "#0a212c"
DARK = "#061620"
GLOW = "#F0D9A0"

TERRAIN = [
    (0, WL), (880, WL),
    (1040, 472), (1780, 472), (1880, WL),
    (4380, WL), (4520, 462), (4940, 462), (5060, WL),
    (W, WL),
]


def terrain(x):
    for i in range(len(TERRAIN) - 1):
        x0, y0 = TERRAIN[i]
        x1, y1 = TERRAIN[i + 1]
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / float(x1 - x0)
    return WL


def lit(x, y, cols, rows, gx, gy, w=5, h=8, chance=.42):
    s = []
    for c in range(cols):
        for r in range(rows):
            if random.random() < chance:
                s.append('<rect x="%g" y="%g" width="%g" height="%g" opacity="%.2f"/>'
                         % (x + c * gx, y + r * gy, w, h,
                            random.choice([.18, .28, .4, .52])))
    return "".join(s)


def onion(cx, ty, tw):
    """Barokni cibulova bane. Charakteristicky prazsky tvar."""
    hw = tw / 2.0
    return ('M%g %g C%g %g %g %g %g %g C%g %g %g %g %g %g Z'
            % (cx - hw, ty,
               cx - hw * 1.5, ty - tw * .5, cx - hw * .75, ty - tw * 1.05, cx, ty - tw * 1.15,
               cx + hw * .75, ty - tw * 1.05, cx + hw * 1.5, ty - tw * .5, cx + hw, ty)
            + 'M%g %g h%g v%g h%g Z' % (cx - hw * .32, ty - tw * 1.12, hw * .64, -tw * .3, -hw * .64)
            + 'M%g %g l%g %g l%g %g Z' % (cx - hw * .3, ty - tw * 1.42, hw * .3, -tw * .34, hw * .3, tw * .34)
            + 'M%g %g v%g h3v%g Z' % (cx - 1.5, ty - tw * 1.76, -tw * .22, tw * .22))


def spire(cx, ty, tw, h):
    """Stihla goticka spice."""
    hw = tw / 2.0
    return 'M%g %g l%g %g l%g %g Z' % (cx - hw, ty, hw, -h, hw, h)


def quadriga(px, py):
    """Vuz se spreženim na pylonu. Vsechny dily se prekryvaji, aby drzely
    pohromade, a vinou se stejnym smerem jako zbytek siluety."""
    return ('M%g %g v-12 h11 v12 Z' % (px, py)                       # vuz
            + 'M%g %g v-10 l4 -6 h13 l4 6 v10 Z' % (px + 9, py)      # telo spreženi
            + 'M%g %g l3 -9 l4 1 l-3 8 Z' % (px + 15, py - 13)       # krk a hlava
            + 'M%g %g l3 -9 l4 1 l-3 8 Z' % (px + 21, py - 13)
            + 'M%g %g v-8 l3 -4 l4 4 v8 Z' % (px + 2, py - 9))       # vozataj


def roofline(x0, x1, hmin, hmax, unit, detail=2, flat=False):
    """
    Rada domu. detail 0 = jen obrysy, 1 = strechy a vikyre, 2 = plus okna.
    Kazdy dum sahá az na WL, takze nemuze levitovat.
    """
    body, wins = [], []
    x = x0
    while x < x1:
        w = random.randint(*unit)
        if x + w > x1:
            w = x1 - x
        if w < 16:
            break
        base = WL if flat else terrain(x + w / 2.0)
        top = base - random.randint(hmin, hmax)
        cx = x + w / 2.0
        r = random.random()
        spots = [.2, .76]

        if r < .40:                                   # sedlova strecha
            roof = random.randint(9, 17)
            body.append('M%g %g V%g l%g %g l%g %g V%g Z'
                        % (x, WL, top, w / 2.0, -roof, w / 2.0, roof, WL))
            chim = top - roof * .28
            spots = [.32, .68]
            if detail >= 1 and w > 30 and random.random() < .5:      # vikyr
                dw = 7
                dx = cx - dw / 2.0
                body.append('M%g %g v-7h%g v7 Z' % (dx, top - roof * .35, dw))
                body.append('M%g %g l%g -6 l%g 6 Z'
                            % (dx - 1, top - roof * .35 - 7, dw / 2.0 + 1, dw / 2.0 + 1))

        elif r < .58:                                 # mansarda
            b1 = random.randint(10, 16)
            b2 = random.randint(7, 12)
            body.append('M%g %g V%g l%g %g l%g %g l%g %g l%g %g V%g Z'
                        % (x, WL, top, w * .18, -b1, w * .32, -b2,
                           w * .32, b2, w * .18, b1, WL))
            chim = top - b1 * .5

        elif r < .74:                                 # plocha s rimsou
            body.append('M%g %g V%g h%g V%g Z' % (x, WL, top, w, WL))
            body.append('M%g %g h%g v5 h%g Z' % (x - 2, top - 5, w + 4, -(w + 4)))
            chim = top + 2

        elif r < .89:                                 # barokni vez s bani
            body.append('M%g %g V%g h%g V%g Z' % (x, WL, top, w, WL))
            tw = max(11, w * .34)
            body.append('M%g %g v%g h%g v%g Z' % (cx - tw / 2.0, top, -26, tw, 26))
            body.append(onion(cx, top - 26, tw))
            chim = top + 2
            spots = [.08, .88]

        else:                                         # goticka vez
            body.append('M%g %g V%g h%g V%g Z' % (x, WL, top, w, WL))
            tw = max(10, w * .3)
            body.append('M%g %g v%g h%g v%g Z' % (cx - tw / 2.0, top, -30, tw, 30))
            body.append(spire(cx, top - 30, tw, tw * 2.1))
            chim = top + 2
            spots = [.08, .88]

        if random.random() < .28:
            cw = 4
            # komin musi lezet celou sirkou nad telem domu, jinak visi pres okraj
            cxx = min(max(x + w * random.choice(spots), x + 2), x + w - cw - 2)
            ch = random.randint(9, 16)
            body.append('M%g %g v%g h%g v%g Z' % (cxx, chim, -ch, cw, ch))

        if detail >= 2 and w > 26 and base - top > 40:
            cols = max(1, int((w - 10) // 13))
            rows = max(1, int((base - top - 20) // 19))
            wins.append(lit(x + 6, top + 14, cols, rows, 13, 19, 4, 6, .32))

        x += w + random.randint(1, 5)

    g = '<path d="%s"/>' % "".join(body)
    if wins:
        g += '<g fill="%s">%s</g>' % (GLOW, "".join(wins))
    return g


def ground(offset=0):
    p = ["M0 %d" % WL]
    for x, y in TERRAIN:
        p.append("L%g %g" % (x, max(0, y - offset)))
    p.append("L%d %d Z" % (W, WL))
    return " ".join(p)


def trees(x0, x1, step=(46, 78)):
    """Stromoradi na nabrezi. Koruna z prekryvajicich se kruhu."""
    s = []
    x = x0
    while x < x1:
        h = random.randint(26, 44)
        ty = WL - 12 - h
        ty0 = ty + h * .55
        s.append('<rect x="%g" y="%g" width="3" height="%g"/>' % (x - 1.5, ty0, WL - ty0))
        for dx, dy, rr in ((0, 0, h * .42), (-h * .26, h * .14, h * .3),
                           (h * .26, h * .12, h * .32), (0, h * .3, h * .3)):
            s.append('<circle cx="%g" cy="%g" r="%g"/>' % (x + dx, ty + dy, rr))
        x += random.randint(*step)
    return "".join(s)


def moored(x, scale=1.0):
    """Zakotvena lodka u brehu."""
    return ('<g transform="translate(%g %g) scale(%g)">' % (x, WL - 6, scale) +
            '<path d="M0 0h58l-7 12H7z"/>'
            '<rect x="12" y="-9" width="34" height="9" rx="1"/>'
            '<rect x="26" y="-20" width="3" height="11"/>'
            '</g>')


# ================================================================= 1. obloha
sky = ['<defs>'
       '<linearGradient id="pSky" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0%" stop-color="#0d2433"/><stop offset="52%" stop-color="#194256"/>'
       '<stop offset="100%" stop-color="#2d6a80"/></linearGradient>'
       '<linearGradient id="pHaze" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0%" stop-color="' + HAZE + '" stop-opacity="0"/>'
       '<stop offset="100%" stop-color="' + HAZE + '" stop-opacity=".55"/></linearGradient>'
       '<linearGradient id="pWater" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0%" stop-color="#0b2a38"/><stop offset="100%" stop-color="#061a24"/></linearGradient>'
       '</defs>']
sky.append('<rect width="%d" height="%d" fill="url(#pSky)"/>' % (W, WL))
st = []
for _ in range(120):
    st.append('<circle cx="%.0f" cy="%.0f" r="%.1f" opacity="%.2f"/>'
              % (random.uniform(0, W), random.uniform(14, 300),
                 random.choice([1.2, 1.6, 2.0]), random.uniform(.12, .4)))
sky.append('<g fill="%s">%s</g>' % (GLOW, "".join(st)))
sky.append('<g><circle cx="1180" cy="136" r="78" fill="%s" opacity=".05"/>'
           '<circle cx="1180" cy="136" r="43" fill="%s" opacity=".1"/>'
           '<circle cx="1180" cy="136" r="24" fill="#F8EDD2" opacity=".78"/>'
           '<circle cx="1169" cy="128" r="24" fill="url(#pSky)" opacity=".5"/></g>' % (GLOW, GLOW))
sky.append('<rect y="420" width="%d" height="180" fill="url(#pHaze)"/>' % W)
sky.append('<rect y="%d" width="%d" height="%d" fill="url(#pWater)"/>' % (WL, W, H - WL))

# ================================================================== 2. dalka
far = ['<g fill="%s" opacity=".26">%s</g>'
       % (HAZE, roofline(0, W, 16, 48, (18, 32), detail=0, flat=True))]
far.append('<g fill="%s" opacity=".38">%s</g>'
           % (FAR, roofline(0, W, 22, 62, (20, 36), detail=1, flat=True)))

# ================================================================== 3. stred
mid = ['<g fill="%s" opacity=".7">%s</g>'
       % (MID, roofline(0, W, 30, 80, (22, 42), detail=1, flat=True))]

# ================================================================= 4. blizko
near = []
n = near.append
n('<defs><linearGradient id="pRefl" x1="0" y1="%d" x2="0" y2="%d" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#fff" stop-opacity=".45"/>'
  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
  '<mask id="pReflFade"><rect y="%d" width="%d" height="%d" fill="url(#pRefl)"/></mask></defs>'
  % (WL, H, WL, W, H - WL))

sk = []
s = sk.append
s('<path d="%s" fill="%s" opacity=".5"/>' % (ground(0), FAR))
s('<g fill="%s">' % MID)
for x0, x1 in [(0, 230), (800, 1035), (1900, 2130), (2940, 3095),
               (3500, 3700), (4020, 4370), (5090, W)]:
    s(roofline(x0, x1, 44, 106, (26, 46)))
s('</g>')

s('<g fill="%s">' % NEAR)

# --- Cechuv most
s('<path fill-rule="evenodd" d="M236 512h528v88H236z'
  'M268 600a58 48 0 0 1 116 0z'
  'M424 600a58 48 0 0 1 116 0z'
  'M580 600a58 48 0 0 1 116 0z"/>')
for px in (246, 402, 558, 726):
    s('<path d="M%g 512v-46h12v46z"/>' % px)
    s('<path d="M%g 466l6-14 6 14z"/>' % px)

# --- Prazsky hrad a katedrala sv. Vita
s('<path d="M1064 %d V472h664v%d z"/>' % (WL, WL - 472))
s('<path d="M1056 472h680v-14h-680z"/>')
s('<path d="M1056 458h680v-7h-680z"/>')
for bx in range(1076, 1276, 34):
    s('<path d="M%g 472v-42h8l3-8v50z"/>' % bx)
for bx in range(1560, 1730, 34):
    s('<path d="M%g 472v-42h8l3-8v50z"/>' % bx)
s('<path d="M1288 %d V344h186v%d z"/>' % (WL, WL - 344))
s('<path d="M1282 344l93-40 93 40z"/>')
s('<path d="M1370 304v-26h9v26z"/>')
for tx in (1294, 1430):
    s('<path d="M%g %d V232h44v%d z"/>' % (tx, WL, WL - 232))
    s('<path d="M%g 232h-5l27-88 27 88h-5z"/>' % tx)
s('<path d="M1500 %d V286h58v%d z"/>' % (WL, WL - 286))
s('<path d="M1494 286h70v-12h-70z"/>')
s('<path d="%s"/>' % onion(1529, 274, 46))
s('<circle cx="1381" cy="392" r="17" fill="%s"/>' % DARK)
s('<circle cx="1381" cy="392" r="12" fill="%s" opacity=".3"/>' % GLOW)

# --- Karluv most
arches = []
for i in range(12):
    arches.append('M%g 600a25 34 0 0 1 50 0z' % (2166 + i * 62))
s('<path fill-rule="evenodd" d="M2146 508h772v92h-772z%s"/>' % "".join(arches))
s('<path d="M2140 508h784v-9h-784z"/>')
s('<path d="M2150 499V318h76v181z"/>')
s('<path d="M2144 318l44-66 44 66z"/>')
for cx0 in (2144, 2220):
    s('<path d="M%g 324h11v-30l5-11 5 11v30h11z"/>' % cx0)
s('<path d="M2183 252v-30h10v30z"/>')
s('<path d="M2176 499v-64a12 12 0 0 1 24 0v64z" fill="%s"/>' % DARK)
s('<path d="M2842 499V334h62v165z"/>')
s('<path d="M2836 334l37-54 37 54z"/>')
s('<path d="M2902 499V392h50v107z"/>')
s('<path d="M2896 392l31-40 31 40z"/>')
s('<path d="M2894 499v-36a26 22 0 0 1 52 0v36z"/>')
s('<path d="M2906 499v-25a12 10 0 0 1 24 0v25z" fill="%s"/>' % DARK)
for sx in range(2252, 2830, 41):
    s('<path d="M%g 499v-17a4.5 4.5 0 0 1 9 0v17z"/>' % sx)

# --- Narodni divadlo
s('<path d="M3126 %d V434h344v%d z"/>' % (WL, WL - 434))
s('<path d="M3156 434v-30h284v30z"/>')
s('<path d="M3150 404c58-30 238-30 296 0z"/>')
s('<path d="M3132 434v-40h40v40z"/><path d="M3424 434v-40h40v40z"/>')
for qx in (3130, 3434):
    s('<path d="%s"/>' % quadriga(qx, 394))
for ax in range(3180, 3418, 30):
    s('<path d="M%g %d v-88a10 10 0 0 1 20 0v88z" fill="%s"/>' % (ax, WL, MID))

# --- Tancici dum
s('<path d="M3756 %d V416h128v%d z"/>' % (WL, WL - 416))
s('<path d="M3748 403h144v13h-144z"/>')
s('<path d="M3664 %d C3668 546 3694 516 3702 486 C3708 462 3696 446 3702 430 '
  'C3710 412 3732 404 3758 404 V%d Z"/>' % (WL, WL))
s('<path d="M3800 403a42 27 0 0 1 84 0z"/>')
s('<path d="M3838 379v-16h8v16z"/>')

# --- Vysehrad
s('<path d="M4526 %d V462h408v%d z"/>' % (WL, WL - 462))
s('<path d="M4518 462h424v-12h-424z"/>')
s('<path d="M4602 %d V378h220v%d z"/>' % (WL, WL - 378))
s('<path d="M4596 378l116-32 116 32z"/>')
for tx in (4634, 4766):
    s('<path d="M%g %d V282h30v%d z"/>' % (tx, WL, WL - 282))
    s('<path d="M%g 282h-4l19-92 19 92h-4z"/>' % tx)
for bx in range(4540, 4930, 28):
    s('<path d="M%g 450v-13h14v13z"/>' % bx)

# --- nabrezi: stromy a zakotvene lode
for a0, a1, stp in ((60, 830, (54, 92)), (1960, 2120, (52, 84)), (3000, 3110, (50, 80)),
                    (4050, 4360, (54, 90)), (5090, W, (54, 90))):
    s('<g opacity=".92">%s</g>' % trees(a0, a1, stp))
for bx, k in ((870, 1.0), (1990, .85), (3010, .95), (4420, 1.05), (5010, .8)):
    s(moored(bx, k))
s('</g>')

# --- svetla
s('<g fill="%s">' % GLOW)
s(lit(1084, 496, 14, 2, 38, 30, 6, 10, .48))
s(lit(1566, 496, 4, 2, 38, 30, 6, 10, .48))
s('<rect x="2168" y="360" width="9" height="14" opacity=".26"/>')
s('<rect x="2862" y="372" width="9" height="13" opacity=".26"/>')
for wx in range(3162, 3440, 30):
    s('<path d="M%g 464h12v28a6 6 0 0 0-12 0z" opacity="%.2f"/>'
      % (wx, random.choice([.2, .3, .42])))
for r in range(5):
    for c in range(4):
        s('<rect x="%g" y="%g" width="9" height="7" opacity="%.2f"/>'
          % (3770 + c * 29, 434 + r * 27, random.choice([.16, .26, .36])))
s(lit(4620, 394, 5, 1, 40, 26, 8, 14, .7))
s('</g>')

skyline = "".join(sk)
n('<g id="skyline">%s</g>' % skyline)
n('<use href="#skyline" transform="translate(0 1200) scale(1 -1)" opacity=".15" mask="url(#pReflFade)"/>')

lamps = []
for lx in range(110, W, 230):
    lamps.append('<rect x="%g" y="%g" width="2.5" height="20" opacity=".2"/>' % (lx, WL - 30))
    lamps.append('<circle cx="%g" cy="%g" r="2.4" opacity=".4"/>' % (lx + 1.25, WL - 30))
    lamps.append('<circle cx="%g" cy="%g" r="6.5" opacity=".06"/>' % (lx + 1.25, WL - 30))
n('<g fill="%s">%s</g>' % (GLOW, "".join(lamps)))
n('<rect y="%d" width="%d" height="10" fill="%s"/>' % (WL - 10, W, DARK))

# ================================================================ 5. trpytky
FOAM_W = int(W * 1.12)
foam = []
sh = []
for _ in range(80):
    sh.append('<rect x="%.0f" y="%.0f" width="%.0f" height="1.5" rx=".75" opacity="%.2f"/>'
              % (random.uniform(0, FOAM_W), random.uniform(WL + 14, H - 16),
                 random.uniform(24, 120), random.uniform(.05, .16)))
foam.append('<g fill="%s">%s</g>' % (GLOW, "".join(sh)))

LAYERS = [("0.10", sky, W), ("0.32", far, W), ("0.58", mid, W),
          ("1", near, W), ("1.06", foam, FOAM_W)]

html = "".join(
    '<div class="pano" data-depth="%s"><svg viewBox="0 0 %d %d" preserveAspectRatio="xMinYMid meet" '
    'aria-hidden="true">%s</svg></div>' % (d, w, H, "".join(parts))
    for d, parts, w in LAYERS)

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    target = os.path.join(root, "index.html")
    t = io.open(target, encoding="utf-8").read()
    t, k = re.subn(r'(<div class="route__stage">\s*).*?(\s*<div class="route__boat")',
                   lambda m: m.group(1) + html + m.group(2), t, flags=re.S)
    if not k:
        sys.exit("kotva route__stage / route__boat nenalezena")
    io.open(target, "w", encoding="utf-8", newline="").write(t)
    print("vrstev:", len(LAYERS), "| delka html:", len(html))
