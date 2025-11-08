

def sum_(arr):
    # base case
    if len(arr) == 0:
        return 0
    elif len(arr) == 1:
        return arr[-1]
    
    # recursive case
    val = arr.pop(0)
    return val + sum_(arr)


print(sum_([1, 2, 3]))