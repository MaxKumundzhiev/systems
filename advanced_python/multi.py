import time
from multiprocessing import Process, Pool

"""
"""


def sum_to_num(stop: int) -> str:
    start = time.monotonic()

    total = 0
    for num in range(stop):
        total += num

    eval = time.monotonic() - start

    return f"Eval: {eval} of {total}"


def sequential_even_on_diff_cores():
    pr_a = Process(name="pr-a", target=sum_to_num, args=(10_000,))
    pr_b = Process(name="pr-b", target=sum_to_num, args=(1_000,))

    res_a, res_b = pr_a.start(), pr_b.start()
    print(pr_a, pr_b)
    pr_a.join()
    print(pr_a, pr_b)
    pr_b.join()
    print(pr_a, pr_b)


def sequential_with_pool():
    """
    As the code shows, Pool’s apply method is synchronous, which means you have to wait
    for the previously apply task to finish before the next apply task can start executing.

    Of course, we can use the apply_async method to create the task asynchronously.
    But again, you need to use the get method to get the result blockingly. It brings us back to the problem with the join method:
    """
    with Pool() as pool:
        res_a = pool.apply(sum_to_num, args=(10_000,))
        res_b = pool.apply(sum_to_num, args=(1_000,))
        # res_a = pool.apply_async(sum_to_num, args=(10_000,))
        # res_b = pool.apply_async(sum_to_num, args=(1_000,))
        """
        but getting results are blocking as well: res_a.get()
        """

        print(res_a)
        print(res_b)


if __name__ == "__main__":
    # sequential_even_on_diff_cores()
    sequential_with_pool()
