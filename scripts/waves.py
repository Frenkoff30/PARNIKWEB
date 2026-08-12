# -*- coding: utf-8 -*-
"""
Generator SVG cest pro vlny.

Vlna se sklada z celeho poctu period, aby ji slo posouvat o polovinu sirky
viewBoxu (1440) a navazovala sama na sebe bez svu. Prvni segment je 'c'
(urcuje oba kontrolni body), dalsi 's' (druhy kontrolni bod na 2h, prvni
se dopocita reflexi).

Spusteni prepise cesty ve vsech *.html.
"""
import io, glob, re, sys, os

TOTAL = 2880          # sirka viewBoxu
SHIFT = TOTAL // 2    # o kolik se vlna posouva (musi byt nasobek periody)


def wave(y0, seg, amp, total=TOTAL):
    """Vrati 'd' cestu vlny slozene z celych period."""
    n = total // seg
    if n * seg != total:
        raise ValueError("segment %d nedeli sirku %d" % (seg, total))
    if SHIFT % (2 * seg):
        raise ValueError("posun %d neni nasobek periody %d" % (SHIFT, 2 * seg))

    h = seg / 3.0
    d = "M0 %d" % y0
    d += "c%g-%d %g-%d %d 0" % (h, amp, 2 * h, amp, seg)

    parts = []
    for i in range(1, n):
        dy = amp if i % 2 == 1 else -amp
        x2 = 2 * h
        parts.append(("%g %d %d 0" % (x2, dy, seg)) if dy > 0
                     else ("%g%d %d 0" % (x2, dy, seg)))
    return d + "s" + " ".join(parts)


A = wave(66, 360, 24)   # spodni vrstva, perioda 720
B = wave(84, 240, 16)   # horni vrstva, perioda 480

BLOCK = (
 '    <svg class="waves__a" viewBox="0 0 %d 120" preserveAspectRatio="none"><path d="%sV120H0Z"/></svg>\n'
 '    <svg class="waves__b" viewBox="0 0 %d 120" preserveAspectRatio="none"><path d="%sV120H0Z"/></svg>\n'
 '    <svg class="waves__glint" viewBox="0 0 %d 120" preserveAspectRatio="none"><path d="%s" fill="none"/></svg>'
) % (TOTAL, A, TOTAL, B, TOTAL, A)

PATTERN = (r'[ ]*<svg class="waves__a".*?</svg>\s*\n'
           r'[ ]*<svg class="waves__b".*?</svg>\s*\n'
           r'[ ]*<svg class="waves__glint".*?</svg>')

if __name__ == "__main__":
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
    total = 0
    for f in sorted(glob.glob(os.path.join(root, "*.html"))):
        t = io.open(f, encoding="utf-8").read()
        t, k = re.subn(PATTERN, lambda m: BLOCK, t, flags=re.S)
        if k:
            io.open(f, "w", encoding="utf-8", newline="").write(t)
        total += k
        print(os.path.basename(f), "bloku:", k)
    print("celkem prepsano bloku:", total)
    if not total:
        sys.exit("nic nenalezeno, zkontroluj PATTERN")
