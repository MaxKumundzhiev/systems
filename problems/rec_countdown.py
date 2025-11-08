

def countdown(number: int):
    # base case
    if number == 0:
        print("countdown is finished")
        return
    # recursive case
    else:
        current = number
        print(f"put on stack {current} and go down")
        next = current - 1
        countdown(number=next)
        print(f"go up {current} and {next}")
        return

countdown(5)


"""
countdown(5) number=5
countdown(4) number=4
countdown(3) number=3
countdown(2) number=2
countdown(1) number=1
countdown(0) number=0 --> finished
"""