## CHALLENGE 1

## Find the region with the highest total revenue (units × price), and print its name and total.

sales = [
    {"id": 1, "region": "North", "product": "Widget", "units": 12, "price": 9.99},
    {"id": 2, "region": "South", "product": "Gadget", "units": 5, "price": 24.50},
    {"id": 3, "region": "North", "product": "Gadget", "units": 8, "price": 24.50},
    {"id": 4, "region": "East", "product": "Widget", "units": 20, "price": 9.99},
    {"id": 5, "region": "West", "product": "Doohickey", "units": 3, "price": 99.00},
    {"id": 6, "region": "South", "product": "Widget", "units": 15, "price": 9.99},
    {"id": 7, "region": "East", "product": "Doohickey", "units": 1, "price": 99.00},
    {"id": 8, "region": "North", "product": "Widget", "units": 7, "price": 9.99},
    {"id": 9, "region": "West", "product": "Gadget", "units": 10, "price": 24.50},
    {"id": 10, "region": "South", "product": "Doohickey", "units": 2, "price": 99.00},
]

## Example 1: 
totals = {}

for item in sales:
    region = item["region"]
    totals[region] = totals.get(region, 0) + item["units"] * item["price"]

best = max(totals, key = totals.get)

## CHALLENGE 2 
## Challenge: Find the user with the most total minutes across all their sessions, and print their name and total.

logins = [
    {"user": "ana",   "device": "phone",  "minutes": 34},
    {"user": "ben",   "device": "laptop", "minutes": 120},
    {"user": "ana",   "device": "laptop", "minutes": 75},
    {"user": "cleo",  "device": "phone",  "minutes": 15},
    {"user": "ben",   "device": "phone",  "minutes": 22},
    {"user": "cleo",  "device": "laptop", "minutes": 60},
    {"user": "dev",   "device": "phone",  "minutes": 90},
    {"user": "ana",   "device": "phone",  "minutes": 41},
    {"user": "dev",   "device": "laptop", "minutes": 18},
    {"user": "cleo",  "device": "phone",  "minutes": 48},
]

sums = {}
for login in logins:
    user = login["user"]
    sums[user] = sums.get(user, 0) + login["minutes"]

print(sums)

## CHALLENGE 3
## Find the longest streak of consecutive days where the temperature rose every day, and print its length (in days) and the index where it starts.

temps = [14, 15, 17, 16, 18, 19, 21, 20, 22, 23, 24, 25, 19, 20]

cur_len = 1
cur_start = 0
best_len = 1
best_start = 0



for i in range(1, len(temps)): ## For every value in temperature
    if temps[i] > temps[i-1]:
        cur_len += 1
    else:
        cur_len = 1
        cur_start = i

    if cur_len > best_len:
        best_len = cur_len
        best_start = cur_start


## CHALLENGE 4
## This is the order people signed in at a door. Some people signed in more than once by mistake. 
## Print the name of the first person who signs in a second time, meaning the first moment someone appears who is already on the sheet.

signins = ["mia", "tom", "zoe", "raj", "tom", "mia", "lena", "zoe"]

already_signed_in = set()

for i in signins:
    if i not in already_signed_in:
        already_signed_in.add(i)
    else:
        print(f"{i} is already signed in")
        break


## Challenge 5
## Each pair is a meeting’s start hour and end hour, and they’re not in order. Some overlap, and some touch end-to-start. 
## Your task is to merge them into the blocks of time you’re busy, where overlapping or touching meetings count as one block. 
## Print the blocks in time order.

## AI version:
meetings = [(9, 10), (13, 15), (10, 11), (14, 16), (18, 19), (20, 21), (19, 20)]

meetings = sorted(meetings)

blocks = []
start, previous_end = meetings[0]        # same as start / previous

for s, e in meetings[1:]:
    if s > previous_end:                 # a gap (was: hour != previous + 1)
        blocks.append((start, previous_end))
        start = s
        previous_end = e
    else:
        previous_end = max(previous_end, e)   # extend the stretch

blocks.append((start, previous_end))     # last stretch
print(blocks)

## My best version:

meetings = [(9, 10), (13, 15), (10, 11), (14, 16), (18, 19), (20, 21), (19, 20)]

blocks = []
start, end = None, None

print(sorted(meetings)) ## [(9, 10), (10, 11), (13, 15), (14, 16), (18, 19), (19, 20), (20, 21)]

for meeting_start, meeting_end in sorted(meetings):
    if block_end is None:
        block_start, block_end = meeting_start, meeting_end
    elif meeting_start > block_end:
        blocks.append((block_start, block_end))
        block_start, block_end = meeting_start, meeting_end
    else:
        block_end = max(block_end, meeting_end)

blocks.append((start, end))
        






    

