#!/usr/bin/env python3
"""The World Today - 22 November 2026.

Pure-stdlib Python that paints a newspaper front page summing up the
world news of Sunday, 22 November 2026 as a single 1024x1024 PNG.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
No network, no third-party modules, deterministic: repeated runs write
identical bytes.

Lead + six verified stories of 22 November 2026:
  Lead: drones set the sanctioned Russian cargo ship Sparta II ablaze
    in the Gulf of Finland; the burning ship drifts into Finnish
    waters and Finland warns the war is spilling over.
  1. Antalya: COP31 climate talks deadlocked 36 hours into overtime;
    the draft deal drops every mention of fossil fuels.
  2. Shenzhen: Trump, Xi and Putin meet at the APEC summit and pledge
    to pump more oil.
  3. Mexico: FBI top-10 cartel boss 'El Chapo Isidro' arrested in a
    shoot-out.
  4. Gulf: tankers hit off Oman as Iran-US naval tensions escalate.
  5. Estonia: to close its border with Russia; Moscow cries 'new Iron
    Curtain'.
  6. US skies: airlines warned of possible Al-Qaeda-linked attacks
    ahead of Thanksgiving.
Footer: Zelensky calls the Crimean Bridge strikes a fair response;
Denmark accuses Russia of an assassination plot; Australia ends
England's T20 winning streak.
"""

import os
import struct
import zlib
from pathlib import Path

SIZE = 1024

NEWS = (250, 246, 238)      # newsprint
BLACK = (20, 20, 20)
CRIMSON = (178, 34, 34)
DEEPBLUE = (30, 64, 120)
SEA = (54, 106, 160)
SKY = (196, 214, 230)
SAND = (152, 186, 122)
AMBER = (200, 162, 42)
SLATE = (100, 100, 100)
CREAM = (234, 228, 214)
FLAME = (228, 118, 56)
EMBER = (240, 170, 60)
PINE = (26, 122, 114)
MIDNIGHT = (26, 40, 70)

# ------------------------------------------------------------------ type
# 5x7 pixel type. Each letter is seven strings of five cells; '#' is ink.
TYPE = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}


def glyph_width(text, scale):
    return len(text) * 6 * scale - scale


def fold(text, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines, current = [], ""
    for word in text.split(" "):
        if current and len(current) + 1 + len(word) > max_chars:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def set(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = bytes(col)

    def rect(self, x, y, w, h, col):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, col)

    def hline(self, x, y, w, col):
        self.rect(x, y, w, 1, col)

    def vline(self, x, y, h, col):
        self.rect(x, y, 1, h, col)

    def frame(self, x, y, w, h, col, t=1):
        self.rect(x, y, w, t, col)
        self.rect(x, y + h - t, w, t, col)
        self.rect(x, y, t, h, col)
        self.rect(x + w - t, y, t, h, col)

    def circle(self, cx, cy, r, col):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, col)

    def ring(self, cx, cy, r, col, t=2):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d <= (r + t) ** 2:
                    self.set(xx, yy, col)

    def ellipse(self, cx, cy, rx, ry, col):
        for yy in range(cy - ry, cy + ry + 1):
            for xx in range(cx - rx, cx + rx + 1):
                if ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0:
                    self.set(xx, yy, col)

    def line(self, x0, y0, x1, y1, col):
        """Bresenham segment."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, col)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def fill_poly(self, pts, col):
        """Scanline polygon fill."""
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(x, y, col)

    def char(self, ch, x, y, scale, col):
        rows = TYPE.get(ch.upper(), TYPE['?'])
        for r in range(7):
            for c in range(5):
                if rows[r][c] == '1':
                    self.rect(x + c * scale, y + r * scale,
                              scale, scale, col)

    def text(self, s, x, y, scale, col):
        cx = x
        for ch in s:
            self.char(ch, cx, y, scale, col)
            cx += 6 * scale
        return cx

    def text_centre(self, s, cx, y, scale, col):
        self.text(s, cx - glyph_width(s, scale) // 2, y, scale, col)

    def block(self, s, x, y, width, scale, col, gap=None):
        if gap is None:
            gap = 9 * scale
        chars = max(1, width // (6 * scale))
        lines = fold(s, chars)
        for i, line in enumerate(lines):
            self.text(line, x, y + i * gap, scale, col)
        return len(lines)


def dotted_arc(cv, p0, pc, p1, col, step=0.02):
    """Dotted quadratic bezier (drone trail)."""
    n = 0
    t = 0.0
    while t <= 1.0:
        u = 1.0 - t
        x = int(u * u * p0[0] + 2 * u * t * pc[0] + t * t * p1[0])
        y = int(u * u * p0[1] + 2 * u * t * pc[1] + t * t * p1[1])
        if n % 3 == 0:
            cv.circle(x, y, 2, col)
        n += 1
        t += step


# ------------------------------------------------------------- tile art
def art_globe(cv, x, y, col):
    cv.ring(x + 20, y + 18, 15, col, 2)
    cv.ellipse(x + 20, y + 18, 15, 6, col)
    cv.vline(x + 20, y + 3, 30, col)
    cv.line(x + 8, y + 10, x + 32, y + 26, col)
    cv.line(x + 32, y + 10, x + 8, y + 26, col)


def art_flags3(cv, x, y, col):
    # three small pennants: US, China, Russia (abstract stripes).
    for i, (a, b) in enumerate(((CRIMSON, NEWS), (CRIMSON, (222, 190, 40)),
                               (NEWS, CRIMSON))):
        fx = x + i * 14
        cv.rect(fx, y + 4, 12, 5, a)
        cv.rect(fx, y + 9, 12, 5, b)
        cv.rect(fx, y + 14, 12, 5, col)
        cv.vline(fx, y + 4, 32, col)


def art_badge(cv, x, y, col):
    cv.fill_poly([(x + 20, y + 2), (x + 26, y + 12), (x + 38, y + 12),
                  (x + 28, y + 20), (x + 32, y + 32), (x + 20, y + 25),
                  (x + 8, y + 32), (x + 12, y + 20), (x + 2, y + 12),
                  (x + 14, y + 12)], col)
    cv.circle(x + 20, y + 16, 4, NEWS)


def art_tanker(cv, x, y, col):
    cv.rect(x + 2, y + 20, 36, 10, col)
    cv.rect(x + 8, y + 12, 10, 8, col)
    cv.rect(x + 24, y + 14, 6, 6, col)
    cv.vline(x + 30, y + 6, 8, col)
    cv.line(x + 2, y + 34, x + 10, y + 38, SEA)
    cv.line(x + 14, y + 34, x + 22, y + 38, SEA)
    cv.line(x + 26, y + 34, x + 34, y + 38, SEA)


def art_gate(cv, x, y, col):
    cv.vline(x + 4, y + 6, 30, col)
    cv.vline(x + 36, y + 6, 30, col)
    for yy in range(y + 8, y + 30, 5):
        cv.hline(x + 4, yy, 32, col)
    cv.fill_poly([(x + 16, y + 2), (x + 24, y + 2), (x + 20, y + 8)], CRIMSON)


def art_plane(cv, x, y, col):
    cv.fill_poly([(x + 2, y + 20), (x + 34, y + 10), (x + 38, y + 14),
                  (x + 20, y + 22), (x + 30, y + 30), (x + 24, y + 30),
                  (x + 14, y + 24), (x + 6, y + 26), (x + 8, y + 22)], col)
    cv.circle(x + 34, y + 12, 2, NEWS)


# ------------------------------------------------------------------ page
def paint():
    cv = Canvas(SIZE, SIZE, NEWS)
    cv.frame(10, 10, SIZE - 20, SIZE - 20, BLACK, 3)
    cv.frame(18, 18, SIZE - 36, SIZE - 36, BLACK, 1)

    # Masthead
    cv.text_centre("THE WORLD TODAY", SIZE // 2, 34, 6, BLACK)
    cv.hline(48, 92, SIZE - 96, BLACK)
    cv.hline(48, 96, SIZE - 96, BLACK)
    cv.text_centre("SUNDAY 22 NOVEMBER 2026 - THE DAY IN WORLD NEWS",
                   SIZE // 2, 108, 2, CRIMSON)

    # ---- lead art: Gulf of Finland, burning Sparta II ---------------
    ax, ay, aw, ah = 40, 138, 944, 238
    cv.frame(ax, ay, aw, ah, BLACK, 2)
    cv.rect(ax + 2, ay + 2, aw - 4, ah - 4, SEA)
    # Finland (north), Estonia (south), Russia (east) as land masses.
    finland = [(ax + 60, ay + 8), (ax + 330, ay + 8), (ax + 350, ay + 60),
               (ax + 300, ay + 96), (ax + 180, ay + 92), (ax + 90, ay + 60)]
    estonia = [(ax + 60, ay + 168), (ax + 330, ay + 168), (ax + 360, ay + 200),
               (ax + 320, ay + 228), (ax + 120, ay + 228), (ax + 70, ay + 200)]
    russia = [(ax + 700, ay + 8), (ax + 936, ay + 8), (ax + 936, ay + 228),
              (ax + 700, ay + 228), (ax + 660, ay + 160), (ax + 660, ay + 70)]
    for land in (finland, estonia, russia):
        cv.fill_poly(land, SAND)
        for i in range(len(land)):
            x0, y0 = land[i]
            x1, y1 = land[(i + 1) % len(land)]
            cv.line(x0, y0, x1, y1, MIDNIGHT)
    cv.text("FINLAND", ax + 130, ay + 40, 2, MIDNIGHT)
    cv.text("ESTONIA", ax + 130, ay + 192, 2, MIDNIGHT)
    cv.text("RUSSIA", ax + 760, ay + 110, 2, MIDNIGHT)
    cv.text("GULF OF FINLAND", ax + 430, ay + 118, 2, NEWS)
    # sea lanes
    for yy in (150, 158):
        cv.hline(ax + 380, ay + yy, 260, NEWS)
    # the burning ship, mid-gulf
    sx, sy = 500, 202
    cv.rect(sx - 62, sy, 124, 18, BLACK)
    cv.rect(sx - 40, sy - 16, 26, 16, BLACK)
    cv.rect(sx + 8, sy - 12, 14, 12, BLACK)
    cv.vline(sx + 40, sy - 26, 26, BLACK)
    # flames and smoke
    cv.fill_poly([(sx - 30, sy), (sx - 18, sy - 34), (sx - 6, sy - 8),
                  (sx + 6, sy - 30), (sx + 18, sy - 6), (sx + 30, sy - 26),
                  (sx + 38, sy)], FLAME)
    cv.fill_poly([(sx - 12, sy - 20), (sx - 2, sy - 44), (sx + 10, sy - 22)],
                 EMBER)
    cv.circle(sx - 24, sy - 40, 12, SLATE)
    cv.circle(sx - 4, sy - 52, 15, SLATE)
    cv.circle(sx + 18, sy - 60, 12, SLATE)
    cv.circle(sx + 36, sy - 56, 9, SLATE)
    # drone trails arcing in from the east
    dotted_arc(cv, (860, 160), (760, 120), (sx + 52, sy - 30), CRIMSON)
    dotted_arc(cv, (880, 210), (780, 190), (sx + 58, sy - 8), CRIMSON)
    cv.fill_poly([(856, 156), (872, 160), (856, 164)], BLACK)
    cv.fill_poly([(876, 206), (892, 210), (876, 214)], BLACK)
    cv.text("SPARTA II", sx - 34, sy + 26, 2, NEWS)
    cv.text("DRIFTING INTO FINNISH WATERS", ax + 560, ay + 208, 2, NEWS)

    # ---- lead headline + deck ---------------------------------------
    cv.text_centre("DRONES SET RUSSIAN SHIP ABLAZE", SIZE // 2, 396, 4, BLACK)
    cv.text_centre("IN THE BALTIC", SIZE // 2, 432, 4, BLACK)
    cv.text_centre("FINLAND: THE WAR IS SPILLING OVER", SIZE // 2, 470, 3,
                   CRIMSON)
    deck = ("Two drones hit the sanctioned cargo ship Sparta II in the "
            "Gulf of Finland. The crew was evacuated as the burning "
            "vessel drifted into Finnish waters; Finland says Ukraine "
            "was likely behind the strike.")
    cv.block(deck, 112, 508, 800, 2, BLACK)
    cv.hline(48, 566, SIZE - 96, BLACK)
    cv.hline(48, 570, SIZE - 96, BLACK)

    # ---- story grid --------------------------------------------------
    stories = [
        ("ANTALYA", "COP31 DEADLOCK: FOSSIL-FUEL FIGHT DRAGS TALKS 36 HOURS OVER",
         "The draft deal drops every mention of fossil fuels; the EU and "
         "island nations push back.", CRIMSON, art_globe),
        ("SHENZHEN", "TRUMP, XI AND PUTIN MEET AT APEC; PLEDGE TO PUMP MORE OIL",
         "The three leaders agree in Shenzhen to raise oil production "
         "and refined fuel supply.", DEEPBLUE, art_flags3),
        ("MEXICO", "FBI TOP-10 CARTEL BOSS 'EL CHAPO ISIDRO' ARRESTED",
         "Mexican forces arrest the wanted drug lord in a shoot-out; "
         "footage shows the capture.", MIDNIGHT, art_badge),
        ("GULF", "TANKERS HIT OFF OMAN AS IRAN-US NAVAL TENSIONS ESCALATE",
         "Multiple tankers are hit off the Oman coast as the Gulf "
         "standoff widens.", SEA, art_tanker),
        ("ESTONIA", "ESTONIA TO CLOSE BORDER WITH RUSSIA; MOSCOW CRIES FOUL",
         "Tallinn moves to shut the frontier; Moscow calls it a new "
         "Iron Curtain.", PINE, art_gate),
        ("US SKIES", "AIRLINES WARNED OF POSSIBLE AL-QAEDA-LINKED ATTACKS",
         "US carriers are warned of a possible terror threat ahead of "
         "the Thanksgiving rush.", AMBER, art_plane),
    ]
    gx, gy = 40, 590
    tw, th = 464, 116
    for i, (kicker, head, body, accent, art) in enumerate(stories):
        x = gx + (i % 2) * (tw + 16)
        y = gy + (i // 2) * (th + 12)
        cv.rect(x, y, 6, th, accent)
        cv.text(kicker, x + 16, y + 2, 2, accent)
        art(cv, x + tw - 48, y + 4, accent)
        cv.block(head, x + 16, y + 22, tw - 16 - 56, 2, BLACK)
        cv.block(body, x + 16, y + 64, tw - 16, 2, SLATE)
        cv.hline(x, y + th - 1, tw, CREAM)

    # ---- footer ------------------------------------------------------
    cv.hline(48, 966, SIZE - 96, BLACK)
    foot1 = ("ALSO: ZELENSKY CALLS CRIMEAN BRIDGE STRIKES A FAIR RESPONSE")
    foot2 = ("DENMARK ACCUSES RUSSIA OF ASSASSINATION PLOT - AUSTRALIA "
             "ENDS ENGLAND'S T20 STREAK")
    cv.text_centre(foot1, SIZE // 2, 978, 1, BLACK)
    cv.text_centre(foot2, SIZE // 2, 992, 1, BLACK)
    return cv


def chunk(kind, payload):
    out = struct.pack(">I", len(payload)) + kind + payload
    return out + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def write_png(cv, path):
    raw = b"".join(b"\x00" + bytes(cv.buf[y * SIZE * 3:(y + 1) * SIZE * 3])
                   for y in range(SIZE))
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(png)
    return len(png)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    size = write_png(paint(), os.path.join(out, "entry.png"))
    print(f"wrote entry.png {size} bytes")


if __name__ == "__main__":
    main()
