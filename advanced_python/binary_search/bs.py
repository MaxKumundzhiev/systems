from typing import *


def find_offset(nums: list[int]) -> int:
    """
    look up for first element
    answer gonna be on right idx, thus l=-1 r=len(nums)-1
    otherwiswe l=0, r=len(nums)
    """
    l, r = -1, len(nums) - 1
    last = nums[-1]

    while r - l > 1:
        middle = (r + l) // 2
        if nums[middle] > last:
            l = middle
        else:
            r = middle
    return r


def search(nums: List[int], target: int) -> int:
    offset = find_offset(nums)
    l, r = offset, offset + len(nums)
    while r - l > 1:
        m = (l + r) // 2
        if nums[m % len(nums)] <= target:
            l = m
        else:
            r = m
    real_left = l % len(nums)
    return real_left if nums[real_left] == target else -1
