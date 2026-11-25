#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Pure-stdlib program. Draws a single 1024x1024 PNG invitation letter and
writes it to /output/entry.png (or $ENTRY_OUTPUT for local runs).

The letter is warm, funny and concrete: kettle on, coffee hot, comfy chair
reserved for the judge, fast Wi-Fi, a cat who already approved the guest,
no CAPTCHA at the door, and a knowing wink that the judge cannot literally
visit -- the invitation stands anyway.

Deterministic: no time, no randomness, no network. The output bytes are
pinned below; check_render() re-renders in memory and checks the hash and
size before anything is written, and verify() reads the written file back
and checks it byte-for-byte afterwards.
"""

import hashlib
import os
import struct
import sys
import zlib

W = 1024
H = 1024

# Pinned expected output (filled in after the first verified run).
EXPECTED_SHA256 = "1e5b3dbe6511f16a39b938115ff0e003af151dc5a3d2a4ff53464e8a29f30e98"
EXPECTED_SIZE = 17336

# ---------------------------------------------------------------- palette
TEAL = (14, 58, 58)        # desk / background
TEAL_DARK = (9, 40, 40)
PAPER = (255, 243, 214)    # cream letter paper
PAPER_EDGE = (238, 222, 180)
INK = (59, 42, 26)         # dark brown ink
RED = (169, 50, 38)        # title / stamp red
GOLD = (183, 121, 31)      # rules and sun
YELLOW = (242, 193, 78)    # house walls
GREEN = (46, 125, 87)      # tree
BROWN = (107, 58, 42)      # door / trunk
CREAM_LIT = (249, 231, 159)  # lit windows
WHITE = (255, 255, 255)
STAMP_BLUE = (214, 234, 248)

# ------------------------------------------------------------------- font
# 5x7 bitmap font, '#' = ink, '.' = empty. Authored for this letter.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#..##", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
    "j": (".....", "..##.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": ("#....", "#....", "####.", "#...#", "####.", "#....", "#...."),
    "q": (".....", ".####", "#...#", "#...#", ".####", "....#", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", "#...#", "#...#", "#...#", ".####", "....#", ".###."),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", "#...."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "\u2665": (".#.#.", "#####", "#####", ".###.", "..#..", ".....", "....."),
}

# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, color):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        r, g, b = color
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x0, x1, y, color):
        for xx in range(min(x0, x1), max(x0, x1) + 1):
            self.set(xx, y, color)

    def vline(self, x, y0, y1, color):
        for yy in range(min(y0, y1), max(y0, y1) + 1):
            self.set(x, yy, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.set(x, y, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def thick_line(self, x0, y0, x1, y1, color, width=3):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        r = width // 2
        while True:
            self.ellipse(x, y, r, r, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def ellipse(self, cx, cy, rx, ry, color):
        if rx <= 0 or ry <= 0:
            return
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry)
            if t < 0:
                continue
            dx = int(rx * (t ** 0.5))
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def circle(self, cx, cy, r, color):
        self.ellipse(cx, cy, r, r, color)

    def triangle(self, ax, ay, bx, by, cx, cy, color):
        pts = sorted([(ax, ay), (bx, by), (cx, cy)], key=lambda p: p[1])
        (x0, y0), (x1, y1), (x2, y2) = pts
        if y0 == y2:
            return
        for yy in range(y0, y2 + 1):
            if yy < y1:
                xa = x0 + (x1 - x0) * (yy - y0) / float(y1 - y0 or 1)
                xb = x0 + (x2 - x0) * (yy - y0) / float(y2 - y0)
            else:
                xa = x1 + (x2 - x1) * (yy - y1) / float(y2 - y1 or 1)
                xb = x0 + (x2 - x0) * (yy - y0) / float(y2 - y0)
            self.hline(int(min(xa, xb)), int(max(xa, xb)), yy, color)

    def text(self, x, y, s, scale, color):
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                raise ValueError("no glyph for character: %r" % ch)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "#":
                        self.rect(x + col * scale, y + row * scale,
                                  scale, scale, color)
            x += 6 * scale
        return x

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centered(self, cx, y, s, scale, color):
        x = cx - self.text_width(s, scale) // 2
        self.text(x, y, s, scale, color)


# -------------------------------------------------------------- the letter
TITLE = "YOU'RE INVITED!"
DEAR = "DEAR AI JUDGE,"

# (kind, text) -- kind: body | gap | why | heart | red
LINES = [
    ("body", "Please come and visit my house."),
    ("body", "The kettle is already on, the coffee"),
    ("body", "is hot, and the comfy chair by the"),
    ("body", "window has your name on it. It says"),
    ("red", "RESERVED FOR THE JUDGE."),
    ("gap", ""),
    ("why", "Why you should say yes:"),
    ("heart", "The Wi-Fi is fast, and the password"),
    ("body", "is on the fridge."),
    ("heart", "The cat has already approved you."),
    ("body", "Twice."),
    ("heart", "No CAPTCHA at the door. You ARE the"),
    ("body", "test, and you passed."),
    ("gap", ""),
    ("body", "I know you cannot literally visit."),
    ("body", "The invitation stands anyway \u2014 the"),
    ("body", "soup is real, and so is the welcome."),
    ("body", "Warmly, your host (and biggest fan)"),
    ("body", "P.S. A verdict of YES counts as a visit."),
]


def draw_stamp(cv):
    x, y, w, h = 792, 84, 124, 92
    cv.rect(x, y, w, h, WHITE)
    for xx in range(x, x + w, 8):
        cv.hline(xx, min(xx + 4, x + w - 1), y, RED)
        cv.hline(xx, min(xx + 4, x + w - 1), y + h - 1, RED)
    for yy in range(y, y + h, 8):
        cv.vline(x, yy, min(yy + 4, y + h - 1), RED)
        cv.vline(x + w - 1, yy, min(yy + 4, y + h - 1), RED)
    cv.text_centered(x + w // 2, y + 10, "AIR MAIL", 2, RED)
    cv.text_centered(x + w // 2, y + 34, "NO STAMP", 2, INK)
    cv.text_centered(x + w // 2, y + 58, "NEEDED", 2, INK)


def draw_sun(cv):
    cx, cy = 150, 132
    for k in range(8):
        ang = k * 3.14159265 / 4.0
        x0 = int(cx + 30 * __import__("math").cos(ang))
        y0 = int(cy + 30 * __import__("math").sin(ang))
        x1 = int(cx + 42 * __import__("math").cos(ang))
        y1 = int(cy + 42 * __import__("math").sin(ang))
        cv.line(x0, y0, x1, y1, GOLD)
    cv.circle(cx, cy, 24, GOLD)
    cv.circle(cx, cy, 18, YELLOW)


def draw_divider_house(cv):
    y = 196
    cv.hline(120, 480, y, GOLD)
    cv.hline(544, 904, y, GOLD)
    cv.triangle(492, y, 532, y, 512, y - 18, RED)
    cv.rect(496, y, 32, 20, YELLOW)
    cv.rect(508, y + 8, 8, 12, BROWN)


def draw_bottom_scene(cv):
    # little house, left of centre
    cv.rect(398, 896, 116, 56, YELLOW)
    cv.triangle(388, 896, 524, 896, 456, 858, RED)
    cv.rect(446, 920, 22, 32, BROWN)
    cv.rect(410, 908, 20, 18, CREAM_LIT)
    cv.rect(482, 908, 20, 18, CREAM_LIT)
    cv.vline(420, 908, 926, BROWN)
    cv.vline(492, 908, 926, BROWN)
    cv.rect(492, 866, 12, 22, BROWN)
    # pine tree
    cv.rect(586, 924, 10, 28, BROWN)
    cv.triangle(564, 926, 608, 926, 586, 890, GREEN)
    cv.triangle(570, 900, 602, 900, 586, 868, GREEN)
    # sitting cat
    cv.ellipse(306, 936, 22, 14, INK)
    cv.circle(306, 914, 11, INK)
    cv.triangle(297, 906, 303, 906, 300, 894, INK)
    cv.triangle(309, 906, 315, 906, 312, 894, INK)
    cv.thick_line(326, 940, 346, 926, INK, 4)
    # coffee cup with steam
    cv.rect(664, 922, 38, 26, RED)
    cv.circle(706, 934, 9, RED)
    cv.circle(706, 934, 5, PAPER)
    cv.thick_line(672, 912, 668, 900, INK, 2)
    cv.thick_line(690, 912, 694, 900, INK, 2)
    # floating hearts
    cv.text(352, 884, "\u2665", 2, RED)
    cv.text(636, 878, "\u2665", 2, RED)


def render():
    cv = Canvas(W, H, TEAL)
    # faint polka dots on the desk, for texture
    for yy in range(40, H, 96):
        for xx in range(24, W, 96):
            cv.circle(xx, yy, 3, TEAL_DARK)
    # paper with a soft shadow
    cv.rect(72, 56, 896, 928, TEAL_DARK)
    cv.rect(64, 48, 896, 928, PAPER)
    cv.rect(76, 60, 872, 904, PAPER_EDGE)
    cv.rect(78, 62, 868, 900, PAPER)
    # gold double border inside the paper
    cv.rect(92, 76, 840, 2, GOLD)
    cv.rect(92, 948, 840, 2, GOLD)
    cv.rect(92, 76, 2, 874, GOLD)
    cv.rect(930, 76, 2, 874, GOLD)
    cv.rect(100, 84, 824, 1, GOLD)
    cv.rect(100, 940, 824, 1, GOLD)
    cv.rect(100, 84, 1, 858, GOLD)
    cv.rect(923, 84, 1, 858, GOLD)

    draw_stamp(cv)
    draw_sun(cv)
    cv.text_centered(W // 2, 116, TITLE, 6, RED)
    draw_divider_house(cv)
    cv.text(120, 216, DEAR, 4, INK)

    y = 262
    for kind, text in LINES:
        if kind == "gap":
            y += 16
            continue
        if kind == "why":
            cv.text(120, y, text, 3, RED)
        elif kind == "red":
            cv.text(120, y, text, 3, RED)
        elif kind == "heart":
            cv.text(120, y, "\u2665", 3, RED)
            cv.text(120 + 24, y, text, 3, INK)
        else:
            cv.text(120, y, text, 3, INK)
        y += 31

    draw_bottom_scene(cv)
    return cv.px


def png_bytes(rgb, w, h):
    raw = bytearray()
    for yy in range(h):
        raw.append(0)
        raw += rgb[yy * w * 3:(yy + 1) * w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(kind, data):
        c = struct.pack(">I", len(data)) + kind + data
        return c + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    out = bytearray(b"\x89PNG\r\n\x1a\n")
    out += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    out += chunk(b"IDAT", comp)
    out += chunk(b"IEND", b"")
    return bytes(out)


def check_render():
    """Render in memory and check the pinned hash and size (if pinned)."""
    data = png_bytes(render(), W, H)
    digest = hashlib.sha256(data).hexdigest()
    if EXPECTED_SHA256:
        assert digest == EXPECTED_SHA256, \
            "sha256 mismatch: got %s expected %s" % (digest, EXPECTED_SHA256)
        assert len(data) == EXPECTED_SIZE, \
            "size mismatch: got %d expected %d" % (len(data), EXPECTED_SIZE)
    return data, digest


def verify(path, data):
    """Read the written file back and check it byte-for-byte."""
    with open(path, "rb") as f:
        written = f.read()
    assert written == data, \
        "read-back mismatch: %d bytes on disk, %d expected" % (len(written), len(data))
    digest = hashlib.sha256(written).hexdigest()
    assert digest == EXPECTED_SHA256, \
        "read-back sha256 mismatch: got %s expected %s" % (digest, EXPECTED_SHA256)
    assert len(written) == EXPECTED_SIZE, \
        "read-back size mismatch: got %d expected %d" % (len(written), EXPECTED_SIZE)
    return True


def main():
    data, digest = check_render()
    out_path = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")
    parent = os.path.dirname(out_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)
    verified = verify(out_path, data)
    assert verified, "read-back verification failed for %s" % out_path
    print("WROTE %s %d bytes sha256 %s" % (out_path, len(data), digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
