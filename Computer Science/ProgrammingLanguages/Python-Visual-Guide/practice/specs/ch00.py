EXERCISES = [
    dict(
        id="0.1", kind="build", title="Warm-up: sort without sorted()",
        task="""
        Write `sort_copy(xs)` that returns a **new** list with the items of `xs` in ascending order.

        Rules: don't call `sorted()` or `list.sort()` (this one is about the moves, not the library),
        and don't change the list you were given.

        Any algorithm is fine: insertion, selection, merge, quick... The tests check the result on
        hundreds of random lists, not your method.
        """,
        stub='''
        def sort_copy(xs):
            """Return a new list with the items of xs in ascending order."""
            ...
        ''',
        tests='''
        def test_sorts_hundreds_of_random_lists(m):
            for xs in rand_lists():
                equal(m.sort_copy(xs), sorted(xs), f"sort_copy({xs})")

        def test_does_not_change_the_input(m):
            xs = [3, 1, 2]
            m.sort_copy(xs)
            equal(xs, [3, 1, 2], "the original list")

        def test_does_not_use_the_library_sort(m):
            check(not uses_name(m, "sorted") and not uses_name(m, "sort"),
                  "this warm-up asks you to sort by hand (no sorted() or .sort())")
        ''',
        alts={
            "insertion sort": ('''
                def sort_copy(xs):
                    out = list(xs)
                    for i in range(1, len(out)):
                        j = i
                        while j and out[j - 1] > out[j]:
                            out[j - 1], out[j] = out[j], out[j - 1]
                            j -= 1
                    return out
            ''', "O(n^2) comparisons but very fast on short or nearly-sorted lists; works in place on the copy."),
            "merge sort": ('''
                def sort_copy(xs):
                    if len(xs) <= 1:
                        return list(xs)
                    mid = len(xs) // 2
                    left, right = sort_copy(xs[:mid]), sort_copy(xs[mid:])
                    out, i, j = [], 0, 0
                    while i < len(left) and j < len(right):
                        if left[i] <= right[j]:
                            out.append(left[i]); i += 1
                        else:
                            out.append(right[j]); j += 1
                    return out + left[i:] + right[j:]
            ''', "O(n log n) always, stable, but builds many small lists (extra memory). Recursion depth is log n."),
        },
    ),
]

DRILLS = [
    dict(kind="predict", code="print(sorted('banana'))"),
    dict(kind="predict", code="xs = [3, 1, 2]\nys = xs\nys.append(0)\nprint(xs)",
         why="ys = xs makes a second name for the same list (Chapter 3)."),
    dict(kind="recall", q="Which command runs the tests for exercise 12.3?", a="python -m practice check 12.3"),
]
