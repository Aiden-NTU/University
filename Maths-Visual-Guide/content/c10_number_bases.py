"""Chapter 10 - Number bases. Rolling counters with fewer digits, making change with 16/8/4/2/1
coins, hex colour codes, and binary adding as XOR plus carry."""
import sympy as sp

from generator import canvas as C
from generator import fonts as F
from content.kit import L, R, W, flow, mistakes, rule_box, rules_page, section, step, title_block

ORDER = 10
NUM = 10
TITLE = "Number bases"
SHORT = "Number bases"
SLUG = "Number-Bases"
ACCENT = C.BLUE
REQUIRES = ["place-value", "powers", "zero-power", "division", "remainder", "xor", "base-exponent"]
INTRODUCES = ["number-base", "binary", "binary-to-decimal", "decimal-to-binary", "octal", "hexadecimal",
              "binary-addition", "bits-bytes"]

PAPER = "#fafcff"
COIN = "#f2c94c"
COIN_EDGE = "#a67c00"


STICK = "#b07a3a"


def sticks(pg, x, y, n, h=34, gap=6, col=STICK):
    for i in range(n):
        pg.line(x + i * gap, y, x + i * gap, y + h, col, 2.4)


def bundle(pg, x, y, h=34, col=STICK):
    for i in range(10):
        pg.line(x + i * 2.4, y, x + i * 2.4, y + h, col, 1.6)
    pg.line(x - 2, y + h / 2, x + 24, y + h / 2, C.RED, 2)


def crate(pg, x, y, s=34):
    pg.rect(x, y, s, s, C.BROWN, 1.6, fillcolor="#e8cfa8", r=3)
    for i in range(1, 4):
        pg.line(x + i * s / 4, y + 3, x + i * s / 4, y + s - 3, "#b58f5c", 0.8)
    pg.text(x + s / 2, y + s / 2 - 7, "100", 9, C.BROWN, F.BOLD, align="center")


def icon(pg, x0, y0):
    for i, d in enumerate("101"):
        pg.rect(x0 + i * 6.4, y0 + 2, 6, 14, C.INK, 0.6, fillcolor="#263238")
        pg.text(x0 + i * 6.4 + 3, y0 + 4, d, 7, "#ffffff", F.BOLD, align="center", solid=False)


def sec(f, t, **kw):
    section(f, t, C.BLUE, icon, **kw)


def counter(pg, x0, y0, digits, w=30, h=40, size=20, hl=None):
    for j, d in enumerate(digits):
        fc = "#263238" if not hl or j not in hl else "#1f5fbf"
        pg.rect(x0 + j * (w + 4), y0, w, h, C.INK, 1, fillcolor=fc, r=4)
        pg.text(x0 + j * (w + 4) + w / 2, y0 + h / 2 - size * 0.62, d, size, "#ffffff", F.BOLD, align="center")


def coin(pg, cx, cy, v, r=15, used=True):
    pg.circle(cx, cy, r, COIN_EDGE, 1.4, fillcolor=COIN if used else "#f4f4f4", dash=None if used else (3, 2))
    pg.text(cx, cy - 7, str(v), 12, COIN_EDGE if used else C.GREY, F.BOLD, align="center", solid=False)


def ex(f, s):
    f.need(100)
    f.p("{B:Example:}  " + s, 13.5, gap=4)


DIG = "0123456789ABCDEF"


def ladder(f, n, b, x0=L + 30, note=None):
    """Repeated division of n by b, one line per step, with the remainders read upwards."""
    rows = []
    while n > 0:
        q, r = divmod(n, b)
        rows.append((n, q, r))
        n = q
    y = f.reserve(len(rows) * 24 + 10)
    pg = f.pg
    for i, (n_, q, r) in enumerate(rows):
        pg.text(x0, y + i * 24, f"{n_} ÷ {b} = {q}", 14, C.INK)
        rs = f"remainder {r}" + (f"  (= {DIG[r]})" if r >= 10 else "")
        pg.text(x0 + 130, y + i * 24, rs, 14, C.ORANGE, F.BOLD)
    pg.arrow(x0 + 290, y + len(rows) * 24 - 10, x0 + 290, y + 4, C.GREEN, 1.8)
    digits = "".join(DIG[r] for _, _, r in reversed(rows))
    pg.note(x0 + 305, y + max(0, len(rows) * 12 - 22), note or f"read upwards:\n{' '.join(digits)}", C.GREEN, 17)
    return digits


def columns(pg, x0, y0, heads, digits, cw=56, col=C.BLUE, size=22):
    for j, (hd, d) in enumerate(zip(heads, digits)):
        pg.rect(x0 + j * cw, y0, cw, 26, col, 1, fillcolor=C.LIGHT[col])
        pg.text(x0 + j * cw + cw / 2, y0 + 7, hd, 11, col, F.BOLD, align="center")
        pg.rect(x0 + j * cw, y0 + 26, cw, 38, col, 1)
        pg.text(x0 + j * cw + cw / 2, y0 + 33, d, size, C.INK, F.BOLD, align="center")


# ----------------------------------------------------------------------------- pages
def title_page(ch):
    pg = title_block(ch, 10, "Number bases", "counting with fewer (or more) than ten digits",
                     C.BLUE, PAPER)
    rows = ["0000", "0001", "0010", "0011", "0100"]
    for i, r in enumerate(rows):
        counter(pg, L + 30, 200 + i * 44, r, 26, 36, 18)
        pg.note(L + 160, 206 + i * 44, f"= {i}", C.BLUE, 20)
    pg.note(L + 250, 230, "a mileage counter whose wheels\nonly have 0 and 1 on them:\nthis is binary, "
            "the way every\ncomputer counts", C.INK, 18)
    f = ch.flow(top=440)
    f.p("We count in tens because we have ten fingers. Nothing else about ten is special. A "
        "computer's switches have only two states (off/on), so computers count in {B:twos}: binary. "
        "Programmers also use {B:sixteens} (hexadecimal) because it's a compact way to write binary.",
        14, gap=10)
    f.p("The good news: every base works exactly like the place value you already know from "
        "Chapter 1. Only the size of the bundles changes.", 14, gap=10)
    f.p("{y:Not a lecture topic, but essential for Computer Science modules.}", 12.5)


def base_ten(ch):
    f = flow(ch)
    sec(f, "Our usual numbers, taken apart column by column", room=600)
    rule_box(f, "place value in any base", [
        "In base $b$ there are $b$ digits: $0, 1, \\dots, b-1$.",
        "Columns, from the right, are worth $b^0=1,\\ b^1,\\ b^2,\\ b^3, \\dots$: each column is worth "
        "$b$ times the one to its right.",
        "The value of a number is the sum of (digit × column value). A subscript gives the base: "
        "$347_{10}$, $10110_2$, $2F_{16}$.",
    ], C.BLUE)
    f.p("Take the number 347. It has three digits, and each digit sits in its own slot, called a "
        "{B:column} (like the columns of a table). Reading from the right: the {B:ones} column, the "
        "{B:tens} column, the {B:hundreds} column. The 3, 4 and 7 are not worked out from anything: "
        "they are simply the digits of 347, read left to right. What the {B:column} changes is how "
        "much each digit is worth (Chapter 1's crates, bundles and sticks):", 14, gap=10)
    y = f.reserve(160)
    pg = f.pg
    heads = [("hundreds column", C.BROWN), ("tens column", C.RED), ("ones column", STICK)]
    for i, (hd, col) in enumerate(heads):
        x0 = L + 10 + i * 165
        pg.rect(x0, y, 150, 150, col, 1.3, r=8)
        pg.rect(x0, y, 150, 24, col, 1, fillcolor=C.LIGHT.get(col, "#f3e6d6"), r=8)
        pg.text(x0, y + 5, hd, 11, col, F.BOLD, w=150, align="center")
        pg.text(x0, y + 28, "347"[i], 30, C.INK, F.BOLD, w=150, align="center")
    for k in range(3):
        crate(pg, L + 22 + k * 44, y + 76, 36)
    for k in range(4):
        bundle(pg, L + 186 + k * 34, y + 78, 34)
    sticks(pg, L + 360, y + 78, 7, 34, 9)
    for i, e in enumerate([r"3\times100=300", r"4\times10=40", r"7\times1=7"]):
        pg.eq(L + 85 + i * 165, y + 132, e, 15, C.INK, align="center", valign="middle")
    ch.check(3 * 100 + 4 * 10 + 7, 347)
    f.p("The {B:column value} is what {B:one} of something is worth in that column: 1 in the ones "
        "column, 10 in the tens column, 100 in the hundreds column. Each step to the left is "
        "{B:ten times} bigger, because ten sticks make a bundle and ten bundles make a crate. Now "
        "write those column values with powers (Chapter 9). $10^2$ just means two tens multiplied:", 14, gap=8)
    y = f.reserve(112)
    pg = f.pg
    vals = [("1000", "10^3", r"10\times10\times10"), ("100", "10^2", r"10\times10"), ("10", "10^1", r"\text{one }10"),
            ("1", "10^0", r"\text{power 0 is 1}")]
    for i, (v, pw, why) in enumerate(vals):
        x0 = L + 12 + i * 122
        pg.rect(x0, y + 18, 96, 58, C.BLUE, 1.2, fillcolor=C.LIGHT[C.BLUE], r=8)
        pg.text(x0, y + 22, v, 16, C.INK, F.BOLD, w=96, align="center")
        pg.eq(x0 + 48, y + 60, "=" + pw, 16, C.BLUE, align="center", valign="middle")
        pg.eq(x0 + 48, y + 92, why, 11, C.GREY, align="center", valign="middle")
        if i < 3:
            pg.arrow(x0 + 122, y + 12, x0 + 96, y + 12, C.RED, 1.1, bend=0.4, head=4)
            pg.text(x0 + 89, y - 4, "× 10", 10, C.RED, F.BOLD, w=40, align="center")
    f.p("{b:Put it together.} Write the column values as powers over the digits, then multiply each digit "
        "by its column value and add:", 14, gap=8)
    y = f.reserve(80)
    pg = f.pg
    columns(pg, L + 20, y, ["10² = 100", "10¹ = 10", "10⁰ = 1"], "347", cw=90)
    pg.eq(L + 300, y + 8, r"3\times100+4\times10", 16)
    pg.eq(L + 300, y + 34, r"+\,7\times1=347", 16)
    f.p("The number 10 is called the {B:base}. A base-10 system needs exactly ten digits (0 to 9) "
        "because when a column reaches ten it {B:rolls over} to 0 and pushes a 1 into the next "
        "column, like the mileage counter.", 14, gap=8)
    ch.term("number base", "how many digits a counting system uses; each column is worth base × the one to its right")
    f.p("{b:Change the base, change the bundles.} In base 2, bundles are made of 2; in base 16, of "
        "16. Everything else stays the same.", 14)


def binary_count(ch):
    f = flow(ch)
    sec(f, "Counting in binary: a counter with only 0 and 1", room=420)
    rule_box(f, "binary (base 2)", [
        "Two digits only: 0 and 1 (called {B:bits}).",
        "Column values from the right: $1, 2, 4, 8, 16, 32, 64, 128, \\dots$ (the powers of 2).",
    ], C.BLUE)
    f.p("Each wheel has just two digits. Add 1 and the right wheel goes 0 → 1. Add 1 again: it "
        "{B:rolls over} to 0 and pushes the next wheel on. Watch:", 14, gap=8)
    y = f.reserve(200)
    pg = f.pg
    for k in range(9):
        b = format(k, "04b")
        col = k // 5
        row = k % 5
        xx = L + 10 + col * 250
        yy = y + row * 38
        counter(pg, xx, yy, b, 24, 32, 16)
        pg.text(xx + 118, yy + 8, f"= {k}", 14, C.BLUE, F.BOLD)
        if k in (2, 4, 8):
            pg.note(xx + 160, yy + 4, "roll over!", C.RED, 14)
    f.p("Binary has two digits, 0 and 1, called {B:bits} (binary digits). The columns are worth "
        "1, 2, 4, 8, 16, ...: each is {B:double} the one to its right, because two of one column make "
        "one of the next.", 14, gap=8)
    ch.term("binary", "base 2: counting with only the digits 0 and 1")
    ch.term("bit", "a binary digit, 0 or 1")


def to_decimal(ch):
    f = flow(ch)
    sec(f, "Binary → ordinary: add up the column values", room=360)
    rule_box(f, "base b → decimal", [
        "Write the column values $1, b, b^2, \\dots$ over the digits, starting from the {B:right}.",
        "Multiply each digit by its column value (in binary: keep the columns with a 1).",
        "Add the results.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    f.p("To read $10110_2$ (the little 2 means \"in base 2\"), write the column values over the "
        "digits and add up the ones that have a 1 under them:", 14, gap=8)
    ch.symbol(r"10110_2", "one-zero-one-one-zero in base two", "the subscript gives the base")
    y = f.reserve(80)
    pg = f.pg
    columns(pg, L + 20, y, ["16", "8", "4", "2", "1"], "10110")
    for j, d in enumerate("10110"):
        if d == "1":
            pg.highlight(L + 20 + j * 56 + 4, y + 30, 48, 30, "g")
    pg.eq(L + 320, y + 22, r"16+4+2=22", 20, C.GREEN)
    ch.check(int("10110", 2), 22)
    f.p("So $10110_2 = 22_{10}$. Read aloud as \"one zero one one zero\", never \"ten thousand one "
        "hundred and ten\" (that's a base-10 number).", 14)


def to_binary(ch):
    f = flow(ch)
    sec(f, "Ordinary → binary: making change with coins", room=460)
    rule_box(f, "decimal → binary (two methods)", [
        "{B:Biggest power first:} list the powers of 2 up to the number. Working from the biggest, "
        "write 1 and subtract if it fits, 0 if it doesn't, until nothing is left.",
        "{B:Repeated halving:} divide by 2, write the remainder (0 or 1), and repeat on the quotient "
        "until it is 0. Read the remainders from the {B:bottom up}.",
    ], C.BLUE)
    f.p("Imagine a country with coins worth {B:16, 8, 4, 2 and 1}, and you may use {B:at most one} "
        "of each. Pay 22 using the biggest coins first:", 14, gap=8)
    y = f.reserve(150)
    pg = f.pg
    steps_ = [(16, True, "22: use the 16 → 6 left"), (8, False, "6: 8 is too big → skip"),
              (4, True, "6: use the 4 → 2 left"), (2, True, "2: use the 2 → 0 left"),
              (1, False, "0: nothing left → skip")]
    for j, (v, used, why) in enumerate(steps_):
        cx = L + 40 + j * 96
        coin(pg, cx, y + 20, v, 17, used)
        pg.text(cx, y + 44, "1" if used else "0", 22, C.GREEN if used else C.GREY, F.BOLD, align="center")
        pg.note(cx - 36, y + 76, why, C.GREEN if used else C.GREY, 13, w=90)
    ch.check(format(22, "b"), "10110")
    f.p("Used = 1, skipped = 0. Reading the row: {G:10110}. That's 22 in binary.", 14, gap=8)
    f.p("{b:Method 2: keep halving} (handy for big numbers). Divide by 2 and write down each remainder "
        "(Chapter 1); then read the remainders {B:from the bottom up}:", 14, gap=6)
    y = f.reserve(140)
    pg = f.pg
    n = 22
    i = 0
    while n > 0:
        q, r = divmod(n, 2)
        pg.text(L + 30, y + i * 24, f"{n} ÷ 2 = {q}", 14, C.INK)
        pg.text(L + 160, y + i * 24, f"remainder {r}", 14, C.ORANGE, F.BOLD)
        n = q
        i += 1
    pg.arrow(L + 270, y + i * 24 - 10, L + 270, y + 4, C.GREEN, 1.8)
    pg.note(L + 285, y + 30, "read upwards:\n1 0 1 1 0", C.GREEN, 17)


def octal_hex(ch):
    f = flow(ch)
    sec(f, "Base 16 (hexadecimal): running out of digits", room=500)
    rule_box(f, "hexadecimal (base 16) and octal (base 8)", [
        "Hex digits: 0 to 9, then {B:A = 10, B = 11, C = 12, D = 13, E = 14, F = 15}. "
        "Columns: 1, 16, 256, 4096 (powers of 16).",
        "Octal digits: 0 to 7. Columns: 1, 8, 64, 512 (powers of 8).",
    ], C.BLUE)
    f.p("In base 16 a column can hold up to fifteen before rolling over. But we only have ten digit "
        "symbols! So we borrow letters: {B:A = 10, B = 11, C = 12, D = 13, E = 14, F = 15}.", 14, gap=8)
    ch.term("hexadecimal (hex)", "base 16: digits 0-9 then A-F for 10-15")
    y = f.reserve(40)
    pg = f.pg
    for i in range(16):
        d = "0123456789ABCDEF"[i]
        pg.rect(L + 10 + i * 30, y, 28, 34, C.BLUE, 0.8, fillcolor=C.LIGHT[C.BLUE] if i >= 10 else "#ffffff")
        pg.text(L + 24 + i * 30, y + 3, d, 14, C.BLUE, F.BOLD, align="center")
        pg.text(L + 24 + i * 30, y + 20, str(i), 8, C.GREY, align="center")
    f.p("Columns are worth 1, 16, 256, ... (powers of 16). So $2F_{16} = 2 \\times 16 + 15 = 47$.",
        14, gap=10)
    ch.check(int("2F", 16), 47)
    f.p("{b:Where you've seen hex: colour codes.} A web colour like #FF8800 is three hex pairs: how "
        "much {R:red}, {G:green} and {B:blue} light, each from 00 (none) to FF (full):", 14, gap=8)
    y = f.reserve(100)
    pg = f.pg
    cols = [("#FF8800", (255, 136, 0)), ("#1F5FBF", (31, 95, 191)), ("#00FF00", (0, 255, 0)), ("#808080", (128, 128, 128))]
    for i, (hx, rgb) in enumerate(cols):
        xx = L + 10 + i * 122
        pg.rect(xx, y, 110, 44, C.INK, 1, fillcolor=hx.lower() + "", r=6)
        pg.text(xx + 55, y + 50, hx, 12, C.INK, F.MONO, align="center")
        pg.text(xx + 55, y + 68, f"R{rgb[0]} G{rgb[1]} B{rgb[2]}", 10, C.GREY, align="center")
    ch.check(int("FF", 16), 255)
    ch.check(int("88", 16), 136)
    f.p("FF = 15 × 16 + 15 = 255, the biggest two hex digits can hold. #FF8800 is full red, a bit "
        "over half green, no blue: orange.", 14, gap=8)
    f.p("{b:Why programmers love hex:} each hex digit is exactly 4 bits, so binary converts in "
        "chunks with no arithmetic:", 14, gap=6)
    y = f.reserve(60)
    pg = f.pg
    for i, (bits, hx) in enumerate([("1111", "F"), ("1000", "8"), ("1000", "8"), ("0000", "0")]):
        xx = L + 20 + i * 90
        pg.text(xx, y, bits, 16, C.INK, F.MONO)
        pg.arrow(xx + 20, y + 22, xx + 20, y + 36, C.GREY, 1, head=4)
        pg.text(xx + 16, y + 38, hx, 16, C.BLUE, F.BOLD)
    pg.note(L + 390, y + 10, "11111000 10000000\n= F8 80", C.BLUE, 15)
    f.p("{b:Octal} (base 8, digits 0-7, columns 1, 8, 64) works the same way with 3-bit chunks; you'll "
        "see it in Linux file permissions like chmod 755.", 13.5, C.GREY)
    ch.term("octal", "base 8: digits 0-7")


def to_any(ch):
    f = flow(ch)
    sec(f, "Decimal → any base: divide and read upwards", room=520)
    rule_box(f, "decimal → base b", [
        "Divide the number by $b$. Write down the whole-number quotient and the {B:remainder} "
        "(a remainder is always between 0 and $b-1$).",
        "Divide the quotient by $b$ again, and keep going until the quotient is {B:0}.",
        "Write each remainder as a single base-$b$ digit (in hex, 10 to 15 become A to F).",
        "Read the remainders from the {B:bottom up}: the last remainder is the leftmost digit.",
        "Check by converting back: digit × column value, added up.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    f.p("This is the halving method from binary with 2 replaced by $b$. It works because each division "
        "peels off the rightmost digit: the remainder is what doesn't fill a whole bundle of $b$.",
        13.5, gap=8)
    ex(f, "write 200 in hexadecimal.")
    d = ladder(f, 200, 16, note="read upwards:\nC 8")
    ch.check_true(d == "C8")
    step(f, r"200=C8_{16}", "check: 12 × 16 + 8 = 192 + 8 = 200 ✓", size=19, color=C.GREEN)
    ch.check(int("C8", 16), 200)
    ex(f, "write 100 in octal (base 8).")
    d = ladder(f, 100, 8)
    ch.check_true(d == "144")
    step(f, r"100=144_8", "check: 1 × 64 + 4 × 8 + 4 = 100 ✓", size=19, color=C.GREEN)
    ch.check(int("144", 8), 100)
    ex(f, "write 45 in base 3.")
    d = ladder(f, 45, 3)
    ch.check_true(d == "1200")
    step(f, r"45=1200_3", "check: 1 × 27 + 2 × 9 = 45 ✓", size=19, color=C.GREEN)
    ch.check(int("1200", 3), 45)
    rule_box(f, "binary ↔ hex and binary ↔ octal", [
        "One hex digit is exactly {B:4 bits} (because $16=2^4$); one octal digit is exactly {B:3 bits} "
        "($8=2^3$).",
        "{B:Binary → hex:} split the bits into groups of 4 {B:from the right}, pad the left group with "
        "zeros, and convert each group (0000 = 0 up to 1111 = F). For octal use groups of 3.",
        "{B:Hex → binary:} replace each hex digit by its 4 bits (keep leading zeros inside the number).",
    ], C.BLUE)
    ex(f, "write $1101011_2$ in hex and in octal.")
    step(f, r"\underbrace{0110}_{6}\ \underbrace{1011}_{B}\ \Rightarrow\ 6B_{16}", "groups of 4 from the right; pad with a 0",
         size=18)
    step(f, r"\underbrace{001}_{1}\ \underbrace{101}_{5}\ \underbrace{011}_{3}\ \Rightarrow\ 153_8", "groups of 3 from the right",
         size=18, color=C.GREEN)
    ch.check(int("1101011", 2), int("6B", 16))
    ch.check(int("1101011", 2), int("153", 8))
    ch.check_true(format(int("1101011", 2), "X") == "6B")
    ex(f, "write $2F_{16}$ in binary.")
    step(f, r"2\to0010,\quad F\to1111\ \Rightarrow\ 101111_2", "drop the leading zeros at the very front",
         size=18, color=C.GREEN)
    ch.check(int("2F", 16), int("101111", 2))
    f.p("Check: $101111_2 = 32 + 8 + 4 + 2 + 1 = 47$, and $2F_{16} = 47$ ✓.", 13.5, C.GREEN)


def adding(ch):
    f = flow(ch)
    sec(f, "Adding in binary: 1 + 1 = 10", room=420)
    rule_box(f, "binary addition", [
        "Line the numbers up on the right and add column by column, {B:right to left}, as in base 10.",
        "$0+0=0$,  $0+1=1$,  $1+1=10_2$ (write 0, carry 1),  $1+1+1=11_2$ (write 1, carry 1).",
        "Check by converting everything to decimal.",
    ], C.BLUE)
    f.p("There are only four single-digit sums. The last one rolls over, just as 9 + 1 does in base "
        "10:", 14, gap=8)
    y = f.reserve(40)
    pg = f.pg
    for i, (s, r) in enumerate([("0 + 0", "0"), ("0 + 1", "1"), ("1 + 0", "1"), ("1 + 1", "10")]):
        pg.text(L + 20 + i * 120, y, f"{s} = {r}", 15, C.RED if r == "10" else C.INK, F.BOLD)
    pg.note(L + 380, y + 18, "write 0, carry 1", C.RED, 14)
    f.p("Work out $1011_2 + 110_2$, column by column from the right, exactly like Chapter 1:", 14, gap=8)
    y = f.reserve(120)
    pg = f.pg
    X = L + 80
    cw = pg.twidth("0", 20, F.MONO)
    for i in (0, 2, 4):
        pg.text(X + cw * i + cw / 2, y, "1", 11, C.RED, F.BOLD, align="center")
    pg.text(X, y + 14, "  1 0 1 1", 20, C.INK, F.MONO)
    pg.text(X, y + 40, "+   1 1 0", 20, C.INK, F.MONO)
    pg.line(X, y + 68, X + 118, y + 68, C.INK, 1.5)
    pg.text(X, y + 72, "1 0 0 0 1", 20, C.GREEN, F.MONO)
    pg.note(X + 150, y + 10, "1s column: 1 + 0 = 1\n2s column: 1 + 1 = 10 → write 0, carry 1\n"
            "4s column: 0 + 1 + 1 (carry) = 10 → write 0, carry 1\n8s column: 1 + 1 (carry) = 10 → 0, carry 1",
            C.INK, 14)
    ch.check(int("1011", 2) + int("110", 2), int("10001", 2))
    f.p("Check in base 10: 11 + 6 = 17, and $10001_2 = 16 + 1 = 17$ ✓.", 13.5, gap=8)
    f.p("{h:Link to Chapter 7, carefully.} A column with {B:two} bits and no carry coming in is simple: "
        "digit = A XOR B, carry = A AND B (a {B:half adder}). But look at the 4s column above: it adds "
        "{B:three} bits, A, B and the carry that came in. Every column after the first can have three "
        "inputs, so a chip uses a {B:full adder}: the digit is 1 when an {B:odd} number of the three are 1, "
        "and the carry out is 1 when {B:two or more} are 1. Here's every column of the sum:", 13.5, gap=8)
    rows = [("1s", 1, 0, 0), ("2s", 1, 1, 0), ("4s", 0, 1, 1), ("8s", 1, 0, 1), ("16s", 0, 0, 1)]
    y = f.reserve(30 + 22 * len(rows))
    pg = f.pg
    hdr = [("column", L + 10), ("A", L + 90), ("B", L + 130), ("carry in", L + 170), ("digit (odd?)", L + 260),
           ("carry out (2+?)", L + 370)]
    for t_, xx in hdr:
        pg.text(xx, y, t_, 11, C.GREY, F.BOLD)
    pg.line(L + 6, y + 17, R - 10, y + 17, C.GREY, 0.8)
    digits = []
    carry = 0
    for k, (nm, a_, b_, cin) in enumerate(rows):
        yy = y + 24 + k * 22
        ch.check(cin, carry)
        n1 = a_ + b_ + cin
        d, cout = n1 % 2, int(n1 >= 2)
        ch.check(d, a_ ^ b_ ^ cin)
        ch.check(cout, (a_ & b_) | (cin & (a_ ^ b_)))
        digits.append(d)
        carry = cout
        for v, xx in [(nm, L + 10), (a_, L + 90), (b_, L + 130), (cin, L + 170)]:
            pg.text(xx, yy, str(v), 13, C.RED if (xx == L + 170 and cin) else C.INK)
        pg.text(L + 260, yy, str(d), 13, C.GREEN, F.BOLD)
        pg.text(L + 370, yy, str(cout), 13, C.RED if cout else C.INK, F.BOLD)
    ch.check("".join(str(d) for d in reversed(digits)), "10001")
    f.p("Read the green digits from the bottom up: 10001 ✓. Only the 1s column can never receive a carry, "
        "so it can be a half adder. Every other column {B:might} get one (here the 2s column happened not "
        "to), so each needs a full adder. In Chapter 7's words, with C the carry in:", 13.5, gap=6)
    f.p("{B:digit} = A XOR B XOR C        {B:carry out} = (A AND B) OR (C AND (A XOR B))", 13.5)
    for a_ in (0, 1):
        for b_ in (0, 1):
            for c_ in (0, 1):
                ch.check(a_ ^ b_ ^ c_, (a_ + b_ + c_) % 2)
                ch.check((a_ & b_) | (c_ & (a_ ^ b_)), int(a_ + b_ + c_ >= 2))


def subtracting(ch):
    f = flow(ch)
    sec(f, "Subtracting in binary: borrowing a 2", room=420)
    rule_box(f, "binary subtraction", [
        "Work column by column, right to left: $0-0=0$, $1-0=1$, $1-1=0$.",
        "$0-1$ needs a {B:borrow}: take 1 from the next column to the left. It arrives as {B:2} "
        "(one of the next column is worth two of this one), so the column becomes $10_2-1=1$.",
        "If the next column is also 0, borrow from further left; every 0 passed over becomes 1.",
    ], C.BLUE)
    ex(f, "$1101_2-110_2$ (that is $13-6$).")
    y = f.reserve(110)
    pg = f.pg
    X = L + 70
    cw = pg.twidth("0", 20, F.MONO)
    for i, s in ((2, "0"), (4, "2"), (6, "2")):
        pg.text(X + cw * i + cw / 2, y, s, 11, C.RED, F.BOLD, align="center")
    pg.text(X, y + 14, "  1 1 0 1", 20, C.INK, F.MONO)
    pg.text(X, y + 40, "−   1 1 0", 20, C.INK, F.MONO)
    pg.line(X, y + 68, X + 118, y + 68, C.INK, 1.5)
    pg.text(X, y + 72, "  0 1 1 1", 20, C.GREEN, F.MONO)
    pg.note(X + 150, y + 6, "1s: 1 − 0 = 1\n2s: 0 − 1, borrow from the 4s (its 1 becomes 0):\n"
            "      2 − 1 = 1\n4s: now 0 − 1, borrow from the 8s (its 1 becomes 0):\n"
            "      2 − 1 = 1\n8s: 0 − 0 = 0", C.INK, 13)
    ch.check(int("1101", 2) - int("110", 2), int("111", 2))
    f.p("So $1101_2 - 110_2 = 111_2$. Check in base 10: $13 - 6 = 7 = 4 + 2 + 1$ ✓.", 13.5, gap=8)
    f.p("{h:Computers don't actually borrow:} they add a negative number stored in \"two's complement\" "
        "form. You'll meet that in Computer Science; on paper, borrowing is fine.", 13.5, C.BROWN)
    ch.check(int("1101", 2) - int("110", 2), 7)


def bytes_(ch):
    f = flow(ch)
    sec(f, "Bits, bytes and why a kilobyte might be 1024", room=280)
    f.p("A group of {B:8 bits} is a {B:byte}. With 8 wheels of 0/1 you can make $2^8 = 256$ different "
        "patterns (00000000 to 11111111, i.e. 0 to 255). That's why colour values stop at 255.", 14, gap=8)
    ch.term("byte", "8 bits; can store 2⁸ = 256 different values (0-255)")
    ch.check(2 ** 8, 256)
    f.p("Computers like powers of 2, and $2^{10} = 1024$ is close to 1000. So memory sizes were "
        "traditionally counted in 1024s: 1 KB = 1024 bytes. Newer notation calls that a {B:kibibyte} "
        "(KiB) and keeps kB = 1000 bytes (the metric prefix from Chapter 5).", 14)
    ch.check(2 ** 10, 1024)


def any_base(ch):
    f = flow(ch)
    sec(f, "Any base at all", room=260)
    f.p("In base b the digits go from 0 to b − 1, and the columns are worth $b^0 = 1$, $b^1$, "
        "$b^2$, ... . For example, base 3 has digits 0, 1, 2 and columns 1, 3, 9, 27:", 14, gap=6)
    step(f, r"2101_3=2\times27+1\times9+0\times3+1\times1", "column values are powers of 3", size=18)
    step(f, r"=54+9+0+1=64", "", size=18, color=C.GREEN)
    ch.check(int("2101", 3), 64)
    f.p("{R:Watch out:} a digit can never equal the base. \"2\" can't appear in binary, and \"8\" can't "
        "appear in octal, just as there's no single digit for ten in base 10.", 13.5)


def find_unknown(ch):
    f = flow(ch)
    sec(f, "Find the unknown: missing digits and missing bases", room=520)
    f.p("Some questions give the value and hide a digit, or hide the base itself. Both are solved by "
        "writing the place-value sum with a letter in it:", 13.5, gap=6)
    rule_box(f, "missing digit or base", [
        "Write the number as (digit × column value) added up, using a letter for the unknown digit, "
        "or $b$ for an unknown base (columns $1, b, b^2, \\dots$).",
        "Set that sum equal to the value you are given, and solve.",
        "Check the answer makes sense: a digit must be a whole number from 0 to $b-1$; a base must be "
        "a whole number {B:bigger than every digit} in the number.",
    ], C.BLUE, numbered=True, tag="PROCEDURE")
    ex(f, "$101x_2=11_{10}$. Find the digit $x$.")
    step(f, r"1\times8+0\times4+1\times2+x\times1=11", "columns 8, 4, 2, 1", size=18)
    step(f, r"10+x=11\ \Rightarrow\ x=1", "a valid binary digit ✓", size=19, color=C.GREEN)
    ch.check(int("1011", 2), 11)
    ex(f, "in which base is $21=7_{10}$?")
    step(f, r"2\times b+1\times1=7", "columns b and 1", size=19)
    step(f, r"2b=6\ \Rightarrow\ b=3", "digits 2 and 1 are both less than 3 ✓", size=19, color=C.GREEN)
    ch.check(int("21", 3), 7)
    ex(f, "in which base is $100=49_{10}$?")
    step(f, r"1\times b^2=49\ \Rightarrow\ b=7", "a base is positive, so not −7", size=19, color=C.GREEN)
    ch.check(int("100", 7), 49)
    ex(f, "$3x_{16}=59_{10}$. Find the hex digit $x$.")
    step(f, r"3\times16+x=59\ \Rightarrow\ x=11=B", "11 is written B in hex", size=19, color=C.GREEN)
    ch.check(int("3B", 16), 59)
    ex(f, "$25_b=17_{10}$. Find $b$.")
    step(f, r"2b+5=17\ \Rightarrow\ b=6", "6 is bigger than the digits 2 and 5 ✓", size=19, color=C.GREEN)
    ch.check(int("25", 6), 17)


def common_mistakes(ch):
    f = flow(ch)
    sec(f, "Mistakes to avoid", room=200)
    mistakes(f, [
        (r"200\to8C_{16}", r"200=C8_{16}", "read the remainders from the bottom up"),
        (r"12_{10}=12_{16}", r"12_{10}=C_{16}", "10 to 15 are single hex digits A to F"),
        (r"1_2+1_2=2_2", r"1_2+1_2=10_2", "there is no digit 2 in binary: write 0, carry 1"),
        (r"1101011_2\to1101\,011", r"0110\,1011=6B_{16}", "group the bits from the right, not the left"),
        (r"101_2=101", r"101_2=4+1=5", "the columns are worth 4, 2, 1, not 100, 10, 1; say \"one zero one\""),
    ])
    ch.check(int("C8", 16), 200)
    ch.check(int("101", 2), 5)


def summary(ch):
    f = flow(ch)
    rules_page(ch, f, [
        ("Place value in base b", r"(d_2\,d_1\,d_0)_b=d_2b^2+d_1b+d_0", "digits $0$ to $b-1$; columns $1, b, b^2, \\dots$ from the right"),
        ("Binary", None, "digits 0, 1; columns 1, 2, 4, 8, 16, 32, ..."),
        ("Hexadecimal", None, "digits 0-9, A = 10 ... F = 15; columns 1, 16, 256, ..."),
        ("Octal", None, "digits 0-7; columns 1, 8, 64, ..."),
        ("Base b → decimal", None, "multiply each digit by its column value and add"),
        ("Decimal → base b", None, "divide by $b$ repeatedly until the quotient is 0; read the remainders bottom-up"),
        ("Decimal → binary", None, "or: take the biggest power of 2 that fits, write 1, subtract, repeat"),
        ("Binary ↔ hex", None, "groups of 4 bits from the right (16 = 2⁴)"),
        ("Binary ↔ octal", None, "groups of 3 bits from the right (8 = 2³)"),
        ("Binary addition", r"1+1=10_2,\quad1+1+1=11_2", "right to left, carrying"),
        ("Binary subtraction", r"10_2-1=1", "0 − 1: borrow from the left; it arrives as 2"),
        ("Bits and bytes", r"n\text{ bits}\to2^n\text{ values}", "8 bits = 1 byte = 256 values (0-255)"),
        ("Missing digit or base", None, "write the place-value sum with a letter; solve; check digits < base"),
    ], C.BLUE)


def your_turn(ch):
    f = flow(ch)
    sec(f, "Counters and coins: your turn", fresh=True)
    f.p("Answers in grey.", 13.5, gap=10)
    groups = [
        ("Binary to ordinary", ["1101₂", "100000₂", "11111111₂"], "1. 13   2. 32   3. 255"),
        ("Ordinary to binary", ["9", "25", "100"], "4. 1001   5. 11001   6. 1100100"),
        ("Hexadecimal", ["1A₁₆ in base 10", "200 in hex", "What colour is #0000FF?", "Write 10110111₂ in hex"],
         "7. 26   8. C8   9. pure blue   10. B7"),
        ("Arithmetic", ["101₂ + 11₂", "1111₂ + 1₂", "How many values can 4 bits store?"],
         "11. 1000₂ (5 + 3 = 8)   12. 10000₂   13. 2⁴ = 16"),
        ("Other bases", ["122₃ in base 10", "Why is 128₈ not a valid octal number?"],
         "14. 17   15. octal has no digit 8"),
        ("More conversions", ["100 in octal", "1110₂ − 101₂", "3C₁₆ in binary", "1101011₂ in octal"],
         "16. 144₈ (100 ÷ 8 = 12 r 4, 12 ÷ 8 = 1 r 4, 1 ÷ 8 = 0 r 1)   17. 1001₂ (14 − 5 = 9)   "
         "18. 111100₂ (0011 1100)   19. 153₈ (001 101 011)"),
        ("Find the unknown", ["101x₂ = 11. Find the digit x.", "In which base is 21 = 7?",
                              "In which base is 100 = 36?", "3x₁₆ = 59. Find the hex digit x.",
                              "25 in base b equals 17. Find b.", "1x1₂ = 7. Find x."],
         "20. x = 1 (8 + 2 + x = 11)   21. base 3 (2b + 1 = 7)   22. base 6 (b² = 36)   "
         "23. x = B (48 + x = 59, x = 11)   24. b = 6 (2b + 5 = 17)   25. x = 1 (4 + 2x + 1 = 7)"),
    ]
    n = 1
    for title, qs, ans in groups:
        f.need(30 + 20 * len(qs) + 26)
        f.text(title, 14, C.BLUE, F.BOLD, gap=6)
        for q in qs:
            f.text(f"{n}. {q}", 13, gap=5, x=L + 14)
            n += 1
        f.text(ans, 10, C.GREY, gap=16, x=L + 14)
    for g, e in [(int("1101", 2), 13), (int("100000", 2), 32), (format(25, "b"), "11001"),
                 (format(100, "b"), "1100100"), (int("1A", 16), 26), (format(200, "X"), "C8"),
                 (format(int("10110111", 2), "X"), "B7"), (int("101", 2) + int("11", 2), 8), (int("122", 3), 17)]:
        ch.check(g, e)
    ch.check_true(format(100, "o") == "144")
    ch.check_true(format(int("1110", 2) - int("101", 2), "b") == "1001")
    ch.check_true(format(int("3C", 16), "b") == "111100")
    ch.check_true(format(int("1101011", 2), "o") == "153")
    b_ = sp.symbols("b_", positive=True)
    ch.check(sp.solve(8 + 2 + b_ - 11, b_), [1])
    ch.check(sp.solve(2 * b_ + 1 - 7, b_), [3])
    ch.check(sp.solve(b_ ** 2 - 36, b_), [6])
    ch.check(int("3B", 16), 59)
    ch.check(sp.solve(2 * b_ + 5 - 17, b_), [6])
    ch.check(sp.solve(4 + 2 * b_ + 1 - 7, b_), [1])


def build(ch):
    ch.bg = PAPER
    title_page(ch)
    base_ten(ch)
    binary_count(ch)
    to_decimal(ch)
    to_binary(ch)
    octal_hex(ch)
    to_any(ch)
    adding(ch)
    subtracting(ch)
    bytes_(ch)
    any_base(ch)
    find_unknown(ch)
    common_mistakes(ch)
    summary(ch)
    your_turn(ch)
