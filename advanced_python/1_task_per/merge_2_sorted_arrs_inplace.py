"""
idea
    fill arr1 inplace from the end
    how?
    on each iter look up for greatest elem
    since both are sorted, greatest are located in the ends, thus
    3 pointers: end of arr1, end of arr2, insert pos
    on each iter we move left, depending on in which arr we found greatest

1,2,3,4,5,6,7,8
|
  |

2,4,6,8
|
"""


def merge_two_sorted_arrays(
    arr1: list[int], m: int, arr2: list[int], n: int
) -> list[int]:
    p1, p2, p = m - 1, n - 1, m + n - 1
    # The loop runs while either pointer has elements left
    while p1 >= 0 or p2 >= 0:
        # --> for TAKING FROM ARR1
        # Case 1: p2 < 0 — arr2 is exhausted.
        # Only arr1 elements remain.
        # Copy them in place (they're already there, but idx and p1 step together, so it's a no-op write that still terminates correctly).
        # Case 2: p1 >= 0 and p2 >= 0 and nums1[p1] > nums2[p2] — both have elements, arr1's is larger.
        # Take from arr1.
        if p2 < 0 or (p1 >= 0 and p2 >= 0 and arr1[p1] > arr2[p2]):
            arr1[p] = arr1[p1]
            p1 -= 1
        # --> for TAKING FROM ARR2
        # p1 < 0 (arr1 exhausted, arr2 still has elements) → take from arr2
        # Both present but nums1[p1] <= nums2[p2] → take from arr2
        else:
            arr1[p] = arr2[p2]
            p2 -= 1
        p -= 1
    return arr1
