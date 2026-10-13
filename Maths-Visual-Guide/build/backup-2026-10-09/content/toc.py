"""Chapter list shared by the book map, lecture guide and appendices."""
from generator import canvas as C

PARTS = [
    ("Part 1", "Numbers", C.ORANGE, range(1, 8)),
    ("Part 2", "Algebra", C.BLUE, range(8, 18)),
    ("Part 3", "Functions and graphs", C.GREEN, range(18, 23)),
    ("Part 4", "Data and chance", C.PURPLE, range(23, 27)),
    ("Part 5", "Geometry and trigonometry", C.TEAL, range(27, 34)),
    ("Part 6", "Calculus", C.RED, range(34, 39)),
]

CHAPTERS = {
    1: "Whole numbers", 2: "Fractions", 3: "Decimals", 4: "Percentage and ratio",
    5: "Measurement", 6: "Sets", 7: "Logic",
    8: "Algebra", 9: "Indices (powers)", 10: "Number bases", 11: "Simplifying",
    12: "Factorisation", 13: "Algebraic fractions", 14: "Transposing formulae",
    15: "Solving equations", 16: "Matrices", 17: "Sequences and series",
    18: "Functions", 19: "Graphs of functions", 20: "The straight line",
    21: "The exponential function", 22: "Logarithms",
    23: "Tables and charts", 24: "Statistics", 25: "Probability and Bayes",
    26: "The Normal distribution",
    27: "Angles", 28: "Intro to trigonometry", 29: "Trig graphs", 30: "Trig identities and equations",
    31: "Solving triangles", 32: "Vectors", 33: "Polar coordinates",
    34: "Gradients of curves", 35: "Chain, product, quotient", 36: "Integration and areas",
    37: "Parts and substitution", 38: "Partial differentiation",
}

LECTURES = [
    ("L01", "Combining fractions and mathematical writing", [1, 2, 3]),
    ("L02", "Algebraic manipulation", [8, 11, 12, 14]),
    ("L03", "Ratios and proportions", [4, 15]),
    ("L04", "Data and descriptive statistics", [24]),
    ("L05", "Graphical analysis", [23]),
    ("L06", "Trigonometry", [27, 28, 29, 30, 31]),
    ("L07", "Powers, logs and graphing", [9, 19, 20, 21, 22]),
    ("L08", "Probability and Bayes", [25]),
    ("L09", "The Normal distribution", [26]),
    ("L10", "Vectors and scalars", [32]),
    ("L11", "Polar coordinates", [30, 33]),
    ("L12", "Matrices and systems of equations", [15, 16]),
    ("L13", "Functions and series", [6, 17, 18]),
    ("L14", "Differentiation and curves", [15, 20, 34]),
    ("L15", "Further differentiation", [35]),
    ("L16", "Introduction to integration", [36]),
    ("L17", "Further integration", [37]),
]
