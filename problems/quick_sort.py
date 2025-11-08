from typing import List


# quick sort
"""
cкорость зависит от выбора опорного элемента

base case
recursive case
    pick pivotal element (might be 1st elem)
    take what is less than pivotal element
    take what is grater than pivotal element
    recursive call call(less) + pivotal + call(grater)
"""

class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:
        # base case
        if len(nums) < 2:
            return nums
        
        # recursive case
        pivotal = nums[0]
        less = [num for num in nums[1:] if num <= pivotal]
        greater = [num for num in nums[1:] if num > pivotal]
        return self.sortArray(less) + [pivotal] + self.sortArray(greater)