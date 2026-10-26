meetings = [(9, 10), (10, 11), (13, 15), (14, 16), (18, 19), (19, 20), (20, 21)]

# Ensure meetings are sorted by start time
meetings.sort()

blocks = list()
s, e = meetings[0] 

for block in meetings[1:]:
    # If the next meeting starts after the current one ends, 
    # the current merged block is complete.
    if block[0] > e: 
        blocks.append((s, e))
        s, e = block[0], block[1] # Reset to the new block's boundaries
    else:
        # Overlap found; extend the end time if necessary
        e = max(e, block[1])

# Don't forget to append the final block!
blocks.append((s, e))

print(blocks)
# Output: [(9, 11), (13, 16), (18, 21)]
