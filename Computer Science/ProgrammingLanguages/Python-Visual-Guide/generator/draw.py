"""Geometry helpers that return point lists for Xournal++ strokes."""
import math


def bezier(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]
        pts.append((x, y))
    return pts


def cubic(p0, p1, p2, p3, n=30):
    pts = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def curve_between(x1, y1, x2, y2, bend=0.0, n=24):
    """Quadratic curve from (x1,y1) to (x2,y2). bend>0 bows to the left of travel."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    c = (mx + nx * bend * L, my + ny * bend * L)
    if bend == 0:
        return [(x1, y1), (x2, y2)]
    return bezier((x1, y1), c, (x2, y2), n)


def arrow_head(tip, frm, size=7.0, spread=0.45):
    ang = math.atan2(tip[1] - frm[1], tip[0] - frm[0])
    a1 = ang + math.pi - spread
    a2 = ang + math.pi + spread
    return [
        (tip[0] + size * math.cos(a1), tip[1] + size * math.sin(a1)),
        tip,
        (tip[0] + size * math.cos(a2), tip[1] + size * math.sin(a2)),
    ]


def ellipse(cx, cy, rx, ry, n=64, a0=0.0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n),
             cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def arc(cx, cy, r, deg0, deg1, n=None):
    """Arc in maths orientation (degrees anticlockwise from +x, y up on screen)."""
    n = n or max(8, int(abs(deg1 - deg0) / 4))
    pts = []
    for i in range(n + 1):
        a = math.radians(deg0 + (deg1 - deg0) * i / n)
        pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
    return pts


def rrect(x, y, w, h, r=8.0, n=6):
    r = min(r, w / 2, h / 2)
    pts = []
    corners = [(x + w - r, y + r, -90, 0), (x + w - r, y + h - r, 0, 90),
               (x + r, y + h - r, 90, 180), (x + r, y + r, 180, 270)]
    for cx, cy, a0, a1 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    pts.append(pts[0])
    return pts


def brace(x1, y1, x2, y2, depth=8.0):
    """Curly brace from (x1,y1) to (x2,y2); the point bulges to the right of travel."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux
    nx, ny = -nx, -ny

    def P(s, t):
        return (x1 + ux * s + nx * t, y1 + uy * s + ny * t)

    h = L / 2
    d = depth
    pts = []
    pts += cubic(P(0, 0), P(0, d * 0.6), P(h * 0.15, d * 0.5), P(h * 0.5, d * 0.5), 10)
    pts += cubic(P(h * 0.5, d * 0.5), P(h * 0.85, d * 0.5), P(h, d * 0.4), P(h, d), 10)[1:]
    pts += cubic(P(h, d), P(h, d * 0.4), P(h * 1.15, d * 0.5), P(h * 1.5, d * 0.5), 10)[1:]
    pts += cubic(P(h * 1.5, d * 0.5), P(h * 1.85, d * 0.5), P(L, d * 0.6), P(L, 0), 10)[1:]
    return pts, P(h, d)


def dashes(pts, on=5.0, off=4.0):
    """Split a polyline into dash segments."""
    segs = []
    cur = []
    state_on = True
    left = on
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        L = math.hypot(xb - xa, yb - ya)
        pos = 0.0
        while pos < L:
            step = min(left, L - pos)
            t0, t1 = pos / L, (pos + step) / L
            a = (xa + (xb - xa) * t0, ya + (yb - ya) * t0)
            b = (xa + (xb - xa) * t1, ya + (yb - ya) * t1)
            if state_on:
                if not cur:
                    cur.append(a)
                cur.append(b)
            pos += step
            left -= step
            if left <= 1e-9:
                if state_on and cur:
                    segs.append(cur)
                    cur = []
                state_on = not state_on
                left = on if state_on else off
    if cur:
        segs.append(cur)
    return segs


def wavy(x1, y, x2, amp=2.0, wl=6.0):
    n = max(4, int((x2 - x1) / wl * 6))
    return [(x1 + (x2 - x1) * i / n, y + amp * math.sin(2 * math.pi * (x2 - x1) * i / n / wl))
            for i in range(n + 1)]


def star(cx, cy, r, n=5):
    pts = []
    for i in range(2 * n + 1):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / n
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts
