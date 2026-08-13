# -*- coding: utf-8 -*-
"""
Generator panoramatu Prahy pro sekci Trasa. Deterministicky (seed).

Panorama je rozdelene na pet vrstev, ktere se pri scrollu posouvaji ruznou
rychlosti (parallax). Odtud pocit hloubky a toho, ze lod skutecne pluje.

  sky   0.10  obloha, hvezdy, mesic, opar, zakladni hladina
  far   0.32  vzdalena zastavba na druhem brehu, mekka a svetla
  mid   0.58  stredni pasmo zastavby
  near  1.00  teren, dominanty, nabrezi, lampy a odraz ve vode
  foam  1.06  trpytky na hladine, nejrychlejsi

Terén a dominanty musi byt ve stejne vrstve, jinak by hrad odplul ze sveho
kopce. Vzdalene vrstvy proto stoji na rovine, jde o protejsi breh.

Pravidlo: nic nelevituje. Kazda stavba se kresli od strechy az na hladinu.

Spusteni prepise vrstvy uvnitr <div class="route__stage"> v index.html.
"""
import random, io, os, re, sys

W, H = 5200, 780
WL = 600
random.seed(23)

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


def roofline(x0, x1, hmin, hmax, unit, windows=True, flat=False):
    """Rada domu. Kazdy dum sahá az na WL, takze nemuze levitovat."""
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
        style = random.random()
        spots = [.22, .74]
        if style < .62:
            roof = random.randint(8, 16)
            body.append('M%g %g V%g l%g %g l%g %g V%g Z'
                        % (x, WL, top, w / 2.0, -roof, w / 2.0, roof, WL))
            chim = top - roof * .45
        elif style < .84:
            body.append('M%g %g V%g h%g V%g Z' % (x, WL, top, w, WL))
            body.append('M%g %g h%g v-5h%g Z' % (x - 2, top, w + 4, -(w + 4)))
            chim = top + 2
        else:
            body.append('M%g %g V%g h%g V%g Z' % (x, WL, top, w, WL))
            tw = max(8, w * .3)
            tx = x + (w - tw) / 2.0
            body.append('M%g %g v%g h%g v%g Z' % (tx, top, -22, tw, 22))
            body.append('M%g %g l%g %g l%g %g Z' % (tx, top - 22, tw / 2.0, -16, tw / 2.0, 16))
            chim = top + 2
            spots = [.11, .86]
        if random.random() < .3:
            cw = 4
            cx = x + w * random.choice(spots)
            body.append('M%g %g h%g v%g h%g Z' % (cx, chim, cw, -random.randint(9, 16), -cw))
        if windows and w > 26 and base - top > 40:
            cols = max(1, int((w - 10) // 13))
            rows = max(1, int((base - top - 20) // 19))
            wins.append(lit(x + 6, top + 14, cols, rows, 13, 19, 4, 6, .34))
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


# =============================================================== 1. obloha
sky = ['<defs>'
       '<linearGradient id="pSky" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0%" stop-color="#0d2433"/><stop offset="52%" stop-color="#194256"/>'
       '<stop offset="100%" stop-color="#2d6a80"/></linearGradient>'
       '<linearGradient id="pHaze" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0%" stop-color="' + HAZE + '" stop-opacity="0"/>'
       '<stop offset="100%" stop-color="' + HAZE + '" stop-opacity=".5"/></linearGradient>'
       '<linearGradient id="pWater" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0%" stop-color="#0b2a38"/><stop offset="100%" stop-color="#061a24"/></linearGradient>'
       '</defs>']
sky.append('<rect width="%d" height="%d" fill="url(#pSky)"/>' % (W, WL))
st = []
for _ in range(110):
    st.append('<circle cx="%.0f" cy="%.0f" r="%.1f" opacity="%.2f"/>'
              % (random.uniform(0, W), random.uniform(16, 300),
                 random.choice([1.2, 1.6, 2.0]), random.uniform(.12, .4)))
sky.append('<g fill="%s">%s</g>' % (GLOW, "".join(st)))
sky.append('<g><circle cx="1180" cy="140" r="76" fill="%s" opacity=".05"/>'
           '<circle cx="1180" cy="140" r="42" fill="%s" opacity=".1"/>'
           '<circle cx="1180" cy="140" r="24" fill="#F8EDD2" opacity=".75"/>'
           '<circle cx="1169" cy="132" r="24" fill="url(#pSky)" opacity=".5"/></g>' % (GLOW, GLOW))
sky.append('<rect y="430" width="%d" height="170" fill="url(#pHaze)"/>' % W)
sky.append('<rect y="%d" width="%d" height="%d" fill="url(#pWater)"/>' % (WL, W, H - WL))

# ============================================================= 2. dalka
far = ['<g fill="%s" opacity=".3">%s</g>' % (HAZE, roofline(0, W, 18, 54, (20, 36), windows=False, flat=True))]
far.append('<g fill="%s" opacity=".42">%s</g>' % (FAR, roofline(0, W, 24, 66, (22, 40), windows=False, flat=True)))

# ============================================================= 3. stred
mid = ['<g fill="%s" opacity=".72">%s</g>' % (MID, roofline(0, W, 32, 82, (24, 44), windows=False, flat=True))]

# ============================================================= 4. blizko
near = []
n = near.append
n('<defs><linearGradient id="pRefl" x1="0" y1="%d" x2="0" y2="%d" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#fff" stop-opacity=".45"/>'
  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
  '<mask id="pReflFade"><rect y="%d" width="%d" height="%d" fill="url(#pRefl)"/></mask></defs>'
  % (WL, H, WL, W, H - WL))

sk = []
s = sk.append
s('<path d="%s" fill="%s" opacity=".55"/>' % (ground(0), FAR))
s('<g fill="%s">' % MID)
for x0, x1 in [(0, 220), (790, 1030), (1900, 2120), (2930, 3090),
               (3490, 3690), (4010, 4360), (5080, W)]:
    s(roofline(x0, x1, 44, 104, (26, 48)))
s('</g>')

s('<g fill="%s">' % NEAR)

# Cechuv most
s('<path fill-rule="evenodd" d="M240 508h520v92H240z'
  'M276 600a62 52 0 0 1 124 0z'
  'M438 600a62 52 0 0 1 124 0z'
  'M600 600a62 52 0 0 1 124 0z"/>')
for px in (252, 414, 576, 740):
    s('<path d="M%g 508v-44h11v44z"/>' % px)
    s('<path d="M%g 464l5.5-13 5.5 13z"/>' % px)

# Prazsky hrad
s('<path d="M1070 %d V472h640v%d z"/>' % (WL, WL - 472))
s('<path d="M1062 472h656v-13h-656z"/>')
s('<path d="M1290 %d V352h182v%d z"/>' % (WL, WL - 352))
s('<path d="M1284 352l91-38 91 38z"/>')
for tx in (1296, 1428):
    s('<path d="M%g %d V244h42v%d z"/>' % (tx, WL, WL - 244))
    s('<path d="M%g 244l21-70 21 70z"/>' % tx)
s('<path d="M1496 %d V284h52v%d z"/>' % (WL, WL - 284))
s('<path d="M1490 284l31-42 31 42z"/>')
s('<path d="M1514 242v-12h14v12z"/><path d="M1517 230l4-16 4 16z"/>')
for bx in range(1084, 1284, 38):
    s('<path d="M%g 472v-40h7v40z"/>' % bx)

# Karluv most
s('<path fill-rule="evenodd" d="M2150 %d h760v100h-760z'
  'M2192 600a46 56 0 0 1 92 0z'
  'M2304 600a46 56 0 0 1 92 0z'
  'M2416 600a46 56 0 0 1 92 0z'
  'M2528 600a46 56 0 0 1 92 0z'
  'M2640 600a46 56 0 0 1 92 0z'
  'M2752 600a46 56 0 0 1 92 0z"/>' % (WL - 100))
s('<path d="M2154 500V312h72v188z"/>')
s('<path d="M2148 312l42-62 42 62z"/>')
s('<path d="M2184 250v-26h10v26z"/>')
s('<path d="M2180 500v-60a10 10 0 0 1 20 0v60z" fill="%s"/>' % DARK)
s('<path d="M2828 500V330h58v170z"/>')
s('<path d="M2822 330l35-50 35 50z"/>')
s('<path d="M2896 500V388h42v112z"/>')
s('<path d="M2890 388l26-36 26 36z"/>')
s('<path d="M2884 500v-34a24 21 0 0 1 48 0v34z"/>')
s('<path d="M2896 500v-24a11 9 0 0 1 22 0v24z" fill="%s"/>' % DARK)
for sx in range(2258, 2810, 58):
    s('<path d="M%g 500v-19a5 5 0 0 1 10 0v19z"/>' % sx)

# Narodni divadlo
s('<path d="M3120 %d V430h340v%d z"/>' % (WL, WL - 430))
s('<path d="M3150 430v-32h280v32z"/>')
s('<path d="M3144 398l50-27 192 0 50 27z"/>')
s('<path d="M3128 430v-38h38v38z"/><path d="M3436 430v-38h38v38z"/>')
for ax in range(3174, 3418, 31):
    s('<path d="M%g %d v-92a11 11 0 0 1 22 0v92z" fill="%s"/>' % (ax, WL, MID))

# Tancici dum
s('<path d="M3752 %d V414h132v%d z"/>' % (WL, WL - 414))
s('<path d="M3744 414h148v-14h-148z"/>')
s('<path d="M3664 %d c7-84 50-113 41-170-5-37 19-56 51-51v221z"/>' % WL)
s('<ellipse cx="3818" cy="392" rx="50" ry="11"/>')

# Vysehrad
s('<path d="M4530 %d V462h400v%d z"/>' % (WL, WL - 462))
s('<path d="M4522 462h416v-12h-416z"/>')
s('<path d="M4600 %d V376h224v%d z"/>' % (WL, WL - 376))
s('<path d="M4594 376l118-32 118 32z"/>')
for tx in (4636, 4756):
    s('<path d="M%g %d V286h32v%d z"/>' % (tx, WL, WL - 286))
    s('<path d="M%g 286l16-80 16 80z"/>' % tx)
for bx in range(4544, 4930, 30):
    s('<path d="M%g 450v-14h15v14z"/>' % bx)
s('</g>')

# svetla
s('<g fill="%s">' % GLOW)
s('<circle cx="1375" cy="404" r="11" opacity=".22"/>')
s(lit(1090, 496, 14, 2, 38, 30, 6, 10, .5))
s(lit(1560, 496, 3, 2, 38, 30, 6, 10, .5))
s('<rect x="2172" y="352" width="9" height="14" opacity=".28"/>')
s('<rect x="2846" y="366" width="9" height="13" opacity=".28"/>')
for wx in range(3146, 3450, 30):
    s('<path d="M%g 462h13v30a6.5 6.5 0 0 0-13 0z" opacity="%.2f"/>'
      % (wx, random.choice([.2, .3, .42])))
for r in range(5):
    for c in range(4):
        s('<rect x="%g" y="%g" width="9" height="7" opacity="%.2f"/>'
          % (3766 + c * 30, 432 + r * 27, random.choice([.16, .26, .36])))
s(lit(4618, 392, 5, 1, 40, 26, 8, 14, .7))
s('<circle cx="4712" cy="410" r="9" opacity=".22"/>')
s('</g>')

skyline = "".join(sk)
n('<g id="skyline">%s</g>' % skyline)
n('<use href="#skyline" transform="translate(0 1200) scale(1 -1)" opacity=".16" mask="url(#pReflFade)"/>')

lamps = []
for lx in range(120, W, 240):
    lamps.append('<rect x="%g" y="%g" width="2.5" height="17" opacity=".22"/>' % (lx, WL - 30))
    lamps.append('<circle cx="%g" cy="%g" r="2.6" opacity=".42"/>' % (lx + 1.25, WL - 32))
    lamps.append('<circle cx="%g" cy="%g" r="7" opacity=".07"/>' % (lx + 1.25, WL - 32))
n('<g fill="%s">%s</g>' % (GLOW, "".join(lamps)))
n('<rect y="%d" width="%d" height="10" fill="%s"/>' % (WL - 10, W, DARK))

# ============================================================= 5. trpytky
foam = []
sh = []
for _ in range(80):
    sh.append('<rect x="%.0f" y="%.0f" width="%.0f" height="1.5" rx=".75" opacity="%.2f"/>'
              % (random.uniform(0, W * 1.12), random.uniform(WL + 14, H - 16),
                 random.uniform(24, 120), random.uniform(.05, .16)))
foam.append('<g fill="%s">%s</g>' % (GLOW, "".join(sh)))

FOAM_W = int(W * 1.12)
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
