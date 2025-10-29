"""
we want optimally store users in memory
for that we use
    - array of linked lists

we create an array of 26 slots (a-z alphabet)
for each new user 
    - we lookup "bucket" for a user out of 26 for constant time
    - we add to the end of linked list a new user
"""

