# coding=utf-8

import random


def get_witness(problem, assignment):
    """
    Given an instance of a partition problem via a list of numbers (the problem) and a list of
    (-1, 1), we say that the assignment satisfies the problem if their dot product is 0.
    """
    sum = 0
    mx = 0
    side_obfuscator = 1 - 2 * random.randint(0, 1)  # 丢硬币，产生随机的-1或者1
    print('side_obfuscator', side_obfuscator)
    witness = [sum]  # witness便是p，p是两个数组的点积，不加绝对值
    assert len(problem) == len(assignment)
    for num, side in zip(problem, assignment):
        assert side == 1 or side == -1
        sum += side * num * side_obfuscator  # 计算p的元素
        print('p的元素', sum)
        witness += [sum]
        print('witness的变化', witness)
        mx = max(mx, num)
    # make sure that it is a satisfying assignment
    assert sum == 0
    shift = random.randint(0, mx)  # 0~mx 之间随机取一个数值
    print('shift', shift)
    witness = [x + shift for x in witness]  # 将随机数r分别加到p的每个元素中
    return witness


l = [4, 11, 8, 1]
m = [1, -1, 1, -1]

witness = get_witness(problem=l, assignment=m)
print('witness的结果', witness)