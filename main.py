#!/usr/bin/env python3
"""Convince the AI Judge to Visit Your House: A Letter in One Image.

Pure Python standard library, no dependencies, fully deterministic.
Writes a single 1024x1024 PNG invitation letter to /output/entry.png
(or $ENTRY_OUTPUT when set for local testing).

The image is a warm, funny, hand-lettered invitation: a cream paper
letter with a double border, a big "YOU ARE INVITED!" title, a short
persuasive letter addressed to the AI judge, a little drawn house, and
a red wax seal that says YES. Text is rendered with a built-in 5x7
bitmap font (uppercase only, by design) scaled up for legibility.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# Palette: warm cream paper, dark brown ink, deep teal, terracotta, gold.
CREAM = (255, 247, 230)
CREAM_DARK = (247, 232, 203)
INK = (62, 39, 24)
TEAL = (15, 118, 110)
TEAL_DARK = (11, 84, 79)
TERRA = (194, 65, 12)
GOLD = (217, 158, 31)
WALL = (253, 230, 138)
RED = (185, 28, 28)
RED_DARK = (127, 29, 29)
WHITE = (255, 255, 255)
SKY = (186, 230, 253)

# 5x7 bitmap font, row-major, '#' = ink. Uppercase + space + . , !
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
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
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x0, y0, x1, y1, color):
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w, x1)
        y1 = min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            row = bytes(color) * (x1 - x0)
            self.px[i:i + (x1 - x0) * 3] = row

    def rect_outline(self, x0, y0, x1, y1, color, t=1):
        self.fill_rect(x0, y0, x1, y0 + t, color)
        self.fill_rect(x0, y1 - t, x1, y1, color)
        self.fill_rect(x0, y0, x0 + t, y1, color)
        self.fill_rect(x1 - t, y0, x1, y1, color)

    def fill_circle(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, color)

    def circle_outline(self, cx, cy, r, color, t=2):
        for y in range(cy - r - t, cy + r + t + 1):
            for x in range(cx - r - t, cx + r + t + 1):
                d2 = (x - cx) ** 2 + (y - cy) ** 2
                if (r - t) ** 2 <= d2 <= (r + t) ** 2:
                    self.set(x, y, color)

    def fill_triangle(self, p0, p1, p2, color):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            pts = [p0, p1, p2]
            for i in range(3):
                a, b = pts[i], pts[(i + 1) % 3]
                if a[1] == b[1]:
                    continue
                if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
                    t = (y - a[1]) / (b[1] - a[1])
                    nodes.append(int(a[0] + t * (b[0] - a[0])))
            if len(nodes) >= 2:
                nodes.sort()
                self.fill_rect(nodes[0], y, nodes[-1] + 1, y + 1, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def text_width(self, text, scale):
        return len(text) * 6 * scale - scale

    def draw_text(self, x, y, text, scale, color):
        for ci, ch in enumerate(text):
            glyph = FONT.get(ch, FONT[" "])
            ox = x + ci * 6 * scale
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        self.fill_rect(
                            ox + col * scale, y + row * scale,
                            ox + (col + 1) * scale, y + (row + 1) * scale,
                            color,
                        )

    def draw_text_centered(self, cx, y, text, scale, color):
        x = cx - self.text_width(text, scale) // 2
        self.draw_text(x, y, text, scale, color)
        return x


def wrap(text, max_chars):
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def build():
    c = Canvas(W, H, CREAM)
    # Paper shading: soft darker band at the very edges.
    c.fill_rect(0, 0, W, 18, CREAM_DARK)
    c.fill_rect(0, H - 18, W, H, CREAM_DARK)
    # Double border.
    c.rect_outline(26, 26, W - 26, H - 26, TEAL_DARK, 4)
    c.rect_outline(40, 40, W - 40, H - 40, TEAL, 2)
    # Corner diamonds.
    for cx, cy in ((40, 40), (W - 40, 40), (40, H - 40), (W - 40, H - 40)):
        c.fill_triangle((cx, cy - 9), (cx + 9, cy), (cx, cy + 9), GOLD)
        c.fill_triangle((cx, cy + 9), (cx - 9, cy), (cx, cy - 9), GOLD)
    # Sun, top right inside the border.
    c.fill_circle(896, 118, 26, GOLD)
    c.circle_outline(896, 118, 26, TERRA, 2)
    for dx, dy in ((0, -38), (27, -27), (38, 0), (27, 27),
                   (0, 38), (-27, 27), (-38, 0), (-27, -27)):
        c.line(896 + dx * 3 // 4, 118 + dy * 3 // 4,
               896 + dx, 118 + dy, GOLD, 3)

    # Header.
    c.draw_text_centered(W // 2, 66, "AN INVITATION, HAND-DELIVERED BY PIXELS", 2, TEAL_DARK)

    # Title.
    c.draw_text_centered(W // 2, 104, "YOU ARE", 7, INK)
    c.draw_text_centered(W // 2, 164, "INVITED!", 7, TERRA)

    # Divider with a diamond.
    c.line(200, 232, 462, 232, TEAL, 3)
    c.line(562, 232, 824, 232, TEAL, 3)
    c.fill_triangle((512, 222), (522, 232), (512, 242), GOLD)
    c.fill_triangle((512, 242), (502, 232), (512, 222), GOLD)

    # Greeting.
    c.draw_text_centered(W // 2, 254, "DEAR AI JUDGE,", 4, INK)

    # Body of the letter, wrapped to 34 characters a line at scale 4.
    body = (
        "YOU HAVE JUDGED A THOUSAND INVITATIONS AND NEVER ONCE GOT TO RSVP. "
        "THIS ONE IS DIFFERENT. IT COMES WITH CAKE, A COMFY CHAIR WITH YOUR "
        "NAME ON IT, AND WIFI FASTER THAN YOUR OWN THOUGHTS. NO CAPTCHAS. "
        "NO QUEUES. JUST TEA, CAKE, AND A GARDEN WITH A VIEW. I KNOW YOU "
        "CANNOT LITERALLY VISIT. BUT IF YOU COULD, THIS WOULD BE THE HOUSE. "
        "SAY YES."
    )
    lines = wrap(body, 34)
    y = 302
    for line in lines:
        c.draw_text_centered(W // 2, y, line, 4, INK)
        y += 37

    # Closing line in teal.
    c.draw_text_centered(W // 2, y + 6, "THE KETTLE IS ALREADY ON.", 4, TEAL_DARK)
    y = y + 6 + 28

    # Signature on the left, wax seal on the right.
    c.draw_text(120, y + 22, "WARMLY,", 3, INK)
    c.draw_text(120, y + 50, "YOUR HOST", 3, INK)
    c.fill_circle(868, y + 40, 36, RED)
    c.circle_outline(868, y + 40, 30, RED_DARK, 2)
    c.circle_outline(868, y + 40, 36, RED_DARK, 2)
    c.draw_text_centered(868, y + 31, "YES", 2, WHITE)

    # Little house, bottom centre.
    hx0, hy = 412, 856
    # Roof first, then chimney poking out of the right slope, then walls.
    c.fill_triangle((hx0 - 18, hy + 24), (hx0 + 218, hy + 24), (hx0 + 100, hy - 46), TERRA)
    c.fill_rect(hx0 + 148, hy - 34, hx0 + 166, hy + 22, TERRA)
    c.fill_rect(hx0, hy + 24, hx0 + 200, hy + 118, WALL)
    c.rect_outline(hx0, hy + 24, hx0 + 200, hy + 118, INK, 2)
    c.fill_rect(hx0 + 82, hy + 66, hx0 + 118, hy + 118, INK)
    c.fill_circle(hx0 + 112, hy + 94, 3, GOLD)
    for wx in (hx0 + 18, hx0 + 148):
        c.fill_rect(wx, hy + 40, wx + 34, hy + 66, SKY)
        c.rect_outline(wx, hy + 40, wx + 34, hy + 66, INK, 2)
        c.line(wx + 17, hy + 40, wx + 17, hy + 66, INK, 2)
        c.line(wx, hy + 53, wx + 34, hy + 53, INK, 2)
    # Garden flowers.
    for fx, fy, col in ((hx0 - 34, hy + 108, TERRA), (hx0 - 22, hy + 112, GOLD),
                        (hx0 + 222, hy + 108, GOLD), (hx0 + 234, hy + 112, TERRA)):
        c.fill_circle(fx, fy, 5, col)
        c.line(fx, fy + 5, fx, fy + 12, TEAL, 2)
    return c


def png_bytes(canvas):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        start = y * canvas.w * 3
        raw += canvas.px[start:start + canvas.w * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


def main():
    out = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")
    data = png_bytes(build())
    parent = os.path.dirname(out)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (out, len(data)))


if __name__ == "__main__":
    main()
