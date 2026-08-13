# -*- coding: utf-8 -*-
"""
Generator panoramatu Prahy pro sekci Trasa. Deterministicky (seed).

Pet vrstev, kazda se pri scrollu posouva svym data-depth. Odtud hloubka.

  sky   0.10  obloha modre hodiny, hvezdy, mesic, hladina
  far   0.30  protejsi breh, svetly, temer bez detailu
  mid   0.55  stredni pasmo zastavby
  near  1.00  teren, nabrezni zed, dominanty, stromy, lode a odraz
  foam  1.06  trpytky na hladine

Tri pravidla, ktera drzi scenu pohromade:

  1. Nic nelevituje. Kazda stavba se kresli od strechy az pod korunu
     nabrezni zdi. Zed bezi pres celou sirku a je stejne cerna jako domy,
     takze se silueta spoji do jednoho tvaru a vse viditelne na necem stoji.
  2. Koruna zdi se kresli az nakonec, pres paty domu. Je to nejblizsi hrana
     sceny, musi prekryvat vsechno za sebou. Ta jedina svetla linka dela
     rozdil mezi mestem u reky a nalepkami na modrem papire.
  3. Cim dal, tim svetlejsi. Vzdusna perspektiva je jediny nastroj, kterym
     ploche siluety dostanou hloubku.

Vodorovne rozvrzeni odpovida zastavkam v route__stops. Pri bezne desktopove
scene je ve vyrezu zhruba 1350 jednotek viewBoxu, stred jede po
  center(p) ~ 675 + 3850 * p
a dominanty jsou usazene na tyto stredy.

Spusteni prepise vrstvy uvnitr <div class="route__stage"> v index.html.
"""
import math, random, io, os, re, sys

W, H = 5200, 780
WL = 600                      # hladina
QUAY = 566                    # koruna nabrezni zdi
random.seed(31)

SKY_A = "#16394E"             # zenit
SKY_B = "#2B6580"
SKY_C = "#74A5B6"
SKY_D = "#CDB48D"             # teply pas nad obzorem

FAR_HILL = "#7BA6B6"
FAR      = "#5E90A4"
MID      = "#2F6479"
NEAR     = "#102C3A"
CAP      = "#2A6076"          # koruna zdi v mesicnim svetle
DARK     = "#081C26"
GLOW     = "#F7E1AE"
WARM     = "#E9B65E"

TERRAIN = [
    (0, QUAY), (1500, QUAY),
    (1548, 486), (1590, 432), (2130, 428), (2215, 492), (2300, QUAY),
    (4020, QUAY), (4040, 522), (4056, 478), (4076, 452), (4110, 446), (4520, 446),
    (4610, 470), (4700, 518), (4800, QUAY),
    (W, QUAY),
]

# Otevrena voda za mosty. Nabrezni zed konci na urovni QUAY, cokoli dal od
# divaka ma hladinu prave tam. Mosty proto vyrustaji z QUAY, ne z WL, a za
# nimi se vykousne kus reky, aby oblouky nebyly zazdene do zastavby.
RIVER = [(950, 1476, 496), (2262, 2986, 486)]


def terrain(x):
    for i in range(len(TERRAIN) - 1):
        x0, y0 = TERRAIN[i]
        x1, y1 = TERRAIN[i + 1]
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / float(x1 - x0)
    return QUAY


def ground():
    p = ["M0 %d" % WL]
    for x, y in TERRAIN:
        p.append("L%g %g" % (x, y))
    p.append("L%d %d Z" % (W, WL))
    return " ".join(p)


def lit(x, y, cols, rows, gx, gy, w=5, h=8, chance=.42):
    """Rozsvicena okna. Mrizka, ze ktere sviti jen nahodna cast."""
    s = []
    for c in range(cols):
        for r in range(rows):
            if random.random() < chance:
                s.append('<rect x="%g" y="%g" width="%g" height="%g" opacity="%.2f"/>'
                         % (x + c * gx, y + r * gy, w, h,
                            random.choice([.22, .34, .48, .62])))
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


def pinnacle(cx, ty, w=9, h=60):
    """Fiala na rohu veze. Pata musi lezet uvnitr telesa veze, ne vedle nej,
    jinak fiala visi ve vzduchu."""
    return ('M%g %g v%g h%g v%g Z' % (cx - w / 2, ty, -h * .62, w, h * .62)
            + 'M%g %g l%g %g l%g %g Z'
            % (cx - w / 2 - 1.6, ty - h * .62, w / 2 + 1.6, -h * .38, w / 2 + 1.6, h * .38))


def spire(cx, ty, tw, h):
    """Stihla goticka spice s kriz kem na vrcholu."""
    hw = tw / 2.0
    return ('M%g %g l%g %g l%g %g Z' % (cx - hw, ty, hw, -h, hw, h)
            + 'M%g %g v-9 h4 v9 Z' % (cx - 2, ty - h))


def dormer(cx, ty, h):
    """Vikyr na sikme strese. Vyska se odvozuje od strechy, aby vikyr nikdy
    nepreteknul pres hreben, a pata sedi kousek pod povrchem, aby srostl."""
    w = h * 1.1
    return ('M%g %g v%g h%g v%g Z' % (cx - w / 2, ty, -h * .6, w, h * .6)
            + 'M%g %g l%g %g l%g %g Z'
            % (cx - w / 2 - 1.2, ty - h * .6, w / 2 + 1.2, -h * .4, w / 2 + 1.2, h * .4))


def victory(cx, ty):
    """Okridlena Vitezstvi na pylonech Cechova mostu."""
    return ('M%g %g v-15 c0 -6 8 -6 8 0 v15 Z' % (cx - 4, ty)
            + 'M%g %g a3.4 3.4 0 1 1 .1 0 Z' % (cx - 1.6, ty - 20)
            + 'M%g %g l-14 -19 l4 21 Z' % (cx - 3, ty - 13)
            + 'M%g %g l14 -19 l-4 21 Z' % (cx + 5, ty - 13)
            + 'M%g %g l11 -10 l3 3 l-11 10 Z' % (cx + 3, ty - 17))


def statue(x, ty):
    """Barokni sousosi na zabradli Karlova mostu."""
    return ('M%g %g v-9 h11 v9 Z' % (x, ty)
            + 'M%g %g v-13 c0 -5 7 -5 7 0 v13 Z' % (x + 2, ty - 9)
            + 'M%g %g a2.6 2.6 0 1 1 .1 0 Z' % (x + 4.2, ty - 24)
            + 'M%g %g l-5 -9 l2 10 Z' % (x + 2, ty - 16))


FRED_X0, FRED_X1 = 3774, 3884


def fred_y(x, r):
    """Vyska vlnici se rimsy na Fredove fasade v miste x pro radu r.

    Fasadu Tancicicho domu nedela mrizka oken, ale zvlnene rimsy: kazde patro
    se pres celou sirku prohne a okna se s nim houpou nahoru a dolu. Amplituda
    i faze se s patrem meni, jinak by z vlny byla pravidelna vlnovka.
    """
    y0 = 444 + r * 17
    amp = 3.4 + 1.8 * math.sin(r * 1.05)
    return y0 + amp * math.sin(x * .055 + r * .6)


def fred_facade():
    out = ['<g fill="none" stroke="#35748C" stroke-width="2" opacity=".5">']
    for r in range(7):                                   # rimsy mezi patry
        pts = []
        x = FRED_X0
        while x <= FRED_X1:
            pts.append('%g %.1f' % (x, fred_y(x, r)))
            x += 5
        out.append('<path d="M%s"/>' % "L".join(pts))
    out.append('</g><g>')
    for r in range(7):                                   # okna na vysku, sedici na rimse
        for c in range(6):
            wx = 3782 + c * 17
            out.append('<rect x="%g" y="%.1f" width="9" height="12" rx=".8" opacity="%.2f"/>'
                       % (wx, fred_y(wx + 4.5, r) - 14.5,
                          random.choice([.18, .28, .4, .52])))
    out.append('</g><g opacity=".34">')                  # prosklene prizemi
    for c in range(5):
        out.append('<rect x="%g" y="549" width="15" height="10" rx="1"/>' % (3780 + c * 21))
    # Ginger je sklo. Naznak podlazi drzim uvnitr nejuzsiho mista siluety,
    # aby zadna linka nevykoukla z obrysu ven.
    out.append('</g><g fill="none" stroke="#35748C" stroke-width="1.6" opacity=".3">')
    for r in range(7):
        out.append('<path d="M3706 %.1fH3744"/>' % (446 + r * 17))
    out.append('</g>')
    return "".join(out)


def quadriga(px, py):
    """Vuz se sprezenim na pylonu Narodniho divadla. Dily se prekryvaji,
    aby silueta drzela pohromade."""
    return ('M%g %g v-12 h11 v12 Z' % (px, py)
            + 'M%g %g v-10 l4 -6 h13 l4 6 v10 Z' % (px + 9, py)
            + 'M%g %g l3 -9 l4 1 l-3 8 Z' % (px + 15, py - 13)
            + 'M%g %g l3 -9 l4 1 l-3 8 Z' % (px + 21, py - 13)
            + 'M%g %g v-8 l3 -4 l4 4 v8 Z' % (px + 2, py - 9))


def arcade(x0, x1, top, foot, step, fill):
    """Rada podloubi. Oblouky se vykousnou do uz nakresleneho tela domu."""
    s = []
    x = x0
    while x + step <= x1:
        r = (step - 6) / 2.0
        s.append('<path d="M%g %g v%g a%g %g 0 0 1 %g 0 v%g Z" fill="%s"/>'
                 % (x, foot, -(foot - top - r), r, r, r * 2, foot - top - r, fill))
        x += step
    return "".join(s)


def roofline(x0, x1, hmin, hmax, unit, detail=2, base=None, foot=WL):
    """
    Rada mestskych domu. `base` vraci uroven terenu pro dane x, `foot` je
    uroven, ke ktere se kazdy dum dotahne dolu, takze nic nelevituje.
    detail 0 = jen obrysy, 1 = strechy a vikyre, 2 = plus okna.
    """
    base = base or (lambda _x: QUAY)
    body, wins = [], []
    x = x0
    while x < x1:
        w = random.randint(*unit)
        if x + w > x1:
            w = x1 - x
        if w < 16:
            break
        g = base(x + w / 2.0)
        top = g - random.randint(hmin, hmax)
        cx = x + w / 2.0
        r = random.random()
        spots = [.2, .76]

        if r < .40:                                   # sedlova strecha
            roof = random.randint(9, 17)
            body.append('M%g %g V%g l%g %g l%g %g V%g Z'
                        % (x, foot, top, w / 2.0, -roof, w / 2.0, roof, foot))
            chim = top - roof * .28
            spots = [.32, .68]
            if detail >= 1 and w > 30 and random.random() < .5:
                # 28 % delky sikminy: povrch strechy tam lezi na top - .56*roof
                body.append(dormer(x + w * .28, top - roof * .56 + 1.5, roof * .42))

        elif r < .58:                                 # mansarda
            b1 = random.randint(10, 16)
            b2 = random.randint(7, 12)
            body.append('M%g %g V%g l%g %g l%g %g l%g %g l%g %g V%g Z'
                        % (x, foot, top, w * .18, -b1, w * .32, -b2,
                           w * .32, b2, w * .18, b1, foot))
            chim = top - b1 * .5

        elif r < .74:                                 # plocha s rimsou
            body.append('M%g %g V%g h%g V%g Z' % (x, foot, top, w, foot))
            body.append('M%g %g h%g v5 h%g Z' % (x - 2, top - 5, w + 4, -(w + 4)))
            chim = top + 2

        elif r < .89:                                 # barokni vez s bani
            body.append('M%g %g V%g h%g V%g Z' % (x, foot, top, w, foot))
            tw = max(11, w * .34)
            body.append('M%g %g v%g h%g v%g Z' % (cx - tw / 2.0, top, -26, tw, 26))
            body.append(onion(cx, top - 26, tw))
            chim = top + 2
            spots = [.08, .88]

        else:                                         # goticka vez
            body.append('M%g %g V%g h%g V%g Z' % (x, foot, top, w, foot))
            tw = max(10, w * .3)
            body.append('M%g %g v%g h%g v%g Z' % (cx - tw / 2.0, top, -30, tw, 30))
            body.append(spire(cx, top - 30, tw, tw * 2.1))
            chim = top + 2
            spots = [.08, .88]

        if random.random() < .3:
            cw = 4
            # komin musi lezet celou sirkou nad telem domu, jinak visi pres okraj
            cxx = min(max(x + w * random.choice(spots), x + 2), x + w - cw - 2)
            ch = random.randint(9, 16)
            body.append('M%g %g v%g h%g v%g Z' % (cxx, chim, -ch, cw, ch))

        if detail >= 2 and w > 26 and g - top > 42:
            cols = max(1, int((w - 10) // 13))
            rows = max(1, int((g - top - 22) // 19))
            wins.append(lit(x + 6, top + 15, cols, rows, 13, 19, 4, 6, .3))

        x += w + random.randint(1, 5)

    out = '<path d="%s"/>' % "".join(body)
    if wins:
        out += '<g fill="%s">%s</g>' % (GLOW, "".join(wins))
    return out


def trees(x0, x1, step=(46, 78)):
    """Stromoradi. Koruna z prekryvajicich se kruhu, kmen vzdy az na teren
    pod sebou, aby stromy na svahu nevisely ve vzduchu."""
    s = []
    x = x0
    while x < x1:
        h = random.randint(24, 40)
        g = terrain(x)
        ty = g - 10 - h
        ty0 = ty + h * .55
        s.append('<rect x="%g" y="%g" width="3" height="%g"/>' % (x - 1.5, ty0, g - ty0))
        for dx, dy, rr in ((0, 0, h * .42), (-h * .26, h * .14, h * .3),
                           (h * .26, h * .12, h * .32), (0, h * .3, h * .3)):
            s.append('<circle cx="%g" cy="%g" r="%g"/>' % (x + dx, ty + dy, rr))
        x += random.randint(*step)
    return "".join(s)


def moored(x, scale=1.0):
    """Zakotvena lodka. Plave na blizke hladine pred zdi, proto svetlejsi ton,
    jinak by splynula s nabrezim a zbyl by z ni necitelny flek."""
    return ('<g transform="translate(%g %g) scale(%g)" fill="#1C4759">' % (x, WL + 13, scale) +
            '<path d="M0 0h66l-9 13H9z"/>'
            '<rect x="13" y="-11" width="40" height="11" rx="1.5"/>'
            '<rect x="30" y="-24" width="3" height="13"/>'
            '<path d="M-4 -1h74v2.6H-4z" opacity=".5"/>'
            '<g fill="%s" opacity=".45"><rect x="19" y="-8" width="5" height="5"/>'
            '<rect x="28" y="-8" width="5" height="5"/>'
            '<rect x="37" y="-8" width="5" height="5"/></g>'
            '</g>' % GLOW)


# ================================================================= 1. obloha
sky = ['<defs>'
       '<linearGradient id="pSky" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0%" stop-color="' + SKY_A + '"/>'
       '<stop offset="42%" stop-color="' + SKY_B + '"/>'
       '<stop offset="76%" stop-color="' + SKY_C + '"/>'
       '<stop offset="100%" stop-color="' + SKY_D + '"/></linearGradient>'
       '<linearGradient id="pWater" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0%" stop-color="#5A8DA0"/>'
       '<stop offset="34%" stop-color="#2B5E72"/>'
       '<stop offset="100%" stop-color="#0E2A38"/></linearGradient>'
       '<radialGradient id="pMoon">'
       '<stop offset="0" stop-color="#FFF3D6" stop-opacity=".26"/>'
       '<stop offset=".2" stop-color="#FFF3D6" stop-opacity=".13"/>'
       '<stop offset=".5" stop-color="#FFF3D6" stop-opacity=".04"/>'
       '<stop offset="1" stop-color="#FFF3D6" stop-opacity="0"/></radialGradient>'
       '</defs>']
sky.append('<rect width="%d" height="%d" fill="url(#pSky)"/>' % (W, WL))

st = []
for _ in range(78):
    st.append('<circle cx="%.0f" cy="%.0f" r="%.1f" opacity="%.2f"/>'
              % (random.uniform(0, W), random.uniform(10, 250),
                 random.choice([1.1, 1.5, 1.9]), random.uniform(.16, .46)))
sky.append('<g fill="#FFF8E6">%s</g>' % "".join(st))

# Mesic. Zare je jeden radialni prechod, ne stoh plosnych kruhu; ty delaly
# viditelne mezikruzi. Vykrojeni srpku je plocha barva oblohy v teto vysce a
# zare se kresli az pres nej, takze prechod vykrojeni do oblohy nikde nedrhne.
sky.append('<g><circle cx="1120" cy="128" r="26" fill="#FFF6E0" opacity=".95"/>'
           '<circle cx="1108" cy="118" r="25" fill="#204E65"/>'
           '<circle cx="1120" cy="128" r="150" fill="url(#pMoon)"/></g>')
sky.append('<rect y="%d" width="%d" height="%d" fill="url(#pWater)"/>' % (WL, W, H - WL))

# ================================================================== 2. dalka
# Protejsi breh. Kopce nejdriv, pak nejsvetlejsi rada strech pred nimi.
hills = ['M0 552']
for hx, hy in ((0, 498), (420, 470), (900, 424), (1340, 392), (1820, 404),
               (2280, 460), (2900, 494), (3500, 470), (4100, 418), (4700, 452),
               (W, 496)):
    hills.append('L%g %g' % (hx, hy))
hills.append('L%d %d L0 %d Z' % (W, WL, WL))
far = ['<path d="%s" fill="%s" opacity=".32"/>' % (" ".join(hills), FAR_HILL)]
far.append('<g fill="%s" opacity=".5">%s</g>'
           % (FAR_HILL, roofline(0, W, 14, 44, (18, 32), detail=0,
                                 base=lambda _x: 548, foot=WL)))
far.append('<g fill="%s" opacity=".62">%s</g>'
           % (FAR, roofline(0, W, 20, 60, (20, 36), detail=1,
                            base=lambda _x: 554, foot=WL)))

# ================================================================== 3. stred
mid = ['<g fill="%s" opacity=".88">%s</g>'
       % (MID, roofline(0, W, 28, 82, (22, 42), detail=1,
                        base=lambda _x: 560, foot=WL))]

# ================================================================= 4. blizko
near = []
n = near.append
n('<defs><linearGradient id="pRefl" x1="0" y1="%d" x2="0" y2="%d" gradientUnits="userSpaceOnUse">'
  '<stop offset="0" stop-color="#fff" stop-opacity=".9"/>'
  '<stop offset=".5" stop-color="#fff" stop-opacity=".34"/>'
  '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
  '<mask id="pReflFade"><rect y="%d" width="%d" height="%d" fill="url(#pRefl)"/></mask></defs>'
  % (WL, H, WL, W, H - WL))

# --- reka za mosty. Kresli se pred zastavbu, aby oblouky mely cim prosvitat,
#     a mimo #skyline, protoze svetla plocha nema co delat v odrazu.
pre = []
for rx0, rx1, ry in RIVER:
    pre.append('<rect x="%g" y="%g" width="%g" height="%g" fill="#3D7488"/>'
               % (rx0 - 14, ry, rx1 - rx0 + 28, QUAY - ry))
    pre.append('<rect x="%g" y="%g" width="%g" height="2" fill="#7FAEBE" opacity=".5"/>'
               % (rx0 - 14, ry, rx1 - rx0 + 28))
n("".join(pre))

sk = []
s = sk.append

# --- teren: hradcanske a vysehradske navrsi
s('<path d="%s" fill="%s"/>' % (ground(), NEAR))

# --- zastavba mezi dominantami; vse ve stejne cerni, silueta se spoji
s('<g fill="%s">' % NEAR)
for x0, x1 in ((40, 900), (1500, 1580), (3000, 3086),
               (3430, 3648), (3900, 4014), (4800, W)):
    s(roofline(x0, x1, 40, 104, (26, 46), base=terrain))

# --- Cechuv most (secese, 1908): tri velke oblouky, ctyri pylony s Vitezstvimi
arch = []
for i in range(3):
    ax = 962 + i * 166
    arch.append('M%g %d a70 58 0 0 1 140 0 Z' % (ax, QUAY))
s('<path fill-rule="evenodd" d="M950 486h520v80H950z%s"/>' % "".join(arch))
s('<path d="M944 486h532v-9h-532z"/>')
for px in (952, 1118, 1284, 1456):
    s('<path d="M%g 477v-46h13v46z"/>' % px)
    s('<path d="%s"/>' % victory(px + 6.5, 433))
for lx in range(1000, 1440, 62):
    s('<path d="M%g 477v-15h2.6v15z"/>' % lx)

# --- Prazsky hrad a katedrala sv. Vita
s('<path d="M1620 %d V372h500v%d z"/>' % (WL, WL - 372))
s('<path d="M1612 372h516v-13h-516z"/>')
s('<path d="M1612 359h516v-6h-516z"/>')
for bx in range(1630, 1812, 30):                       # vikyre nad rimsou kridla
    s('<path d="M%g 359v-30h7l3-7v37z"/>' % bx)
for bx in range(2062, 2112, 24):
    s('<path d="M%g 359v-30h7l3-7v37z"/>' % bx)

s('<path d="M1846 %d V300h150v%d z"/>' % (WL, WL - 300))          # hlavni lod
s('<path d="M1838 300l83-30 83 30z"/>')                            # sedlova strecha
s('<path d="M1917 276v-42h8v42z"/>')                               # sanktusnik, pata v hrebeni
s('<path d="%s"/>' % spire(1921, 234, 9, 30))
for tx in (1848, 1954):                                            # zapadni veze
    s('<path d="M%g %d V236h40v%d z"/>' % (tx, WL, WL - 236))
    s('<path d="M%g 236h-6l26-78 26 78h-6z"/>' % tx)
# Jizni vez zabira i posledni ctyri jednotky lodi. Kdyby zacinala az za ni,
# zustala by mezi nimi svisla skvira oblohy.
s('<path d="M1992 %d V266h64v%d z"/>' % (WL, WL - 266))
s('<path d="M1986 266h76v-12h-76z"/>')
s('<path d="%s"/>' % onion(2024, 254, 44))
s('<circle cx="1921" cy="338" r="16" fill="%s"/>' % DARK)
s('<circle cx="1921" cy="338" r="11" fill="%s" opacity=".34"/>' % GLOW)

# --- Karluv most: devet oblouku, veze na obou koncich, sousosi na zabradli
arch = []
for i in range(9):
    ax = 2394 + i * 56
    arch.append('M%g %d a22 52 0 0 1 44 0 Z' % (ax, QUAY))
s('<path fill-rule="evenodd" d="M2262 476h724v90h-724z%s"/>' % "".join(arch))
s('<path d="M2256 476h736v-9h-736z"/>')
for sx in range(2402, 2884, 48):
    s('<path d="%s"/>' % statue(sx, 469))

s('<path d="M2918 %d V240h64V%d z"/>' % (QUAY, QUAY))              # Staromestska vez
for cx in (2924, 2976):                                            # fialy na rozich
    s('<path d="%s"/>' % pinnacle(cx, 250))
s('<path d="M2912 240l38-58 38 58z"/>')
s('<path d="M2946 190v-34h8v34z"/>')
s('<path d="M2936 467v-64a14 14 0 0 1 28 0v64z" fill="%s"/>' % DARK)

s('<path d="M2316 %d V270h60V%d z"/>' % (QUAY, QUAY))              # Malostranske veze
for cx in (2322, 2370):
    s('<path d="%s"/>' % pinnacle(cx, 278, 8, 46))
s('<path d="M2310 270l36-54 36 54z"/>')
s('<path d="M2342 222v-26h8v26z"/>')
s('<path d="M2262 %d V330h46V%d z"/>' % (QUAY, QUAY))
s('<path d="M2256 330l29-42 29 42z"/>')
s('<path d="M2302 467v-38a11 14 0 0 1 22 0v38z"/>')                # branska zed mezi vezemi
s('<path d="M2307 467v-25a11 13 0 0 1 22 0v25z" fill="%s"/>' % DARK)

# --- Narodni divadlo. Klenuta strecha musi zacinat presne na rozich atiky,
#     jinak jeji konce trci nad rimsu do vzduchu.
s('<path d="M3106 %d V446h298v%d z"/>' % (WL, WL - 446))
s('<path d="M3098 446h314v-14h-314z"/>')
s('<path d="M3134 432h242v-32h-242z"/>')
s('<path d="M3134 400c54 -34 188 -34 242 0z"/>')                   # klenuta strecha
s('<path d="M3096 %d V404h44v%d z"/>' % (WL, WL - 404))            # rohove pylony
s('<path d="M3370 %d V404h44v%d z"/>' % (WL, WL - 404))
for qx in (3100, 3374):
    s('<path d="%s"/>' % quadriga(qx, 405))                        # pata v korune pylonu
s(arcade(3128, 3390, 462, 512, 32, MID))

# --- Tancici dum. Fred stoji rovne, Ginger se stahuje v pase. Mezi nimi musi
#     v urovni pasu zustat kus oblohy, jinak z dvojice zbyde jeden beztvary kopec.
s('<path d="M3772 %d V424h114v%d z"/>' % (WL, WL - 424))           # Fred
s('<path d="M3766 424h126v-13h-126z"/>')
s('<path d="M3798 411a30 24 0 0 1 60 0z"/>')                       # medusa
s('<path d="M3826 387v-16h5v16z"/>')
# Ginger. Dole se opira o Freda, nahore se od nej odklani; skvira mezi nimi
# musi byt jen v pase, ne prasklina tahnouci se az k nabrezi.
s('<path d="M3672 %d C3678 526 3698 508 3702 480 '
  'C3705 456 3690 440 3694 416 H3758 '
  'C3754 442 3746 458 3750 482 C3756 516 3764 544 3772 %d Z"/>' % (WL, WL))
s('<path d="M3690 416h72v-9h-72z"/>')

# --- Vysehrad: hradby s cimburim a bazilika sv. Petra a Pavla
s('<path d="M4120 446h400v-16h-400z"/>')
for bx in range(4124, 4512, 26):
    s('<path d="M%g 430v-11h13v11z"/>' % bx)
s('<path d="M4300 %d V366h124v%d z"/>' % (WL, WL - 366))
s('<path d="M4292 366l70-26 70 26z"/>')
for tx in (4288, 4398):
    s('<path d="M%g %d V286h38v%d z"/>' % (tx, WL, WL - 286))
    s('<path d="M%g 286h-6l25-84 25 84h-6z"/>' % tx)
s('<circle cx="4362" cy="398" r="13" fill="%s"/>' % DARK)
s('<circle cx="4362" cy="398" r="9" fill="%s" opacity=".3"/>' % GLOW)
s('<path d="M4172 %d V414h38v%d z"/>' % (WL, WL - 414))            # rotunda sv. Martina
s('<path d="M4166 414l25-24 25 24z"/>')
s('<path d="M4189 392v-11h4v11z"/>')
s('</g>')

# --- rozsvicena okna dominant
s('<g fill="%s">' % GLOW)
s(lit(1636, 386, 6, 2, 36, 29, 7, 11, .62))                         # zapadni kridlo hradu
s(lit(2066, 386, 2, 2, 30, 29, 7, 11, .62))                         # vychodni kridlo
s('<rect x="2944" y="300" width="11" height="16" opacity=".34"/>')  # Staromestska vez
s('<rect x="2340" y="330" width="11" height="15" opacity=".3"/>')   # Malostranska vez
for wx in range(3134, 3390, 32):                                    # arkada divadla
    s('<path d="M%g 510v-27a7 7 0 0 1 14 0v27z" opacity="%.2f"/>'
      % (wx, random.choice([.22, .34, .46])))
s(fred_facade())                                                    # Tancici dum
s('<rect x="4322" y="392" width="10" height="16" opacity=".5"/>')   # bazilika
s('<rect x="4384" y="392" width="10" height="16" opacity=".42"/>')
s('</g>')

# --- nabrezni zed. Kresli se pres paty domu, je to nejblizsi hrana sceny.
s('<rect y="%d" width="%d" height="%d" fill="%s"/>' % (QUAY, W, WL - QUAY, NEAR))
for jx in range(0, W, 46):
    s('<rect x="%g" y="%d" width="1.6" height="%d" fill="%s" opacity=".5"/>'
      % (jx, QUAY + 4, WL - QUAY - 4, DARK))
for sx in (620, 2060, 3560, 4700):                                  # schody k vode
    s('<rect x="%g" y="%d" width="46" height="%d" fill="#153A4B"/>' % (sx, QUAY, WL - QUAY))
    for i in range(6):
        s('<rect x="%g" y="%.1f" width="%g" height="2" fill="%s" opacity=".5"/>'
          % (sx, QUAY + 2 + i * 5.4, 46 - i * 7, CAP))
s('<rect y="%d" width="%d" height="5" fill="%s"/>' % (QUAY - 5, W, CAP))
s('<rect y="%d" width="%d" height="1.5" fill="%s" opacity=".5"/>' % (QUAY - 6.5, W, GLOW))

# --- molo pro nalodeni. Stoji na blizke vode pred zdi, proto stejny svetlejsi
#     ton jako zakotvene lodky; v cerni zdi by po nem nezbylo nic.
s('<g fill="#1C4759">')
s('<path d="M694 %d h212v10H694z"/>' % (WL - 8))
s('<path d="M688 %d l14 -22h10l-14 22z"/>' % (WL - 8))               # lavka od zdi
for mx in range(704, 900, 32):
    s('<rect x="%g" y="%d" width="6" height="26"/>' % (mx, WL + 2))
for rx in range(700, 906, 34):                                       # zabradli
    s('<rect x="%g" y="%d" width="3" height="20"/>' % (rx, WL - 28))
s('<rect x="698" y="%d" width="204" height="3"/>' % (WL - 28))
s('<path d="M892 %d v-40h5v40z"/>' % (WL - 8))                       # palek s lucernou
s('</g>')
s('<circle cx="894.5" cy="%d" r="3.4" fill="%s" opacity=".6"/>' % (WL - 50, GLOW))

# --- stromoradi, palery, patniky
s('<g fill="%s">' % NEAR)
for a0, a1, stp in ((70, 660, (54, 92)), (1500, 1560, (54, 74)), (3000, 3090, (52, 84)),
                    (3440, 3640, (54, 90)), (3900, 4010, (52, 86)), (4830, W, (54, 90))):
    s('<g opacity=".95">%s</g>' % trees(a0, a1, stp))
for bx, k in ((1010, .9), (2470, .8), (3120, .95), (4210, 1.0), (4880, .85)):
    s(moored(bx, k))
for px in range(120, W, 190):
    s('<path d="M%g %d v-9 a4 4 0 0 1 8 0 v9z" opacity=".9"/>' % (px, QUAY - 5))
s('</g>')

# --- palery na zdi
lamps = []
for lx in range(180, W, 220):
    lamps.append('<rect x="%g" y="%g" width="2.6" height="24" opacity=".24"/>' % (lx, QUAY - 29))
    lamps.append('<circle cx="%g" cy="%g" r="2.8" opacity=".55"/>' % (lx + 1.3, QUAY - 30))
    lamps.append('<circle cx="%g" cy="%g" r="8" opacity=".07"/>' % (lx + 1.3, QUAY - 30))
s('<g fill="%s">%s</g>' % (GLOW, "".join(lamps)))

skyline = "".join(sk)
n('<g id="skyline">%s</g>' % skyline)

# --- odraz. Zrcadlo kolem hladiny, stlacene na 55 %, aby se do pasu vody vesly
#     i veze, ztlumene a rozcuchane vlnkami. y' = 930 - 0.55y, tedy hladina
#     zustava na svem miste a vse nad ni se do vody sklopi.
#     Maska visi na obalovem <g>, ne primo na <use>. Transformace elementu se
#     totiz aplikuje i na obsah masky a prevracena maska by odraz odstrihla.
n('<g mask="url(#pReflFade)"><use href="#skyline" '
  'transform="translate(0 %g) scale(1 -0.55)" opacity=".6"/></g>' % (WL * 1.55))
rip = []
for _ in range(150):
    ry = random.uniform(WL + 3, H)
    rip.append('<rect x="%.0f" y="%.1f" width="%.0f" height="%.1f" opacity="%.2f"/>'
               % (random.uniform(-60, W), ry, random.uniform(70, 300),
                  random.uniform(1.4, 3.2),
                  .1 + .22 * (1 - (ry - WL) / float(H - WL))))
n('<g fill="#6E9EB2">%s</g>' % "".join(rip))

# ================================================================ 5. trpytky
FOAM_W = int(W * 1.12)
sh = []
for _ in range(90):
    sh.append('<rect x="%.0f" y="%.0f" width="%.0f" height="1.6" rx=".8" opacity="%.2f"/>'
              % (random.uniform(0, FOAM_W), random.uniform(WL + 10, H - 12),
                 random.uniform(26, 130), random.uniform(.06, .2)))
foam = ['<g fill="#FFF0CE">%s</g>' % "".join(sh)]

LAYERS = [("0.10", sky, W), ("0.30", far, W), ("0.55", mid, W),
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
