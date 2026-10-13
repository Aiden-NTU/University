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
