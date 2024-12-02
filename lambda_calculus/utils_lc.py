import sys

sys.path.append("./")
from common.utilities import *


def check_bracket(exp: str):
    bracket_stack = 0
    for ch in exp:
        if ch == "(":
            bracket_stack += 1
        elif ch == ")":
            bracket_stack -= 1
        if bracket_stack < 0:
            return False
    return bracket_stack == 0


def remove_outer_bracket(exp: str):
    while len(exp) > 0 and exp[0] == "(" and exp[-1] == ")":
        if check_bracket(exp[1:-1]):
            exp = exp[1:-1]
        else:
            break
    return exp


def get_exp_from_MN(exp: str):
    """从MN形式的表达式拆解出每一个M

    Args:
        exp (str): MN形式的表达式
    """
    res = []
    bracket_stack = 0
    last_index = 0
    for i, ch in enumerate(exp):
        if bracket_stack == 0 and is_x(ch):
            res.append(ch)
        elif ch == "(":
            bracket_stack += 1
            if bracket_stack == 1:
                last_index = i
        elif ch == ")":
            bracket_stack -= 1
            if bracket_stack == 0:
                res.append(remove_outer_bracket(exp[last_index : i + 1]))
    return res
