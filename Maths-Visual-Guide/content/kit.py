"""Small shared helpers. Only mechanics live here; every chapter draws its own pictures."""
from generator import canvas as C
from generator import fonts as F

L, R, W = 50, 545, 495


def flow(ch):
    """One continuous writing position for the whole chapter (after its title page)."""
    if getattr(ch, "_flow", None) is None:
        ch._flow = ch.flow()
        ch._flow.new_page()
    return ch._flow


def section(f, title, color, icon=None, room=300, size=20, fresh=False):
    """Start a section: new page if there's not much room left. `icon(pg, x, y)` draws a
    chapter-specific mark in a 18x18 box at (x, y)."""
    if fresh and f.y > f.top + 5:
        f.new_page()
    elif f.y > f.top + 5:
        f.need(room)
        if f.y > f.top + 5:
            f.gap(20)
    pg = f.pg
    y = f.y
    s = size
    while pg.twidth(title, s, F.BOLD) > R - L - 28 and s > 12:
        s -= 1
    if icon:
        icon(pg, L - 4, y + 2)
        pg.text(L + 22, y - 1 + (size - s) / 2, title, s, color, F.BOLD)
    else:
        pg.text(L, y - 1 + (size - s) / 2, title, s, color, F.BOLD)
    f.y += size + 14


def step(f, latex, why=None, size=21, x=L + 16, note_x=None, col=C.RED, color=C.INK,
         min_note_x=290, gap=12, arrow=True):
    """A worked line with its reason written beside it (joined by a small arrow)."""
    pg = f.pg
    w, h, _ = pg.eq_size(latex, size)
    nx = note_x or max(x + w + 34, min_note_x)
    if why and nx > R - 90:
        nx = None
    nh = 0
    if why and nx:
        nh = F.line_h(F.HAND, 16) * len(F.wrap(why, F.HAND, 16, R - nx))
    below = why and nx is None
    bh = F.line_h(F.HAND, 16) * len(F.wrap(why, F.HAND, 16, R - x - 20)) if below else 0
    y = f.reserve(max(h, nh) + bh + gap)
    pg = f.pg
    pg.eq(x, y, latex, size, color)
    if why and nx:
        pg.note(nx, y + max(0, h / 2 - 11), why, col, 16, w=R - nx)
        if arrow:
            pg.arrow(nx - 6, y + h / 2, x + w + 8, y + h / 2, col, 1.0, head=4)
    elif below:
        pg.note(x + 20, y + h + 1, why, col, 16, w=R - x - 20)
    return y, w, h


# ----------------------------------------------------------------------------- rule-first blocks
def _soft(col, t=0.55):
    base = C.LIGHT.get(col) or mix(col, "#ffffff", 0.82)
    return mix(base, "#ffffff", t)


def rule_box(f, title, lines, color=C.BLUE, size=13, numbered=False, gap=14, tag="RULE"):
    """A boxed rule or procedure. `lines` are rich-markup strings ($maths$, {B:...});
    numbered=True turns them into steps 1, 2, 3."""
    pad, num_w = 12, (20 if numbered else 0)
    iw = W - 2 * pad - num_w
    pg = f.pg
    lab = f"{tag}:  {title}" if tag else title
    th = F.line_h(F.BOLD, 12) * len(F.wrap(lab, F.BOLD, 12, W - 2 * pad))
    hs = [pg.rich_h(t, iw, size) for t in lines]
    h = th + 16 + sum(hs) + 6 * (len(lines) - 1) + pad
    y = f.reserve(h + gap)
    pg = f.pg
    pg.rect(L, y, W, h, color, 1.4, fillcolor=_soft(color), r=8)
    pg.text(L + pad, y + 8, lab, 12, color, F.BOLD, w=W - 2 * pad)
    yy = y + th + 16
    for i, (t, hh) in enumerate(zip(lines, hs)):
        if numbered:
            pg.text(L + pad, yy, f"{i + 1}.", size, color, F.BOLD)
        pg.rich(L + pad + num_w, yy, t, iw, size)
        yy += hh + 6
    return y, h


def rules_table(f, headers, rows, widths=None, color=C.BLUE, size=11.5, gap=14):
    """A ruled table of rich-markup cells. The header row repeats if the table runs onto a new page."""
    n = len(headers)
    widths = widths or [W / n] * n
    xs = [L]
    for w_ in widths[:-1]:
        xs.append(xs[-1] + w_)
    pad = 6

    def row_h(cells, sz):
        return max(f.pg.rich_h(c, w_ - 2 * pad, sz) for c, w_ in zip(cells, widths)) + 2 * pad

    def draw(cells, sz, header):
        h = row_h(cells, sz)
        if f.need(h):
            if not header:
                draw(headers, size, True)
        y = f.reserve(h)
        pg = f.pg
        if header:
            pg.rect(L, y, W, h, color, 0.1, fillcolor=color, r=3)
        for c, x, w_ in zip(cells, xs, widths):
            pg.rich(x + pad, y + pad, c, w_ - 2 * pad, sz, "#ffffff" if header else C.INK,
                    F.BOLD if header else F.SANS)
        if not header:
            pg.line(L, y + h, L + W, y + h, _soft(color, 0.1), 0.8)
            for x in xs[1:]:
                pg.line(x, y + 2, x, y + h - 2, _soft(color, 0.3), 0.5)
        return h

    draw(headers, size, True)
    for r_ in rows:
        draw(r_, size, False)
    f.gap(gap)


def mistakes(f, items, title="Common mistakes", size=17, gap=12):
    """Wrong line (grey, red wavy underline) beside the right line (green), with the reason underneath.
    items: (wrong_latex, right_latex, why). A strike-through would hide minus signs, so it is underlined."""
    f.need(60)
    y = f.reserve(24)
    f.pg.text(L, y, "✗  " + title, 14, C.RED, F.BOLD)
    half = W / 2 - 14
    for wrong, right, why in items:
        pg = f.pg
        s = size
        while s > 10 and max(pg.eq_size(wrong, s)[0], pg.eq_size(right, s)[0]) > half - 24:
            s -= 0.5
        w1, h1, _ = pg.eq_size(wrong, s)
        w2, h2, _ = pg.eq_size(right, s)
        eh = max(h1, h2)
        wh = F.line_h(F.HAND, 15) * len(F.wrap(why, F.HAND, 15, W - 30)) if why else 0
        y = f.reserve(eh + wh + 23)
        pg = f.pg
        pg.eq(L + 22, y + (eh - h1) / 2, wrong, s, C.GREY)
        pg.underline(L + 20, y + (eh + h1) / 2 + 5, w1 + 4, C.RED, 1.4, wave=True)
        pg.xmark(L + 2, y + eh / 2 - 5, 10)
        rx = L + W / 2 + 10
        pg.tick(rx - 18, y + eh / 2 - 6, 12)
        pg.eq(rx, y + (eh - h2) / 2, right, s, C.GREEN)
        if why:
            pg.note(L + 22, y + eh + 11, why, C.RED, 15, w=W - 30)
    f.gap(gap)


def rules_page(ch, f, items, color=C.BLUE, title="Rules in this chapter", register=True):
    """A summary page of every rule in the chapter. items: (label, latex or None, words or None).
    Formulas are also registered for the Formula Pages (skipping any already registered)."""
    f.new_page()
    pg = f.pg
    pg.text(L, f.y, title, 22, color, F.BOLD)
    f.y += 32
    f.p("Learn these. Every worked example in the chapter is one of these rules applied step by step.",
        12, C.GREY, gap=8)
    have = {d["latex"] for d in ch.formulas}
    lw = 150
    for label, latex, words in items:
        pg = f.pg
        eh = 0
        s = 13.5
        if latex:
            while s > 9 and pg.eq_size(latex, s)[0] > W - lw - 12:
                s -= 0.5
            eh = pg.eq_size(latex, s)[1]
        wh = pg.rich_h(words, W - lw - 12, 11) if words else 0
        lh = F.line_h(F.BOLD, 11) * len(F.wrap(label, F.BOLD, 11, lw - 12))
        h = max(lh, eh + (wh + 3 if wh else 0)) + 9
        y = f.reserve(h)
        pg = f.pg
        pg.rect(L - 6, y + 2, 3, h - 10, color, 0.1, fillcolor=color)
        pg.text(L + 2, y + 2, label, 11, color, F.BOLD, w=lw - 12)
        yy = y + 2
        if latex:
            pg.eq(L + lw, yy, latex, s)
            yy += eh + 3
        if words:
            pg.rich(L + lw, yy, words, W - lw - 12, 11)
        pg.line(L, y + h - 4, R, y + h - 4, "#eeeeee", 0.6)
        if register and latex and latex not in have:
            ch.formula(latex, label)
            have.add(latex)


def eqrow(f, items, size=20, gap=14):
    """Several formulas side by side, centred in equal columns."""
    pg = f.pg
    hs = [pg.eq_size(it, size)[1] for it in items]
    y = f.reserve(max(hs) + gap)
    pg = f.pg
    n = len(items)
    for i, it in enumerate(items):
        cx = L + W * (i + 0.5) / n
        pg.eq(cx, y + (max(hs) - hs[i]) / 2, it, size, align="center")
    return y


def title_block(ch, number, title, tagline, color, bg="#ffffff"):
    pg = ch.new_page(bg=bg)
    pg.text(L, 60, f"Chapter {number}", 16, C.GREY, F.BOLD)
    s = 40
    while pg.twidth(title, s, F.BOLD) > W and s > 24:
        s -= 1
    pg.text(L, 82, title, s, color, F.BOLD)
    pg.note(L, 88 + s * 1.25, tagline, color, 22, w=W)
    return pg


# ----------------------------------------------------------------------------- 3D blocks
GO_FILL = "#fff7dc"


def your_go_h(w, s, size=14):
    return 30 + F.line_h(F.HAND, size) * len(F.wrap(s, F.HAND, size, w - 24)) + 8


def your_go(pg, x, y, w, s, size=14):
    """A pencil-first task box: the reader commits to a drawing or a guess before the next frame."""
    h = your_go_h(w, s, size)
    pg.rect(x, y, w, h, C.ORANGE, 1.2, fillcolor=GO_FILL, r=8)
    pg.text(x + 12, y + 7, "✎ YOUR GO (pencil first)", 11, C.ORANGE, F.BOLD)
    pg.note(x + 12, y + 26, s, C.INK, size, w=w - 24)
    return h


def go(f, s, gap=10, size=14):
    """Full-width your-go box in the flow."""
    h = your_go_h(W, s, size)
    y = f.reserve(h + gap)
    your_go(f.pg, L, y, W, s, size)


def mix(c1, c2, t):
    """Blend two #rrggbb colours: t = 0 gives c1, t = 1 gives c2."""
    p1 = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    p2 = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(u + (v - u) * t):02x}" for u, v in zip(p1, p2))


DEPTH = 0.45  # how far the depth axis slants up-right


def block(pg, ox, oy, X0, Y0, Z0, X1, Y1, Z1, col, label=None, size=13, dashed=False):
    """A box drawn in oblique 3D: X right, Y up, Z away from you. (ox, oy) is where (0,0,0) lands."""
    P = lambda X, Y, Z: (ox + X + DEPTH * Z, oy - Y - DEPTH * Z)
    front = [P(X0, Y0, Z0), P(X1, Y0, Z0), P(X1, Y1, Z0), P(X0, Y1, Z0)]
    top = [P(X0, Y1, Z0), P(X1, Y1, Z0), P(X1, Y1, Z1), P(X0, Y1, Z1)]
    side = [P(X1, Y0, Z0), P(X1, Y0, Z1), P(X1, Y1, Z1), P(X1, Y1, Z0)]
    if dashed:
        for face in (front, top, side):
            pg.poly(face, col, 1.0, dash=(3, 3), closed=True)
        return
    lt = C.LIGHT[col]
    for face, fc in ((front, lt), (top, mix(lt, "#ffffff", 0.55)), (side, mix(lt, col, 0.3))):
        pg.fillpoly(face, fc, outline=col, width=1.0, layer=C.MAIN)
    if label:
        fx, fy = P((X0 + X1) / 2, (Y0 + Y1) / 2, Z0)
        pg.eq(fx, fy, label, size, col, align="center", valign="middle")


def blocks(pg, ox, oy, items):
    """Draw boxes far-to-near so nearer ones cover farther ones: back first, then left to right, bottom up."""
    for it in sorted(items, key=lambda b_: (-b_[2], b_[0], b_[1])):
        block(pg, ox, oy, *it)
