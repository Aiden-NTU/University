x = dict(name = "John", age = 36, country = "Norway") ## Key-structured mutable ordered
print(x)
x = list(("John", 36, "Norway")) ## Mutable
print(x)
x = set(("John", 36, "Norway")) ## Mutable deduped variant of list
print(x)
x = tuple(("John", 36, "Norway")) ## Immutable variant of list, allows dupes
print(x)
x = frozenset(("John", 36, "Norway")) ## Immutable variant of set
print(x)
## x = frozendict(("John", 36, "Norway"))  ## For sys.version_info >= (3, 15): - See builtins.pyi, restricted below this version.

thisdict = {
    "brand": "ford",
    "model": "mustang",
    "year": 1964,
    "colours": ["red", "white", "blue"]
}

## Search for model key using List Comprehension

key = [k for k in thisdict if k == "model" and thisdict.get(k) == "mustang"]
print(f"key is here:{key}")

## Essentially :
## Tuple --> Frozen list
## Frozenset ---> Frozen set..
## FrozenDict ---> Frozen dictionary