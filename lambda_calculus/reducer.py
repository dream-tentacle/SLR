"""
Use '>' to represent lambda
"""

import sys, string

sys.path.append("./")
from checker import *
from utils_lc import *
from common.utilities import *


def free_variable(exp: str) -> set[str]:
    if is_x(exp):
        return set([exp])
    if exp[0] == ">":
        return set(free_variable(exp[3:])) - set(exp[1])
    sub_exps = get_exp_from_MN(exp)
    res = set()
    for sub_exp in sub_exps:
        res = res.union(free_variable(sub_exp))
    return res


def substitute(M: str, N: str, x: str) -> str:
    """计算M[N/x]，即将M中的x替换成N

    Args:
        M (str): 不带空格
        N (str): 不带空格
        x (str): 一位长度字符串

    Raises:
        Exception: 若没有更多变量名可用则抛出异常

    Returns:
        str: 替换结果
    """
    assert len(x) == 1
    M = remove_outer_bracket(M)
    N = remove_outer_bracket(N)
    if is_x(M):
        if M == x:
            return N
        else:
            return M
    if M[0] == ">":
        if M[1] == x:
            return M
        if M[1] not in free_variable(N):
            return f">{M[1]}.{substitute(M[3:],N, x)}"
        unused_variables = set(list(string.ascii_lowercase)) - free_variable(N)
        unused_variables = list(unused_variables)
        unused_variables.sort()
        if len(unused_variables) == 0:
            raise Exception(f"Not enough variable names for {M}[{N}/{x}]")
        return f">{list(unused_variables)[0]}.{substitute(substitute(M[3:], list(unused_variables)[0] ,M[1]),N,x)}"
    sub_exps = get_exp_from_MN(M)
    re = []
    for sub_exp in sub_exps:
        result = substitute(sub_exp, N, x)
        if is_x(result):
            re.append(result)
        else:
            re.append(f"({result})")
    return "".join(re)


def is_normal_form(exp: str) -> bool:
    """检测是否为normal form

    Args:
        exp (str): 表达式

    Returns:
        bool: 判断结果
    """
    if exp[0] == ">":
        return is_normal_form(exp[3:])
    if is_x(exp):
        return True
    sub_exps = get_exp_from_MN(exp)
    for sub_exp in sub_exps[:-1]:
        if sub_exp[0] == ">" or not is_normal_form(sub_exp):
            return False
    return is_normal_form(sub_exps[-1])


@typechecked
def normal_order_reduce(exp: str) -> str:
    """进行一次normal order reduce

    Args:
        exp (str): 待化简式，可包含空格

    Returns:
        str: 化简结果，自动删除空格
    """
    exp = exp.replace(" ", "")
    exp = remove_outer_bracket(exp)
    if is_normal_form(exp):
        return exp
    if exp[0] == ">":
        return exp[:3] + normal_order_reduce(exp[3:])
    sub_exps = get_exp_from_MN(exp)
    res = ""
    for i, sub_exp in enumerate(sub_exps[:-1]):
        if sub_exp[0] == ">":
            pre = ""
            if i > 0:
                for j in range(i):
                    pre += f"({sub_exps[j]})" if not is_x(sub_exps[j]) else sub_exps[j]
            inner = ""
            for j in range(i + 1, len(sub_exps)):
                inner += f"({sub_exps[j]})" if not is_x(sub_exps[j]) else sub_exps[j]
            result = substitute(sub_exp[3:], inner, sub_exp[1])
            reduced = pre + "(" + result + ")"
            return remove_outer_bracket(reduced)
    for i, sub_exp in enumerate(sub_exps):
        if not is_normal_form(sub_exp):
            sub_exps[i] = normal_order_reduce(sub_exp)
            res = ""
            for j in range(len(sub_exps)):
                res += f"({sub_exps[j]})" if not is_x(sub_exps[j]) else sub_exps[j]
            return res
    raise Exception("The program failed!")


@typechecked
def show_reduce_process(exp: str, stopping: int = 10):
    print(exp)
    previous = []
    i = 0
    while not is_normal_form(exp):
        i += 1
        if i >= stopping:
            print("-> ... (the result is too long or it just diverges)")
            break
        previous.append(exp)
        exp = normal_order_reduce(exp)
        print(f"-> {exp}")
        if any([i in exp for i in previous]):
            print("-> ... (never ends)")
            break


show_reduce_process("(>x.z(>y.yyy)x)(>x.z(>y.yyy)x)")
show_reduce_process("(>x.xx)(>x.xx)")
show_reduce_process("MNZ(>x.xx)(>y.yyy)")
# 停机问题无法判定结果
