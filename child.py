from toolz import partial

def func(c1,c2,c3):
    print("RUNNING!")
    return c1,c2,c3

c1 = partial(func, "bob")
c1("sarah","OTHER MOTHERFUCKERRRRRRRRR")
