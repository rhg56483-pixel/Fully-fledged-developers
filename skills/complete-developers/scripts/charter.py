#!/usr/bin/env python3
"""Generate a contrast-checked design charter (tokens + principles) in one call.

Why: choosing palette, type, space and motion by hand costs many tokens and
often produces generic or low-contrast results. This script derives a coherent
set from an archetype, a seed colour and four dials, and verifies the text
pairs against WCAG before printing.

Examples
  python charter.py --list
  python charter.py --archetype food-hospitality --rtl --name "Crater"
  python charter.py --archetype fintech-trust --seed "#0F6B5C" --dials boldness=2,density=4
  python charter.py --archetype saas-tool --format css > tokens.css
  python charter.py --table              # markdown archetype table (used by docs)

Dials (1-5): boldness (quiet..loud), density (airy..compact),
             motion (still..lively), warmth (cool/precise..warm/human).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _color import contrast, ensure_contrast, hex_to_oklch, oklch_to_hex  # noqa: E402

DIAL_NAMES = ("boldness", "density", "motion", "warmth")

# id: (label, label_ar, best for, mood, seed, (b, d, m, w),
#      latin display, latin body, arabic display, arabic body, signature move, avoid)
ARCHETYPES: dict[str, dict] = {
    "food-hospitality": dict(
        label="Food & hospitality", label_ar="مطاعم وضيافة",
        best="restaurants, cafes, bakeries", mood="appetising, warm, tactile",
        seed="#B4532A", dials=(3, 2, 2, 5),
        ld="Fraunces", lb="DM Sans", ad="El Messiri", ab="Tajawal",
        move="a menu that reads like a printed card, prices aligned with leader dots",
        avoid="stock-photo mosaics, neon, cold greys"),
    "luxury-retail": dict(
        label="Luxury retail", label_ar="رفاهية وتجزئة",
        best="perfume, oud, jewellery, fashion", mood="quiet, precious, unhurried",
        seed="#7A5C2E", dials=(2, 1, 2, 4),
        ld="Cormorant Garamond", lb="Manrope", ad="Amiri", ab="IBM Plex Sans Arabic",
        move="one oversized product on a calm ground with hairline rules",
        avoid="discount banners, loud gradients, crowded grids"),
    "fintech-trust": dict(
        label="Fintech & trust", label_ar="مالية وثقة",
        best="payments, banking, invoicing", mood="precise, calm, credible",
        seed="#0F6B5C", dials=(2, 4, 2, 2),
        ld="Sora", lb="IBM Plex Sans", ad="IBM Plex Sans Arabic", ab="IBM Plex Sans Arabic",
        move="numbers as the hero, tabular figures, generous alignment",
        avoid="handshake stock photos, crypto neon, vague claims"),
    "saas-tool": dict(
        label="SaaS & productivity", label_ar="أدوات وإنتاجية",
        best="dashboards, productivity, B2B tools", mood="clear, efficient, friendly",
        seed="#3B5BDB", dials=(3, 4, 3, 3),
        ld="Bricolage Grotesque", lb="Plus Jakarta Sans", ad="Readex Pro", ab="IBM Plex Sans Arabic",
        move="a real fragment of the product UI in the hero, not an abstract blob",
        avoid="three identical feature cards, purple glow blobs, fake logos"),
    "editorial-news": dict(
        label="Editorial & reading", label_ar="تحرير وقراءة",
        best="blogs, magazines, documentation", mood="authoritative, literate, calm",
        seed="#B3261E", dials=(3, 3, 1, 3),
        ld="Newsreader", lb="Newsreader", ad="Amiri", ab="Noto Naskh Arabic",
        move="strong typographic hierarchy on a column grid with a pull quote",
        avoid="endless card feeds, tiny grey text, ad-style banners"),
    "portfolio-creative": dict(
        label="Portfolio & studio", label_ar="معرض أعمال واستوديو",
        best="personal sites, studios, case studies", mood="confident, personal, expressive",
        seed="#E4572E", dials=(5, 2, 4, 3),
        ld="Syne", lb="Manrope", ad="Changa", ab="Tajawal",
        move="case studies as large image sequences with short captions",
        avoid="template grids, generic skill bars, stock icons"),
    "education-kids": dict(
        label="Learning & kids", label_ar="تعليم وأطفال",
        best="children's learning, family apps", mood="playful, safe, big",
        seed="#F08A00", dials=(4, 1, 4, 5),
        ld="Baloo 2", lb="Nunito", ad="Baloo Bhaijaan 2", ab="Almarai",
        move="large tactile shapes and one friendly illustrated guide",
        avoid="small text, dense menus, harsh reds"),
    "health-calm": dict(
        label="Health & calm", label_ar="صحة وهدوء",
        best="clinics, wellness, mindfulness", mood="reassuring, soft, human",
        seed="#2F7F6F", dials=(1, 1, 1, 4),
        ld="DM Serif Display", lb="Nunito Sans", ad="Almarai", ab="IBM Plex Sans Arabic",
        move="generous space and one human-scale photograph",
        avoid="clinical stock imagery, alarming reds used as decoration"),
    "real-estate": dict(
        label="Real estate", label_ar="عقارات",
        best="property listings, developers", mood="solid, aspirational, clear",
        seed="#1E3A5F", dials=(3, 3, 2, 3),
        ld="Playfair Display", lb="Manrope", ad="Cairo", ab="Noto Naskh Arabic",
        move="full-bleed property imagery with a floor-plan overlay",
        avoid="cluttered filters first, tiny photos, loud badges"),
    "game-neon-arcade": dict(
        label="Game: neon arcade", label_ar="ألعاب نيون",
        best="action games, esports, HUDs", mood="electric, fast, nocturnal",
        seed="#00C896", dials=(5, 3, 5, 1),
        ld="Space Grotesk", lb="JetBrains Mono", ad="Changa", ab="Tajawal",
        move="HUD-style framing with one scanline texture used once",
        avoid="glow on everything, low-contrast text on glow"),
    "game-cozy-cartoon": dict(
        label="Game: cozy cartoon", label_ar="ألعاب كرتونية",
        best="casual games, Roblox-style menus", mood="chunky, friendly, bouncy",
        seed="#FF6B5A", dials=(4, 2, 5, 5),
        ld="Lilita One", lb="Nunito", ad="Baloo Bhaijaan 2", ab="Almarai",
        move="thick outlines and chunky buttons with a real pressed state",
        avoid="thin type, hairline borders, flat grey panels"),
    "heritage-arabic": dict(
        label="Arabic heritage", label_ar="تراث وهوية عربية",
        best="cultural events, Ramadan, Gulf identity", mood="dignified, rhythmic, warm",
        seed="#0E5F4B", dials=(3, 2, 2, 4),
        ld="Cormorant Garamond", lb="Manrope", ad="Amiri", ab="Noto Naskh Arabic",
        move="a geometric pattern used as structure (frame, divider, 6% ground), not clip-art",
        avoid="crescent-and-lantern clip-art, gold gradient text"),
    "tech-developer": dict(
        label="Developer tools", label_ar="أدوات المطورين",
        best="docs, CLIs, open-source projects", mood="exact, calm, technical",
        seed="#00A37A", dials=(2, 5, 2, 2),
        ld="Space Grotesk", lb="IBM Plex Sans", ad="IBM Plex Sans Arabic", ab="IBM Plex Sans Arabic",
        move="a real terminal or code sample with copy-to-clipboard in the hero",
        avoid="matrix-green hacker cliches, decorative code that does not run"),
    "event-invite": dict(
        label="Event & invitation", label_ar="مناسبات ودعوات",
        best="weddings, launches, invitations", mood="ceremonial, intimate, elegant",
        seed="#8E4A6B", dials=(3, 1, 3, 4),
        ld="Instrument Serif", lb="Jost", ad="Reem Kufi", ab="Amiri",
        move="the date and names set as a typographic centrepiece",
        avoid="busy backgrounds, more than two ornaments"),
    "nonprofit-community": dict(
        label="Community & non-profit", label_ar="مجتمع وعمل خيري",
        best="charities, mosques, associations", mood="sincere, steady, open",
        seed="#1D6F8C", dials=(2, 2, 2, 4),
        ld="Fraunces", lb="Source Sans 3", ad="Noto Kufi Arabic", ab="Tajawal",
        move="real people and stories first, one steady donation action",
        avoid="guilt imagery, stock smiles, five competing buttons"),
}

# Google Fonts weight sets that are safe (families with fewer weights).
WEIGHTS = {
    "Tajawal": "400;500;700", "Almarai": "400;700;800", "Amiri": "400;700",
    "DM Serif Display": "400", "Instrument Serif": "400", "Lilita One": "400",
}
DEFAULT_WEIGHTS = "400;500;600;700"
MONO = "JetBrains Mono"

RADIUS = {1: 2, 2: 4, 3: 8, 4: 12, 5: 16}
RATIO = {1: 1.333, 2: 1.3, 3: 1.25, 4: 1.2, 5: 1.15}
MOTION = {1: (80, 120, 160), 2: (120, 180, 240), 3: (150, 220, 320),
          4: (180, 280, 420), 5: (200, 320, 520)}


def parse_dials(text: str | None, base: tuple[int, int, int, int]) -> dict[str, int]:
    out = dict(zip(DIAL_NAMES, base))
    if not text:
        return out
    for part in text.split(","):
        if not part.strip():
            continue
        key, _, val = part.partition("=")
        key = key.strip().lower()
        if key not in out:
            raise SystemExit(f"unknown dial {key!r}; choose from {', '.join(DIAL_NAMES)}")
        try:
            n = int(val)
        except ValueError:
            raise SystemExit(f"dial {key} needs an integer 1-5, got {val!r}")
        if not 1 <= n <= 5:
            raise SystemExit(f"dial {key} must be between 1 and 5")
        out[key] = n
    return out


def _neutral_hue(seed_h: float, warmth: int) -> float:
    if warmth <= 2:
        return 250.0
    if warmth == 3:
        return seed_h
    return 75.0


def _pair(fg: str, bg: str) -> dict:
    return {"fg": fg, "bg": bg, "ratio": round(contrast(fg, bg), 2)}


def build_tokens(arch_id: str, seed: str | None, dials: dict[str, int], rtl: bool) -> dict:
    a = ARCHETYPES[arch_id]
    seed = seed or a["seed"]
    sL, sC, sH = hex_to_oklch(seed)
    sC = max(sC, 0.04)
    nh = _neutral_hue(sH, dials["warmth"])
    nc = 0.004 + 0.004 * dials["warmth"]
    boldness = dials["boldness"]

    accent_shift = 30 if boldness <= 2 else (150 if boldness == 3 else 180)
    ah = (sH + accent_shift) % 360

    def theme(dark: bool) -> dict:
        if dark:
            bg = oklch_to_hex(0.165, nc, nh)
            surface = oklch_to_hex(0.205, nc, nh)
            surface2 = oklch_to_hex(0.245, nc, nh)
            border = oklch_to_hex(0.31, nc, nh)
            text = ensure_contrast(0.95, nc, nh, bg, 12.0, "lighter")
            muted = ensure_contrast(0.72, nc, nh, bg, 5.0, "lighter")
            pL = max(sL, 0.70)
            primary = ensure_contrast(pL, sC, sH, bg, 4.5, "lighter")
            accent = ensure_contrast(0.74, sC * 0.9, ah, bg, 4.5, "lighter")
            tone = "lighter"
        else:
            bg = oklch_to_hex(0.985, nc, nh)
            surface = oklch_to_hex(0.997, nc * 0.5, nh)
            surface2 = oklch_to_hex(0.962, nc, nh)
            border = oklch_to_hex(0.90, nc, nh)
            text = ensure_contrast(0.22, nc * 1.5, nh, bg, 12.0, "darker")
            muted = ensure_contrast(0.50, nc, nh, surface2, 4.5, "darker")
            pL = min(max(sL, 0.42), 0.62)
            primary = oklch_to_hex(pL, sC, sH)
            accent = ensure_contrast(0.60, sC * 0.9, ah, bg, 3.0, "darker")
            tone = "darker"
        white, ink = "#FFFFFF", oklch_to_hex(0.18, nc, nh)
        if contrast(white, primary) >= 4.5:
            on_primary = white
        elif contrast(ink, primary) >= 4.5:
            on_primary = ink
        else:
            primary = ensure_contrast(oklch_to_hex_L(primary), sC, sH, white, 4.5, "darker") \
                if not dark else ensure_contrast(oklch_to_hex_L(primary), sC, sH, ink, 4.5, "lighter")
            on_primary = white if not dark else ink
        focus = ensure_contrast(0.55 if not dark else 0.78, sC, sH, bg, 3.0, tone)
        status = {}
        for name, hue in (("success", 150.0), ("warning", 75.0), ("danger", 27.0)):
            c = 0.14 if name != "warning" else 0.13
            status[name] = ensure_contrast(0.55 if not dark else 0.78, c, hue, bg, 4.5, tone)
        return {
            "bg": bg, "surface": surface, "surface-2": surface2, "border": border,
            "text": text, "text-muted": muted, "primary": primary, "on-primary": on_primary,
            "accent": accent, "focus": focus, **status,
        }

    light, dark = theme(False), theme(True)

    def checks(t: dict) -> dict:
        return {
            "text on bg": _pair(t["text"], t["bg"]),
            "text on surface": _pair(t["text"], t["surface"]),
            "muted on bg": _pair(t["text-muted"], t["bg"]),
            "muted on surface-2": _pair(t["text-muted"], t["surface-2"]),
            "on-primary on primary": _pair(t["on-primary"], t["primary"]),
            "accent on bg (graphic)": _pair(t["accent"], t["bg"]),
            "focus on bg (graphic)": _pair(t["focus"], t["bg"]),
            "danger on bg": _pair(t["danger"], t["bg"]),
        }

    ratio = RATIO[dials["density"]] + (0.067 if boldness >= 4 else 0.0)
    base = 1.1 if rtl else 1.0
    steps = {f"step{n:+d}".replace("+", "p").replace("-", "m"): round(base * ratio ** n, 3)
             for n in range(-1, 7)}
    r_md = RADIUS[dials["warmth"]] if boldness < 5 or dials["warmth"] > 2 else 0
    dur = MOTION[dials["motion"]]
    airy = 6 - dials["density"]
    section = [24 + airy * 12, 48 + airy * 24]

    def stack(names: list[str], generic: str) -> str:
        return ", ".join(f'"{n}"' for n in names) + f", {generic}"

    display = a["ad"] if rtl else a["ld"]
    body = a["ab"] if rtl else a["lb"]
    secondary_d = a["ld"] if rtl else a["ad"]
    secondary_b = a["lb"] if rtl else a["ab"]
    fonts = {
        "display": stack([display, secondary_d], "serif" if display in SERIF else "sans-serif"),
        "body": stack([body, secondary_b], "system-ui, sans-serif"),
        "mono": f'"{MONO}", ui-monospace, monospace',
    }
    families = []
    for f in (a["ld"], a["lb"], a["ad"], a["ab"]):
        if f not in families:
            families.append(f)
    return {
        "archetype": arch_id, "label": a["label"], "seed": seed.upper(), "dials": dials,
        "rtl": rtl, "light": light, "dark": dark,
        "contrast": {"light": checks(light), "dark": checks(dark)},
        "type": {
            "fonts": fonts, "families": families, "ratio": round(ratio, 3), "steps_rem": steps,
            "line_height": {"body": 1.8 if rtl else 1.55, "heading": 1.4 if rtl else 1.15},
            "measure": "58ch" if rtl else "66ch",
            "letter_spacing": "0 (never track Arabic)" if rtl else "-0.01em on large headings only",
        },
        "space": {"base_px": 4, "scale_px": [4, 8, 12, 16, 24, 32, 48, 64, 96, 128],
                  "section_px": section},
        "radius_px": {"sm": r_md // 2, "md": r_md, "lg": r_md * 2, "pill": 999},
        "motion_ms": {"fast": dur[0], "base": dur[1], "slow": dur[2],
                      "ease": "cubic-bezier(.2,.7,.2,1)"},
        "move": a["move"], "avoid": a["avoid"], "mood": a["mood"],
    }


SERIF = {"Fraunces", "Cormorant Garamond", "Newsreader", "Playfair Display", "DM Serif Display",
         "Instrument Serif", "Amiri", "Noto Naskh Arabic"}


def oklch_to_hex_L(hex_value: str) -> float:
    return hex_to_oklch(hex_value)[0]


def fonts_url(families: list[str]) -> str:
    parts = []
    for f in families:
        w = WEIGHTS.get(f, DEFAULT_WEIGHTS)
        name = f.replace(" ", "+")
        parts.append(f"family={name}" if w == "400" else f"family={name}:wght@{w}")
    return "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"


def render_css(t: dict) -> str:
    def block(theme: dict) -> str:
        return "\n".join(f"  --{k}: {v};" for k, v in theme.items())

    r, s = t["radius_px"], t["space"]
    steps = "\n".join(f"  --{k.replace('step', 'text-')}: {v}rem;" for k, v in t["type"]["steps_rem"].items())
    m = t["motion_ms"]
    sel = ':root[data-theme="dark"]'
    out = [
        ":root {", block(t["light"]),
        f'  --font-display: {t["type"]["fonts"]["display"]};',
        f'  --font-body: {t["type"]["fonts"]["body"]};',
        f'  --font-mono: {t["type"]["fonts"]["mono"]};',
        steps,
        f'  --leading-body: {t["type"]["line_height"]["body"]};',
        f'  --leading-heading: {t["type"]["line_height"]["heading"]};',
        f'  --measure: {t["type"]["measure"]};',
        f'  --radius-sm: {r["sm"]}px; --radius-md: {r["md"]}px; --radius-lg: {r["lg"]}px;',
        f'  --space-section: clamp({s["section_px"][0]}px, 8vw, {s["section_px"][1]}px);',
        f'  --dur-fast: {m["fast"]}ms; --dur-base: {m["base"]}ms; --dur-slow: {m["slow"]}ms;',
        f'  --ease: {m["ease"]};',
        "  color-scheme: light dark;", "}",
        "@media (prefers-color-scheme: dark) {", "  :root:not([data-theme=\"light\"]) {",
        block(t["dark"]).replace("\n  ", "\n    ").replace("  --", "    --", 1), "  }", "}",
        f"{sel} {{", block(t["dark"]), "}",
        "@media (prefers-reduced-motion: reduce) {",
        "  *, *::before, *::after { animation-duration: .01ms !important; "
        "transition-duration: .01ms !important; scroll-behavior: auto !important; }", "}",
    ]
    if t["rtl"]:
        out.append("html[dir=\"rtl\"] body { line-height: var(--leading-body); letter-spacing: 0; }")
    return "\n".join(out) + "\n"


def render_md(t: dict, name: str | None) -> str:
    title = name or "Project"
    d = t["dials"]
    lines = [
        f"# Design charter: {title}",
        "",
        f"Archetype **{t['label']}** · mood: {t['mood']} · seed `{t['seed']}` · "
        f"dials boldness {d['boldness']}, density {d['density']}, motion {d['motion']}, "
        f"warmth {d['warmth']} · {'RTL (Arabic first)' if t['rtl'] else 'LTR'}",
        "",
        "## Principles",
        f"- **Memorable move:** {t['move']}.",
        f"- **Avoid:** {t['avoid']}.",
        "- One voice for action (primary). Hierarchy by size, weight and space before borders.",
        "- Spend boldness in one place; keep everything else quiet and consistent.",
        "",
        "## Colour (contrast verified on opaque colours)",
        "| Token | Light | Dark |", "|---|---|---|",
    ]
    for k in t["light"]:
        lines.append(f"| {k} | `{t['light'][k]}` | `{t['dark'][k]}` |")
    lines += ["", "Key pairs (ratio light / dark):"]
    for k in t["contrast"]["light"]:
        lines.append(f"- {k}: {t['contrast']['light'][k]['ratio']} / {t['contrast']['dark'][k]['ratio']}")
    ty = t["type"]
    lines += [
        "", "## Type",
        f"- Display: {ty['fonts']['display']}", f"- Body: {ty['fonts']['body']}",
        f"- Scale ratio {ty['ratio']}; base {'1.1rem' if t['rtl'] else '1rem'}; "
        f"body leading {ty['line_height']['body']}, headings {ty['line_height']['heading']}; "
        f"measure {ty['measure']}; letter-spacing {ty['letter_spacing']}.",
        f"- Fonts: {fonts_url(ty['families'])} (confirm availability before shipping)",
        "", "## Space, shape, motion",
        f"- Space scale (px): {', '.join(map(str, t['space']['scale_px']))}; "
        f"section padding {t['space']['section_px'][0]}–{t['space']['section_px'][1]}px.",
        f"- Radius sm/md/lg: {t['radius_px']['sm']}/{t['radius_px']['md']}/{t['radius_px']['lg']}px.",
        f"- Motion: {t['motion_ms']['fast']}/{t['motion_ms']['base']}/{t['motion_ms']['slow']}ms, "
        f"{t['motion_ms']['ease']}; honour prefers-reduced-motion.",
        "", "## Voice",
        "- Name actions by what happens (\"Save changes\", not \"Submit\"); keep the same word through the flow.",
        "- Errors say what happened and how to fix it; empty states invite one action. No filler, no hype.",
        "", "## CSS tokens", "```css", render_css(t).rstrip(), "```", "",
        "_Page-specific exceptions go below this line._", "",
    ]
    return "\n".join(lines)


def archetype_table() -> str:
    rows = ["| id | best for | mood | memorable move | avoid |", "|---|---|---|---|---|"]
    for k, a in ARCHETYPES.items():
        rows.append(f"| `{k}` | {a['best']} | {a['mood']} | {a['move']} | {a['avoid']} |")
    return "\n".join(rows)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--archetype", help="archetype id (see --list)")
    p.add_argument("--seed", help="brand/seed colour, #RGB or #RRGGBB (overrides archetype seed)")
    p.add_argument("--dials", help="e.g. boldness=2,density=4,motion=1,warmth=3")
    p.add_argument("--rtl", action="store_true", help="Arabic-first: fonts, leading, base size")
    p.add_argument("--name", help="project name for the charter title")
    p.add_argument("--format", choices=("md", "json", "css"), default="md")
    p.add_argument("--list", action="store_true", help="list archetypes")
    p.add_argument("--table", action="store_true", help="print the archetype markdown table")
    a = p.parse_args(argv)

    if a.list:
        for k, v in ARCHETYPES.items():
            print(f"{k:22} {v['label']} / {v['label_ar']}: {v['best']}")
        return 0
    if a.table:
        print(archetype_table())
        return 0
    if not a.archetype:
        p.error("--archetype is required (use --list)")
    if a.archetype not in ARCHETYPES:
        p.error(f"unknown archetype {a.archetype!r}; run --list")
    try:
        dials = parse_dials(a.dials, ARCHETYPES[a.archetype]["dials"])
        tokens = build_tokens(a.archetype, a.seed, dials, a.rtl)
    except ValueError as exc:
        p.error(str(exc))
    if a.format == "json":
        print(json.dumps(tokens, indent=2, ensure_ascii=False))
    elif a.format == "css":
        sys.stdout.write(render_css(tokens))
    else:
        sys.stdout.write(render_md(tokens, a.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
