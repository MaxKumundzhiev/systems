from typing import List


def sum_(arr):
    # base case
    if len(arr) == 0:
        return 0
    elif len(arr) == 1:
        return arr[-1]

    # recursive case
    val = arr.pop(0)
    return val + sum_(arr)


def freq_count(arr: List[int], freq: dict) -> dict:
    # base case
    if not bool(arr):
        return freq

    val = arr.pop()
    freq[val] = freq.get(val, 0) + 1
    freq_count(arr, freq)
    return freq


def max_val_in_arr_iter(arr) -> int | float:
    curr_max = float("-inf")
    for val in arr:
        curr_max = max(curr_max, val)
    return curr_max


def max_val_in_arr_rec(arr) -> int:
    """
    # [1,2,3] -> [2,3] max(1, 3) -> 3
    # [2,3]   -> [3]   max(2, 3) -> 3
    # [3]     -> [3]   3
    """
    # base case
    if len(arr) == 1:
        return arr[-1]

    val = arr.pop(0)
    return max(val, max_val_in_arr_rec(arr))


if __name__ == "__main__":
    # print(sum_([1, 2, 3]))
    # print(freq_count([1,1,2], {}))
    # print(max_val_in_arr_iter([1, -5, 10, 1000]))
    # print(max_val_in_arr_rec([1, -5, 10, 1000]))
    ...
