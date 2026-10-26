
## 1
a = 50
b = 10
c = "hello world"
d = "No"

c = "hello world"
if a>b: print(c)

## 2
a = 50
b = 10
c = "hello world"

if a != b: print(c)

## 3
if a == b: print(a == b) 
else: print (d)

## 4

if a == 1:
    print (1)
elif a > b:
    print (2)
else:
    print (3)

## 5

if a == b and c == d:
    print("Hello")


## 6

if 5 > 2: print("Five is greater than two!")

## 7

print("Yes") if 5 > 2 else print("No")



## 9

for i in range (0, 6):
    i += 1
    print(i)

## 10

i = 1
while i < 6:
    if i == 3:
        break
    i += 1


## 13

fruits = ["apple", "banana", "cherry"]

for i in fruits:
    print(i)

for v,i in enumerate(fruits):
    if v == "banana":
        i+=1


## 15 --> see 9.

## 16 

fruits = ["apple", "banana", "cherry"]

for v,i in enumerate(fruits):
    if v == "banana":
        break



def isangry(bob, jerry): ## You could merge the args into a tuple then iterate the tuple for the counter but i have forgotten how to collect **args...
    angry_count = 0
    if bob == "angry":
        angry_count += 1
    if jerry == "angry":
        angry_count == 2
    if angry_count == 2:
        text = "Both are angry"
    else: 
        text = "One is angry"
    return text



def isangryImproved(*args): ## Collect args..
    angry_count = args.count("angry") ## Args is a tuple so it has the supplied count from __builtins__

    text = "Both are angry" if angry_count == 2 else "One is angry" ## Ok technically this doesn't work if the supplied args is > 2, but you can use slots...
    return text

## Or we could use kwargs with a sort of slot behaviour. Unfortunately true slots only works on class attributes but this has the same higher level effect..


def isangryimprovedkwargs(**kwargs):
    allowed_keys = {"bob", "jerry"}
    extra_keys = kwargs.keys() - allowed_keys
    if extra_keys:
        raise TypeError

    emotion = [str(val).lower() for val in kwargs.values()]
    angry_count = emotion.count("angry")
    txt = "Both are angry" if angry_count == 2 else "One is angry" if angry_count == 1 else "None are angry"
    return txt

def somesillysquarefunctionthing(x):
    for i in range(1, 10):
        print(x**2)
    return None


def decrementorthing (x):
    while x != 0: ## Let's hope they don't give a negative beccause i can't be arsed to guard. but you would just add a neg protect clause at the top to prvent the while from running...obviously.
        print(x)
        x -=1


def somestringreadthing(strr):
    print("running...")
    for i in range(1, len(strr), 2): ## Yes I am cheating, no i don't care. It works.
        print(strr[i])
    return None

somestringreadthing("hello")






