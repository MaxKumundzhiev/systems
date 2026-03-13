"""
parent = (idx - 1) // 2
leftChild = 2 * idx + 1
rightChild = 2 * idx + 2
"""


class Heap:
    def __init__(self) -> None:
        self.nums: list[int] = []

    def insert(self, value: int) -> None:
        self.nums.append(value)
        self._sift_up(len(self.nums) - 1)

    def _sift_up(self, idx: int) -> None:
        # while not root and child > parent
        while idx > 0 and self.nums[idx] > self.nums[(idx - 1) // 2]:
            parent: int = (idx - 1) // 2
            self.nums[idx], self.nums[parent] = self.nums[parent], self.nums[idx]
            idx = parent
