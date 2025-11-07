"""
selection sort

Time O(n^2)
Space O(n)

for each val in nums look up the smallest
add it to res arr
pop it from original arr
"""

from typing import List

class Solution:
    def find_smallest(self, nums) -> int:
        smallest_val, smallest_idx = nums[0], 0
        for idx in range(len(nums)):
            if nums[idx] < smallest_val:
                smallest_val, smallest_idx = nums[idx], idx
        return smallest_idx

    def sortArray(self, nums: List[int]) -> List[int]:
        res = []
        for _ in range(len(nums)):
            smallest_idx = self.find_smallest(nums)
            res.append(nums.pop(smallest_idx))
        return res