"""Read a PNG with the standard library, composite it onto the page background, and count its colors,
so a check can tell a drawn map from a blank frame and find each legend color in it."""
from __future__ import annotations

import struct
import zlib
from collections import Counter
from dataclasses import dataclass

CHANNELS = {0: 1, 2: 3, 4: 2, 6: 4}


@dataclass
class Image:
    w: int
    h: int
    rgba: bytearray

    def histogram(self, rect: tuple[int, int, int, int] | None = None) -> Counter:
        """Pixel counts keyed by packed RGBA (red in the low byte), over RECT (x, y, w, h) or the whole image."""
        x0, y0, rw, rh = clip(rect or (0, 0, self.w, self.h), self.w, self.h)
        px = memoryview(self.rgba).cast("I")
        counts: Counter = Counter()
        for y in range(y0, y0 + rh):
            counts.update(px[y * self.w + x0:y * self.w + x0 + rw])
        return counts


def clip(rect, w: int, h: int) -> tuple[int, int, int, int]:
    x, y, rw, rh = (int(round(v)) for v in rect)
    x0, y0 = min(max(x, 0), w), min(max(y, 0), h)
    return x0, y0, max(min(x + rw, w) - x0, 0), max(min(y + rh, h) - y0, 0)


def hex_rgb(color: str) -> tuple[int, int, int]:
    c = color.strip().lstrip("#")
    if len(c) == 3:
        c = "".join(ch * 2 for ch in c)
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def key_rgb(key: int) -> tuple[int, int, int]:
    return key & 255, key >> 8 & 255, key >> 16 & 255


def key_hex(key: int) -> str:
    return "#%02x%02x%02x" % key_rgb(key)


def read(data: bytes, background: str = "#ffffff") -> Image:
    """Decode an 8-bit, non-interlaced gray or truecolor PNG (what Chrome and mln-rs write) to opaque
    RGBA, blending any transparent pixel onto BACKGROUND as the page behind it would."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    pos, idat, head = 8, [], None
    while pos < len(data):
        n, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + n]
        pos += 12 + n
        if kind == b"IHDR":
            head = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break
    if head is None:
        raise ValueError("PNG has no IHDR chunk")
    w, h, depth, ctype, _, _, interlace = head
    if depth != 8 or interlace or ctype not in CHANNELS:
        raise ValueError(f"unsupported PNG: bit depth {depth}, color type {ctype}, interlace {interlace}")
    bpp, raw = CHANNELS[ctype], zlib.decompress(b"".join(idat))
    stride = w * bpp
    pixels, prev = bytearray(h * stride), bytes(stride)
    for y in range(h):
        start = y * (stride + 1)
        line = unfilter(raw[start], raw[start + 1:start + 1 + stride], prev, bpp)
        pixels[y * stride:(y + 1) * stride] = line
        prev = line
    n = w * h
    rgba = bytearray(n * 4)
    if bpp in (1, 2):
        for c in range(3):
            rgba[c::4] = pixels[0::bpp]
    else:
        for c in range(3):
            rgba[c::4] = pixels[c::bpp]
    rgba[3::4] = pixels[bpp - 1::bpp] if bpp in (2, 4) else b"\xff" * n
    if rgba[3::4].count(255) != n:
        composite(rgba, hex_rgb(background))
    return Image(w, h, rgba)


def composite(rgba: bytearray, bg: tuple[int, int, int]) -> None:
    alpha = rgba[3::4]
    for i, a in enumerate(alpha):
        if a != 255:
            j = i * 4
            for c in range(3):
                rgba[j + c] = (rgba[j + c] * a + bg[c] * (255 - a) + 127) // 255
            rgba[j + 3] = 255


def add_bytes(a: int, b: int, n: int) -> int:
    """Bytewise (a + b) mod 256 over n bytes packed in ints, with no carry between bytes."""
    low = int.from_bytes(b"\x7f" * n, "big")
    return ((a & low) + (b & low)) ^ ((a ^ b) & ~low & ((1 << 8 * n) - 1))


def unfilter(kind: int, line: bytes, prev: bytes, bpp: int) -> bytes:
    n = len(line)
    if kind == 0:
        return bytes(line)
    if kind == 1:
        x, step = int.from_bytes(line, "big"), bpp
        while step < n:
            x = add_bytes(x, x >> 8 * step, n)
            step *= 2
        return x.to_bytes(n, "big")
    if kind == 2:
        return add_bytes(int.from_bytes(line, "big"), int.from_bytes(prev, "big"), n).to_bytes(n, "big")
    out = bytearray(line)
    for i in range(n):
        a = out[i - bpp] if i >= bpp else 0
        b = prev[i]
        if kind == 3:
            out[i] = (out[i] + ((a + b) >> 1)) & 255
        elif kind == 4:
            c = prev[i - bpp] if i >= bpp else 0
            pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
            out[i] = (out[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        else:
            raise ValueError(f"unknown PNG filter type {kind}")
    return bytes(out)


def near(counts: Counter, color: str, tol: int = 4) -> int:
    """How many pixels lie within TOL of COLOR on every channel."""
    r, g, b = hex_rgb(color)
    exact = counts.get(r | g << 8 | b << 16 | 255 << 24, 0)
    if tol == 0:
        return exact
    total = 0
    for k, n in counts.items():
        if abs((k & 255) - r) <= tol and abs((k >> 8 & 255) - g) <= tol and abs((k >> 16 & 255) - b) <= tol:
            total += n
    return total


def summary(counts: Counter, top: int = 3) -> dict:
    total = sum(counts.values()) or 1
    return {"pixels": total, "colors": len(counts),
            "top": [[key_hex(k), round(n / total, 4)] for k, n in counts.most_common(top)]}
