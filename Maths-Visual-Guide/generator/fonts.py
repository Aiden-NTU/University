"""Text measurement that matches how Xournal++ (Pango) lays out text."""
import functools

import cairo

SANS = "DejaVu Sans"
BOLD = "DejaVu Sans Bold"
ITALIC = "DejaVu Sans Oblique"
BOLDITALIC = "DejaVu Sans Bold Oblique"
HAND = "Caveat"
MONO = "DejaVu Sans Mono"

# Calibrated against Xournal++ 1.3.6 exports: distance from text-box top to the
# baseline, and distance between consecutive lines, as multiples of font size.
METRICS = {
    SANS: (0.9285, 1.18),
    BOLD: (0.9285, 1.18),
    ITALIC: (0.9285, 1.18),
    BOLDITALIC: (0.9285, 1.18),
    HAND: (1.045, 1.26),
    MONO: (0.9285, 1.18),
}

_REF = 1000.0
_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 4, 4)
_ctx = cairo.Context(_surf)
_opts = cairo.FontOptions()
_opts.set_hint_style(cairo.HINT_STYLE_NONE)
_opts.set_hint_metrics(cairo.HINT_METRICS_OFF)
_ctx.set_font_options(_opts)


def _face(font):
    fam = font
    weight = cairo.FONT_WEIGHT_NORMAL
    slant = cairo.FONT_SLANT_NORMAL
    if "Bold" in fam:
        weight = cairo.FONT_WEIGHT_BOLD
        fam = fam.replace(" Bold", "")
    if "Oblique" in fam:
        slant = cairo.FONT_SLANT_OBLIQUE
        fam = fam.replace(" Oblique", "")
    return fam, slant, weight


@functools.lru_cache(maxsize=200000)
def width(text, font=SANS, size=13.0):
    fam, slant, weight = _face(font)
    _ctx.select_font_face(fam, slant, weight)
    _ctx.set_font_size(_REF)
    w = _ctx.text_extents(text).x_advance * size / _REF
    return w * 1.035 if font == HAND else w


def baseline(font, size):
    return METRICS.get(font, METRICS[SANS])[0] * size


def line_h(font, size):
    return METRICS.get(font, METRICS[SANS])[1] * size


def wrap(text, font, size, maxw):
    """Greedy word wrap. Honours explicit newlines. Returns list of lines."""
    out = []
    for para in text.split("\n"):
        words = para.split(" ")
        cur = ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if width(trial, font, size) <= maxw or not cur:
                cur = trial
            else:
                out.append(cur)
                cur = w
        out.append(cur)
    return out
