"""Part 0 - Start here. Designed as a travel phrasebook for the language of maths."""
from generator import canvas as C
from generator import fonts as F
from content.toc import CHAPTERS, LECTURES, PARTS

ORDER = 0
NUM = "Part 0"
TITLE = "Start here: a phrasebook for the language of maths"
SHORT = "Start here"
SLUG = "Start-Here"
ACCENT = C.BROWN
REQUIRES = []
INTRODUCES = ["reading-maths", "equals-sign", "inequality-symbols", "letters-stand-for-numbers",
              "multiplication-notation", "brackets-first", "square-and-root-words", "pi-word"]

CREAM = "#fffaf0"
L, R = 50, 545


def page(ch):
    return ch.new_page(bg=CREAM)


def tab(pg, y, label, color=ACCENT):
    """Phrasebook section tab: a coloured tongue at the left edge."""
    w = pg.twidth(label, 12, F.BOLD) + 30
    pg.rect(0, y, w + 20, 26, color, 0, fillcolor=color, r=0)
    pg.text(20, y + 5, label, 12, "#ffffff", F.BOLD)


def phrase(f, english, latex, say=None, size=19, note=None):
    """One phrasebook line: English on the left, maths on the right, 'say it' under."""
    pg = f.pg
    ew = 235
    eh = pg.rich_h(english, ew, 13)
    w, h, _ = pg.eq_size(latex, size)
    sh = 22 if say else 0
    nh = pg.rich_h(note, 470, 12) + 4 if note else 0
    row = max(eh, h + sh) + nh + 16
    y = f.reserve(row)
    pg = f.pg
    pg.rich(L, y + 6, english, ew, 13)
    lx0 = L + min(ew, pg.rich_w(english, 13)) + 8
    pg.line(lx0, y + 17, 360, y + 17, "#c9b99a", 1.0, dash=(1.5, 3.5))
    pg.eq(452, y + 4, latex, size, align="center")
    if say:
        pg.note(452, y + 6 + h, "say: " + say, C.BROWN, 15, align="center")
    if note:
        pg.rich(L + 14, y + max(eh, h + sh) + 10, note, 470, 12, C.GREY)
    pg.line(L, y + row - 3, R, y + row - 3, "#eadfc8", 0.8)


def scales(pg, cx, y, left, right, tilt=0.0, lcol=C.BLUE, rcol=C.ORANGE):
    """A see-saw balance with a formula on each pan. tilt>0 means left pan lower."""
    beam = 170
    pg.poly([(cx - 22, y + 150), (cx, y + 40), (cx + 22, y + 150)], C.BROWN, 2.2)
    pg.line(cx - 45, y + 150, cx + 45, y + 150, C.BROWN, 3)
    lx, rx = cx - beam, cx + beam
    ly, ry = y + 40 + tilt, y + 40 - tilt
    pg.line(lx, ly, rx, ry, C.BROWN, 3)
    pg.dot(cx, y + 40, 4, C.BROWN)
    for px, py, lab, col in ((lx, ly, left, lcol), (rx, ry, right, rcol)):
        pg.line(px, py, px - 40, py + 45, "#9a8a70", 1)
        pg.line(px, py, px + 40, py + 45, "#9a8a70", 1)
        pg.poly([(px - 55, py + 45), (px + 55, py + 45), (px + 40, py + 58), (px - 40, py + 58)],
                C.BROWN, 1.6, closed=True)
        pg.eq(px, py + 42, lab, 20, col, align="center", valign="baseline")


def labelled(f, latex, parts, say, size=34, levels=2):
    """A formula with a label hanging under each chosen part (fx = fraction across)."""
    w, h, _ = f.pg.eq_size(latex, size)
    say_m = "{y:say:} {h:" + say + "}" if say else ""
    sh = f.pg.rich_h(say_m, 490, 14) if say else 0
    y = f.reserve(h + (74 + sh if say else 50 + 24 * levels))
    pg = f.pg
    x0 = 297 - w / 2
    pg.eq(x0, y, latex, size)
    for i, (fx, txt, col) in enumerate(parts):
        px = x0 + fx * w
        ty = y + h + 18 + (i % levels) * 24
        pg.line(px, y + h + 2, px, ty - 2, col, 1)
        pg.note(px, ty, txt, col, 16, align="center")
    if say:
        pg.rich(L, y + h + 70, say_m, 490, 14, C.BROWN)


# --------------------------------------------------------------------------- pages
def cover(ch):
    pg = page(ch)
    # the phrasebook itself
    pg.rect(130, 40, 335, 215, C.BROWN, 2.5, fillcolor="#f3e3c7", r=16)
    pg.rect(145, 55, 305, 185, "#c9a877", 1.2, r=10, dash=(4, 3))
    pg.text(297, 72, "PHRASEBOOK", 13, C.BROWN, F.BOLD, align="center")
    pg.text(297, 92, "The Language", 28, C.INK, F.BOLD, align="center")
    pg.text(297, 127, "of Maths", 28, C.INK, F.BOLD, align="center")
    pg.note(297, 166, "for people who were never taught the words", C.BROWN, 19, align="center")
    pg.eq(220, 205, r"2+3=5", 19, C.BLUE, align="center")
    pg.arrow(262, 215, 314, 215, C.GREY, 1.2, both=True, head=5)
    pg.note(385, 201, "two add three is five", C.BLUE, 18, align="center")

    f = ch.flow(top=280)
    f.text("Before any maths: a promise", 22, C.BROWN, F.BOLD, gap=12)
    f.p("If maths has always looked like a wall of strange marks, that is **not** because you are "
        "bad at it. Maths is written in a language, a very squashed-up, shorthand language, and "
        "almost every book expects you to speak it already. Nobody ever sat you down and taught "
        "you the words.", 14, gap=12)
    f.p("This part does exactly that. Think of it as a {W:phrasebook} for a country you are about "
        "to visit. You do not need to be fluent. You only need to be able to read the signs, and "
        "to know what to say when someone points at one.", 14, gap=12)
    f.p("There are no sums to do in this part. There is only reading.", 14, C.BROWN, gap=18)
    f.text("How the rest of this book works", 16, C.INK, F.BOLD, gap=8)
    points = [
        "Each section starts with a {b:boxed RULE} (or a numbered PROCEDURE) that says exactly what "
        "to do, then {o:worked examples}, then a picture only if it helps. Every chapter ends with "
        "a {g:rules page} listing all its rules, and the {r:Formula Pages} at the back collect them all.",
        "In worked examples, each line changes {o:only one thing}. The part that changed is marked, "
        "and a {r:handwritten note} says why you are allowed to do it.",
        "Before you are asked to trust a rule, it is {g:tested with real numbers} so you can watch "
        "it work.",
        "This is a Xournal++ file, so {p:write on it}. Circle what you don't get. Highlight what "
        "you do.",
        "Take it slowly. {b:Ten minutes on one line is normal.} Mathematicians do it too.",
    ]
    for s in points:
        f.bullet(s, 13)


def shorthand(ch):
    pg = page(ch)
    tab(pg, 40, "Lesson 1 · Maths is shorthand")
    f = ch.flow(top=84)
    f.p("Here is a sentence in ordinary English. Read it slowly. Then follow the arrows: each "
        "coloured chunk gets turned into maths shorthand.", 14, gap=14)
    y = f.reserve(40)
    chunks = [("I think of a number,", C.BLUE), ("double it,", C.ORANGE),
              ("add three,", C.PURPLE), ("and I get eleven.", C.GREEN)]
    x = L
    centres = []
    for s, col in chunks:
        w = pg.twidth(s, 15)
        pg.rect(x - 4, y - 3, w + 8, 26, col, 1.3, fillcolor=C.LIGHT[col], r=6)
        pg.text(x, y + 1, s, 15, col)
        centres.append((x + w / 2, col))
        x += w + 18
    f.gap(10)
    y = f.reserve(128)
    mx = [(150, r"\blu{x}", "x is a letter standing\nfor the mystery number"),
          (255, r"\org{2x}", "2x means\n2 times x"),
          (355, r"\pur{+\,3}", "add 3"),
          (460, r"\grn{=\,11}", "is the same\nvalue as 11")]
    for (cx, col), (tx, lat, why) in zip(centres, mx):
        pg.arrow(cx, y - 8, tx, y + 38, col, 1.4, bend=0.1)
        pg.eq(tx, y + 44, lat, 24, align="center")
        pg.text(tx, y + 80, why, 10.5, C.GREY, align="center")
    f.gap(8)
    f.p("Put the pieces together and the whole sentence becomes:", 14, gap=8)
    f.eq(r"\org{2x}\pur{\,+\,3}\grn{\,=\,11}", 30, gap=8)
    f.p("That is all an equation is: a sentence, written in shorthand. The maths version is shorter, "
        "but it says {B:exactly the same thing} as the English. Every time you see maths, there is an "
        "English sentence hiding inside it. Your job is only to find that sentence.", 14, gap=16)
    f.p("It works the other way too. Here is a piece of maths you might see in a shop:", 14, gap=6)
    labelled(f, r"\blu{C}=\org{p}\times\pur{n}",
             [(0.08, "the total cost", C.BLUE), (0.52, "the price of one", C.ORANGE),
              (0.93, "how many you buy", C.PURPLE)], None, 30, levels=3)
    f.p("So  $C = p \\times n$  is read out as: \"the total cost is the price of one thing times the "
        "number of things you buy\". The letters are just the first letters of the words.", 14, gap=14)
    f.p("{r:Why bother with shorthand?}  Because the long English sentences get very tiring very "
        "quickly, and because the short version is easier to {b:move around}. Later in this book "
        "you will learn to shuffle shorthand sentences around to find missing numbers. You cannot "
        "do that easily with paragraphs of English.", 13, gap=6)


def doing_things(ch):
    pg = page(ch)
    tab(pg, 40, "Lesson 2 · Doing things to numbers")
    f = ch.flow(top=84)
    f.p("Every line below is one phrase. The {b:English} is on the left, the {W:maths} is on the "
        "right, and underneath is how people actually {h:say it out loud}.", 13, gap=10)
    phrase(f, "Put 3 and 4 together.", r"3+4", "three plus four")
    phrase(f, "Start with 7 and take 2 away.", r"7-2", "seven minus two")
    phrase(f, "Three lots of four (4 + 4 + 4).", r"3\times 4", "three times four",
           note="The times sign has disguises. All of these mean 3 times 4:  $3\\times4$,  "
                "$3\\cdot4$,  $3*4$ (on computers),  $3(4)$  and  $(3)(4)$.")
    phrase(f, "Share 12 equally into 3 groups.", r"12\div 3", "twelve divided by three",
           note="Division also has disguises:  $12\\div3$,  $12/3$  and  $\\frac{12}{3}$.  "
                "The line in a fraction {B:is} a division sign.")
    phrase(f, "5 multiplied by itself (5 times 5).", r"5^2", "five squared",
           note="The small raised 2 means \"multiply two copies together\": $5^2 = 5\\times5 = 25$. "
                "It is {R:not} 5 times 2. (All of Chapter 9 is about these.)")
    phrase(f, "Which number, times itself, makes 9?", r"\sqrt{9}", "the square root of nine",
           note="The answer is 3, because $3\\times3=9$. So $\\sqrt{9}=3$. A square root "
                "{B:undoes} squaring.")
    phrase(f, "Four below zero (like a temperature of minus 4 degrees).", r"-4", "minus four / negative four")
    f.gap(4)
    f.p("{r:Watch out:} the letter  $x$  and the times sign  $\\times$  look almost the same. "
        "That is why, once letters appear, people usually {b:leave the times sign out}. You will see "
        "this on the next pages.", 13)


def equals(ch):
    pg = page(ch)
    tab(pg, 40, "Lesson 3 · The = sign is a balance")
    f = ch.flow(top=84)
    f.p("Most people learn at school that \"=\" means {r:\"and the answer is...\"}. That idea causes "
        "a huge amount of confusion later on. Here is what it really means:", 14, gap=10)
    f.p("{B:=}  means  {B:\"the thing on the left has exactly the same value as the thing on the "
        "right\"}. It is a {B:balanced see-saw}.", 15, gap=6)
    y = f.reserve(200)
    scales(pg, 297, y, r"3+4", r"7")
    pg.note(297, y + 170, "same value on both sides, so it balances", C.BROWN, 18, align="center")
    f.p("Because it is a balance, it does not matter which side is which:", 14, gap=6)
    y = f.reserve(40)
    pg = f.pg
    for i, lat in enumerate([r"3+4=7", r"7=3+4", r"3+4=2+5"]):
        cx = 110 + i * 175
        w, _ = pg.eq(cx, y, lat, 22, align="center")
        pg.tick(cx + w / 2 + 8, y + 2, 14)
    f.p("All three are {g:true}. The last one surprises people: there is no \"answer\" on the right "
        "at all, just two different ways of making 7. They balance, so the = sign is correct.", 13,
        gap=16)
    f.p("{r:Why this matters later:} when you rearrange formulas (Chapter 14) and solve equations "
        "(Chapter 15), the whole trick is to keep the see-saw balanced. Whatever you do to one side, "
        "you must do to the other side too.", 13)


def equals2(ch):
    pg = page(ch)
    f = ch.flow(top=52)
    f.text("The rest of the balance family", 18, C.BROWN, F.BOLD, gap=6)
    phrase(f, "not the same value", r"3\neq 5", "three is not equal to five")
    phrase(f, "smaller than", r"3<8", "three is less than eight")
    phrase(f, "bigger than", r"8>3", "eight is greater than three")
    phrase(f, "smaller than, or maybe equal to", r"x\leq 10", "x is less than or equal to ten")
    phrase(f, "bigger than, or maybe equal to", r"x\geq 0", "x is greater than or equal to zero")
    phrase(f, "roughly the same", r"\pi\approx 3.14", "pi is approximately three point one four")
    f.gap(6)
    f.text("A trick for  <  and  >", 16, C.INK, F.BOLD, gap=6)
    f.p("The sign is a mouth. It always opens {b:wide towards the bigger number} and points its "
        "narrow tip at the smaller one. (It is \"greedy\": it wants to eat the bigger number.)", 14,
        gap=8)
    y = f.reserve(115)
    pg = f.pg
    for cx, a, s, b in ((160, "3", "<", "8"), (430, "8", ">", "3")):
        pg.text(cx - 70, y + 20, a, 44, C.INK, F.BOLD)
        pg.text(cx + 40, y + 20, b, 44, C.INK, F.BOLD)
        if s == "<":
            pg.poly([(cx + 22, y + 22), (cx - 18, y + 45), (cx + 22, y + 68)], C.ORANGE, 4)
            pg.note(cx + 55, y + 82, "wide end\nat the 8", C.ORANGE, 15)
        else:
            pg.poly([(cx - 18, y + 22), (cx + 22, y + 45), (cx - 18, y + 68)], C.ORANGE, 4)
            pg.note(cx - 90, y + 82, "wide end\nat the 8", C.ORANGE, 15)
    f.gap(10)
    f.p("Your Lecture 1 slides also use three rarer members of the family:", 13, gap=4)
    f.bullet("$1000000\\gg 2$   {h:say: is much greater than.}  Far, far bigger.", 13)
    f.bullet("$0.001\\ll 5$   {h:say: is much less than.}  Far, far smaller.", 13)
    f.bullet("$a+b\\equiv b+a$   {h:say: is identically equal to.}  Three lines instead of two means "
             "\"this is not just true for one number, it is {B:always} true, whatever numbers you use\".",
             13)


def letters(ch):
    pg = page(ch)
    tab(pg, 40, "Lesson 4 · Letters are hidden numbers")
    f = ch.flow(top=84)
    f.p("This is the step that loses most people, so let's go very slowly.", 14, gap=8)
    f.p("A {B:letter} in maths is {B:a number wearing a disguise}. Picture a sealed envelope with a "
        "number written on a card inside. We cannot see the number, so we write a letter on the "
        "outside of the envelope to talk about it.", 14, gap=6)
    y = f.reserve(130)
    # envelope
    ex, ey = 80, y + 10
    pg.rect(ex, ey, 150, 95, C.BROWN, 2, fillcolor="#f6e7cc")
    pg.poly([(ex, ey), (ex + 75, ey + 52), (ex + 150, ey)], C.BROWN, 2)
    pg.eq(ex + 75, ey + 58, r"x", 30, C.BLUE, align="center")
    pg.note(ex + 170, ey + 8, "on the outside: a letter", C.BLUE, 18)
    pg.rect(ex + 330, ey + 10, 70, 80, C.GREY, 1.2, fillcolor="#ffffff", r=4)
    pg.text(ex + 365, ey + 30, "4", 34, C.GREEN, F.BOLD, align="center")
    pg.note(ex + 170, ey + 50, "inside: an actual number", C.GREEN, 18)
    pg.arrow(ex + 318, ey + 70, ex + 152, ey + 72, C.GREY, 1.1, bend=-0.15, dash=(4, 3))
    f.p("Letters do one of two jobs:", 14, gap=4)
    f.p("{b:1. A mystery number.}  In  $2x+3=11$  there is exactly one number hiding in the envelope. "
        "(It's 4: double 4 is 8, add 3 is 11.) Finding it is called {b:solving}.", 13, x=L + 16, w=475,
        gap=6)
    f.p("{o:2. A number that can change.}  In  $C = p\\times n$  the letters change from shop to shop "
        "and day to day. The shorthand is a {o:recipe} that works whatever the numbers are. A letter "
        "used like this is called a {o:variable} (because it can vary).", 13, x=L + 16, w=475, gap=12)
    f.text("How letters are written (the rules nobody tells you)", 16, C.INK, F.BOLD, gap=4)
    phrase(f, "3 times x", r"3x", "three x", note="The times sign is left out. The number is written "
           "{B:first}: $3x$, never $x3$.")
    phrase(f, "x times y", r"xy", "x y", note="Two letters side by side are multiplied.")
    phrase(f, "x times x", r"x^2", "x squared", note="{R:Not} $2x$. Check with a number: if $x=5$, "
           "then $x^2=5\\times5=25$ but $2x=2\\times5=10$. Different!")


def letters2(ch):
    pg = page(ch)
    f = ch.flow(top=52)
    f.text("Opening the envelope", 18, C.BROWN, F.BOLD, gap=6)
    f.p("If someone tells you what number is inside, you can replace the letter with that number and "
        "work out the value. This is called {b:substituting}. Let's say  $x = 4$.", 14, gap=10)
    rows = [
        (r"3x", r"3\times\org{4}", r"12", "3x means 3 times x, and x is 4"),
        (r"x^2", r"\org{4}\times\org{4}", r"16", "x squared means x times x"),
        (r"2x+3", r"2\times\org{4}+3", r"11", "double 4 is 8, then add 3"),
        (r"\frac{x}{2}", r"\frac{\org{4}}{2}", r"2", "4 shared into 2 is 2"),
    ]
    for a, b, c, why in rows:
        y = f.reserve(56)
        pg = f.pg
        pg.eq(95, y + 6, a, 22, C.BLUE, align="center")
        pg.arrow(135, y + 18, 175, y + 18, C.GREY, 1.2, head=5)
        pg.eq(250, y + 6, b, 22, align="center")
        pg.arrow(325, y + 18, 360, y + 18, C.GREY, 1.2, head=5)
        pg.eq(385, y + 6, c, 22, C.GREEN, align="center")
        pg.note(425, y + 6, why, C.RED, 15, w=125)
    f.gap(10)
    f.p("{o:The orange 4s} show where the envelope was opened. Nothing else changed. That will be "
        "true all through this book: {o:orange} marks the part of a line that just changed.", 13,
        gap=18)
    f.text("Why use letters at all?", 18, C.BROWN, F.BOLD, gap=6)
    f.p("Because a letter lets you say something is true {B:for every number at once}. For example, "
        "try adding two numbers in either order:", 14, gap=6)
    y = f.reserve(34)
    pg = f.pg
    for i, lat in enumerate([r"2+5=5+2", r"10+1=1+10", r"7+30=30+7"]):
        pg.eq(130 + i * 170, y, lat, 19, align="center")
    f.p("You could write examples forever. Or you can write it once, with letters:", 14, gap=4)
    f.eq(r"a+b=b+a", 30, C.PURPLE, gap=4)
    f.p("and that one short line says: {p:\"whatever two numbers you pick, adding them in either "
        "order gives the same answer\"}. The letters are envelopes that can hold {B:any} number.",
        14)


def brackets(ch):
    pg = page(ch)
    tab(pg, 40, "Lesson 5 · Brackets say \"do me first\"")
    f = ch.flow(top=84)
    f.p("Round brackets  $(\\;)$  are a fence around part of a calculation. Whatever is inside the "
        "fence gets worked out {B:first}, and then treated as a single number.", 14, gap=12)
    f.p("Watch the same three numbers give different answers:", 14, gap=6)
    y = f.reserve(150)
    # left: with brackets
    pg.eq(150, y, r"(\org{2+3})\times 4", 24, align="center")
    pg.eq(150, y + 48, r"\org{5}\times 4", 24, align="center")
    pg.eq(150, y + 96, r"\grn{20}", 26, align="center")
    pg.arrow(150, y + 30, 150, y + 44, C.GREY, 1.1, head=4)
    pg.arrow(150, y + 78, 150, y + 92, C.GREY, 1.1, head=4)
    pg.note(30, y + 30, "fence first:\n2+3 is 5", C.ORANGE, 15)
    # right: without
    pg.eq(420, y, r"2+\org{3\times 4}", 24, align="center")
    pg.eq(420, y + 48, r"2+\org{12}", 24, align="center")
    pg.eq(420, y + 96, r"\grn{14}", 26, align="center")
    pg.arrow(420, y + 30, 420, y + 44, C.GREY, 1.1, head=4)
    pg.arrow(420, y + 78, 420, y + 92, C.GREY, 1.1, head=4)
    pg.note(470, y + 30, "no fence: times\ngoes before plus", C.ORANGE, 15)
    pg.line(297, y - 4, 297, y + 130, "#e0d4bd", 1)
    ch.check("(2+3)*4", 20, "brackets")
    ch.check("2+3*4", 14, "no brackets")
    f.p("Without a fence there is an agreed order (\"times and divide before plus and minus\"). The "
        "full set of rules, and the famous internet argument about  $8\\div2(2+2)$, are in "
        "Chapter 1.", 13, gap=14)
    f.text("A number touching a bracket means multiply", 16, C.INK, F.BOLD, gap=6)
    phrase(f, "4 times the result of (2 + 3)", r"4(2+3)", "four, bracket, two plus three",
           note="There is an invisible times sign between the 4 and the bracket: "
                "$4(2+3) = 4\\times(2+3) = 4\\times 5 = 20$.")
    ch.check("4*(2+3)", 20)
    phrase(f, "3 times the result of (x + 1)", r"3(x+1)", "three, bracket, x plus one",
           note="Same idea with a letter. (How to \"open\" a bracket like this is in Chapter 11.)")


def reading_formulas(ch):
    pg = page(ch)
    tab(pg, 40, "Lesson 6 · Reading a formula out loud")
    f = ch.flow(top=84)
    f.p("A {B:formula} is a shorthand recipe that connects some quantities with letters. You will "
        "meet lots of them. Here is how to read them. Say each one out loud as you read.", 14,
        gap=12)

    labelled(f, r"\blu{y}=\org{m}\pur{x}+\grn{c}",
             [(0.08, "y", C.BLUE), (0.45, "m times x", C.ORANGE), (0.92, "plus c", C.GREEN)],
             "\"y equals m x plus c\"   (m and x are touching, so they are multiplied)")
    labelled(f, r"\blu{v}=\org{u}+\grn{a}\pur{t}",
             [(0.08, "v", C.BLUE), (0.5, "u", C.ORANGE), (0.87, "plus a times t", C.GREEN)],
             "\"v equals u plus a t\"   (this one is from physics: speed after some time)")
    f.gap(4)
    f.p("A Greek letter or two will turn up. The first is {B:$\\pi$}, said \"pie\". It is not a "
        "variable: it is one fixed number, about 3.14159, that has to do with circles (Chapter 5 "
        "explains where it comes from).", 13, gap=8)
    ch.symbol(r"\pi", "pie", "a fixed number, about 3.14159, from circles")
    labelled(f, r"\blu{A}=\org{\pi}\grn{r^2}",
             [(0.12, "A", C.BLUE), (0.55, "pi times", C.ORANGE), (0.88, "r squared", C.GREEN)],
             "\"A equals pie r squared\"   (the area of a circle with radius r)")
    f.gap(6)
    f.text("Two more reading tips", 16, C.INK, F.BOLD, gap=6)
    f.p("{b:Small letters written low}, like  $x_1$  and  $x_2$, are just {b:name tags}. "
        "$x_1$ is said \"x one\" and means \"the first x\". It is {R:not} x times 1.", 13, gap=6)
    f.p("{b:A letter with a little mark}, like  $a'$  (\"a dash\" or \"a prime\") or  $\\bar{x}$  "
        "(\"x bar\"), is a {b:different quantity} related to $a$ or $x$: $\\bar{x}$ is the mean of the "
        "$x$ values (Chapter 24), and $f'(x)$ is the gradient function of $f$ (Chapter 34). Each mark "
        "is explained when it first appears.", 13)


def reading_layers(ch):
    pg = page(ch)
    f = ch.flow(top=52)
    f.text("Formulas with layers: read from the inside out", 18, C.BROWN, F.BOLD, gap=6)
    f.p("Some formulas are built in layers, like an onion. Your Lecture 2 slides use this one, "
        "for how long a pendulum (a swinging weight on a string) takes to swing:", 14, gap=8)
    f.eq(r"T=2\pi\sqrt{\frac{l}{g}}", 32, gap=10)
    f.p("Don't read it left to right. Find the {b:innermost} piece and work outwards:", 14, gap=10)
    layers = [
        (r"\frac{\blu{l}}{\blu{g}}", "layer 1 (the middle):", "\"l divided by g\"", C.BLUE),
        (r"\sqrt{\frac{l}{g}}", "layer 2:", "\"the square root of that\"", C.ORANGE),
        (r"2\pi\sqrt{\frac{l}{g}}", "layer 3:", "\"two pi times that\"", C.PURPLE),
        (r"T=2\pi\sqrt{\frac{l}{g}}", "outside:", "\"T is equal to all of that\"", C.GREEN),
    ]
    for i, (lat, lab, say, col) in enumerate(layers):
        w, h, _ = f.pg.eq_size(lat, 22)
        y = f.reserve(h + 14)
        pg = f.pg
        mid = y + h / 2
        pg.text(L, mid - 8, lab, 12, col, F.BOLD)
        pg.eq(L + 150, y, lat, 22, col)
        pg.note(L + 300, mid - 12, say, col, 17)
    f.gap(8)
    f.p("So the whole thing is read: {h:\"T equals two pi times the square root of l over g\"}.",
        14, C.BROWN, gap=12)
    f.p("You now know how to {b:read} it. How to {b:rearrange} it, for example to find the "
        "length of string needed for a given swing time, is exactly what Chapter 14 teaches, one "
        "layer at a time.", 13, gap=16)


def how_to_read(ch):
    pg = page(ch)
    tab(pg, 40, "Lesson 7 · How to read a page of maths")
    f = ch.flow(top=84)
    f.p("Maths is not read like a novel. A single line can take five minutes, and that is normal: "
        "people who are good at maths read it slowly too. Here is a route to follow whenever a "
        "line looks scary. Walk it one stepping stone at a time.", 14, gap=12)
    steps = [
        ("Say it out loud in English.", "Use the phrases in this part. If you can say it, you can "
         "start to understand it."),
        ("Find the words you don't know.", "The Word Finder at the back of the book lists every "
         "maths word with the page where it is properly explained."),
        ("Find the rule first.", "Each section opens with a boxed RULE or PROCEDURE; read it before "
         "the example. Every chapter's rules are listed together on its rules page, and the Formula "
         "Pages at the back gather them all, with tables of standard derivatives and integrals."),
        ("Put real numbers in.", "Replace each letter with a small, easy number such as 2 or 3 and "
         "work it out. Watching what happens teaches you more than staring."),
        ("Compare each line with the one above.", "Ask: what ONE thing changed? Why was that "
         "allowed? In this book the change is marked and the reason is written beside it."),
        ("Cover the answer and try.", "Hide the rest of a worked example with a sheet of paper and "
         "uncover one line at a time. Guess the next line before you look."),
        ("Stuck? Circle it and move on.", "Mark the line in red on this page. Understanding often "
         "arrives on the second or third visit, after your brain has slept on it."),
    ]
    for i, (head, body) in enumerate(steps):
        bh = f.pg.rich_h(body, 380, 12.5)
        y = f.reserve(max(64, bh + 30))
        pg = f.pg
        sx = 95 + (i % 2) * 22
        pg.ellipse(sx, y + 24, 34, 22, C.BROWN, 1.6, fillcolor="#efdcb8")
        pg.text(sx, y + 12, str(i + 1), 18, C.BROWN, F.BOLD, align="center")
        if i < len(steps) - 1:
            for k in range(3):
                pg.dot(sx + 8 - k * 4 + (11 if i % 2 == 0 else -11) * (k + 1) / 3, y + 52 + k * 6, 1.6,
                       "#c9a877")
        pg.text(160, y + 4, head, 14, C.INK, F.BOLD)
        pg.rich(160, y + 24, body, 380, 12.5, C.INK)


def book_map(ch):
    pg = page(ch)
    tab(pg, 40, "Your map of the book")
    f = ch.flow(top=82)
    f.p("The book is a railway network. Each coloured line is a Part; each stop is a chapter. "
        "Chapters only use ideas from stops {b:earlier} on the network, so if you get lost you can "
        "always travel back. Part 4 only needs Parts 1 and 2, so you can jump to it early.", 13,
        gap=10)
    y0 = f.y + 8
    row_h = 96
    for r, (pname, ptitle, col, chaps) in enumerate(PARTS):
        y = y0 + r * row_h
        chaps = list(chaps)
        n = len(chaps)
        x0, x1 = 80, 530
        pg.text(L - 20, y - 4, f"{pname} · {ptitle}", 12, col, F.BOLD)
        ly = y + 26
        pg.line(x0 - 10, ly, x1 + 10, ly, col, 7, layer=C.UNDER)
        step = (x1 - x0) / max(1, n - 1)
        for i, c in enumerate(chaps):
            sx = x0 + i * step
            pg.circle(sx, ly, 10, col, 2.4, fillcolor="#ffffff")
            pg.text(sx, ly - 7.5, str(c), 10, col, F.BOLD, align="center")
            label = CHAPTERS[c]
            lines = F.wrap(label, F.SANS, 8.5, max(44, 2 * step - 8) if n > 6 else 90)
            drop = 22 if (n > 6 and i % 2 == 1) else 0
            if drop:
                pg.line(sx, ly + 11, sx, ly + 12 + drop, col, 0.8)
            for k, ln in enumerate(lines[:2]):
                pg.text(sx, ly + 14 + drop + k * 10, ln, 8.5, C.INK, align="center")
        if r < len(PARTS) - 1:
            pg.line(x1 + 10, ly, x1 + 10, ly + row_h, "#cccccc", 2, dash=(3, 3))
    f.y = y0 + len(PARTS) * row_h
    f.p("{h:Part 0 (this part) is the ticket office. Everything starts here.}", 13, C.BROWN)


def lecture_guide(ch):
    pg = page(ch)
    tab(pg, 40, "Got a lecture coming up?")
    f = ch.flow(top=82)
    f.p("Each of your NTU maths lectures, and the chapters of this book that prepare you for it. "
        "The numbers in circles are chapter numbers, listed in the order to read them. The colour "
        "tells you which Part of the book (and which line on the railway map) they are in.", 13,
        gap=10)
    for code, title, chaps in LECTURES:
        y = f.reserve(34)
        pg = f.pg
        pg.rect(L, y, 42, 22, ACCENT, 0, fillcolor=ACCENT, r=11)
        pg.text(L + 21, y + 4, code, 11, "#ffffff", F.BOLD, align="center")
        pg.text(L + 52, y + (3 if pg.twidth(title, 11.5) < 265 else -3), title, 11.5, C.INK, w=265)
        x = 380
        pg.text(x - 8, y + 5, "read:", 10, C.GREY, align="right")
        for c in chaps:
            col = next(pc for (_, _, pc, rg) in PARTS if c in rg)
            pg.circle(x + 11, y + 11, 11, col, 1.4, fillcolor=C.LIGHT[col])
            pg.text(x + 11, y + 4.5, str(c), 10.5, col, F.BOLD, align="center")
            x += 30
        pg.line(L, y + 29, R, y + 29, "#eadfc8", 0.7)
    f.gap(8)
    f.p("{r:A note about your slides.} A few slides contain small mistakes (typos in formulas). "
        "When a chapter meets one, it says so and shows the correct version. They are all "
        "collected in the Slide Errata at the back.", 12.5)


def build(ch):
    ch.bg = CREAM
    cover(ch)
    shorthand(ch)
    doing_things(ch)
    equals(ch)
    equals2(ch)
    letters(ch)
    letters2(ch)
    brackets(ch)
    reading_formulas(ch)
    reading_layers(ch)
    how_to_read(ch)
    book_map(ch)
    lecture_guide(ch)
    ch.term("equation", "a maths sentence saying two things have the same value (it has an = sign)", 2)
    ch.term("equals sign (=)", "the two sides have exactly the same value, like a balanced see-saw", 4)
    ch.term("variable", "a letter standing for a number that can change", 6)
    ch.term("substitute", "replace a letter with a number and work out the value", 7)
    ch.term("formula", "a shorthand recipe connecting quantities, written with letters", 9)
    ch.term("square root", "the number which, multiplied by itself, gives the number you started with", 3)
    ch.term("squared", "multiplied by itself: 5 squared is 5 x 5", 3)
    ch.symbol("=", "equals", "has the same value as", 4)
    ch.symbol(r"\neq", "is not equal to", "different value", 4)
    ch.symbol("<", "is less than", "smaller than", 4)
    ch.symbol(">", "is greater than", "bigger than", 4)
    ch.symbol(r"\leq", "less than or equal to", "smaller or the same", 4)
    ch.symbol(r"\geq", "greater than or equal to", "bigger or the same", 4)
    ch.symbol(r"\approx", "approximately equal to", "roughly the same", 4)
    ch.symbol(r"\equiv", "identically equal to", "true for every possible number", 5)
    ch.symbol(r"\gg", "much greater than", "far bigger", 5)
    ch.symbol(r"\sqrt{\;}", "square root of", "which number times itself gives this", 3)
    ch.symbol(r"x^2", "x squared", "x times x", 3)
    ch.symbol(r"x_1", "x one", "a name tag: the first x", 10)
