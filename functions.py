import math

def get_name(name):
    return name.replace("_", " ").title()

def seq_floated(start, stop, step=1):
    min = start
    
    while True:
        if step:
            yield start
        else:
            yield 0

        start += step
        if step > 0:
            if start > stop:
                step = -step
        else:
            if start < min:
                step = -step

def set_threshold(num, min, max):
    if num < min:
        return min
    elif num > max:
        return max
    return num

def get_dist(a, b):
    return math.sqrt(abs(a[0]-b[0])**2 + abs(a[1]-b[1])**2)
