"""
Реализуй структуру данных, которая позволяет быстро находить сумму всех элементов на отрезке [l, r] (включая границы). При этом массив не изменяется.

Другими словами, нужно реализовать:
Конструктор (вызывается один раз).
Метод sum (вызывается многократно, поэтому он должен быть максимально быстрым).
"""


class PrefixSum:
    def __init__(self, nums: list[int]) -> None:
        self._prefix = [0]
        for n in nums:
            self._prefix.append(self._prefix[-1] + n)

    def sum(self, l: int, r: int):
        return self._prefix[r + 1] - self._prefix[l]
