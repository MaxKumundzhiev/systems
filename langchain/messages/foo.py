import sys


def foo():
    data = sys.stdin.read().split()
    if not data:
        return

    it = iter(data)
    n = int(next(it))

    current_water = last_time = 0

    for _ in range(n):
        t_i = int(next(it))
        v_i = int(next(it))

        delta_t = t_i - last_time
        current_water = max(0, current_water - delta_t)
        current_water += v_i
        last_time = t_i

    return current_water


if __name__ == "__main__":
    foo()
