import math


# def truncate(number, digits=6):
#     stepper = 10.0 ** digits
#     return math.trunc(stepper * number) / stepper


def truncate(number, digits=6):
    num = "{:.6f}".format(number)
    return float(num)

