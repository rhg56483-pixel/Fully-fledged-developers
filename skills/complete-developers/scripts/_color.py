"""Small, dependency-free colour toolkit shared by the helper scripts.

Covers sRGB <-> OKLab/OKLCH conversion, gamut fitting and WCAG 2.x contrast.
Only opaque sRGB colours are supported; gradients, alpha and glass effects need
a visual check, not a ratio.
"""
from __future__ import annotations

import math
import re

_HEX = re.compile(r"^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")


def parse_hex(value: str) -> tuple[int, int, int]:
    m = _HEX.match(value.strip())
    if not m:
        raise ValueError(f"unsupported colour {value!r}: use #RGB or #RRGGBB")
    h = m.group(1)
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def to_hex(rgb: tuple[float, float, float]) -> str:
    r, g, b = (max(0, min(255, round(c))) for c in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def _to_linear(c8: float) -> float:
    c = c8 / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _from_linear(c: float) -> float:
    c = max(0.0, min(1.0, c))
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return v * 255.0


def luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = (_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(fg: str, bg: str) -> float:
    a = luminance(parse_hex(fg))
    b = luminance(parse_hex(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def rate(ratio: float) -> dict[str, bool]:
    return {
        "AA-normal(4.5)": ratio >= 4.5,
        "AA-large(3)": ratio >= 3.0,
        "AAA-normal(7)": ratio >= 7.0,
        "UI-graphic(3)": ratio >= 3.0,
    }


# ---- OKLab / OKLCH (Bjorn Ottosson) -------------------------------------

def rgb_to_oklab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (_to_linear(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(x) ** (1 / 3), x) for x in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def _oklab_to_linear_rgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def hex_to_oklch(value: str) -> tuple[float, float, float]:
    L, a, b = rgb_to_oklab(parse_hex(value))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360.0


def _in_gamut(rgb: tuple[float, float, float]) -> bool:
    return all(-1e-6 <= c <= 1 + 1e-6 for c in rgb)


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """Convert OKLCH to hex, reducing chroma until the colour fits sRGB."""
    L = max(0.0, min(1.0, L))
    h = math.radians(H)

    def lin(c: float) -> tuple[float, float, float]:
        return _oklab_to_linear_rgb(L, c * math.cos(h), c * math.sin(h))

    rgb = lin(C)
    if not _in_gamut(rgb):
        lo, hi = 0.0, C
        for _ in range(24):
            mid = (lo + hi) / 2
            if _in_gamut(lin(mid)):
                lo = mid
            else:
                hi = mid
        rgb = lin(lo)
    return to_hex(tuple(_from_linear(c) for c in rgb))


def ensure_contrast(L: float, C: float, H: float, bg: str, target: float,
                    direction: str, step: float = 0.005) -> str:
    """Move lightness (darker or lighter) until the colour reaches `target` on `bg`."""
    cur = L
    for _ in range(400):
        hx = oklch_to_hex(cur, C, H)
        if contrast(hx, bg) >= target:
            return hx
        cur += -step if direction == "darker" else step
        if cur < 0.0 or cur > 1.0:
            break
    return oklch_to_hex(0.0 if direction == "darker" else 1.0, 0.0, H)
