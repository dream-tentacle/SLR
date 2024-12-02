import sys
from typeguard import typechecked

sys.path.append("./")
from lambda_calculus.utils_lc import *


@typechecked
def check_syntax(exp: str):
    """检查语法
    M, N = x | (M) | MN | >x.M
    Args:
        exp (str): 需要检查语法的表达式
    """
    exp = exp.replace(" ", "")
    for ch in exp:
        if not is_x(ch) and ch != "(" and ch != ")" and ch != "." and ch != ">":
            raise SyntaxError(f"Unknown char '{ch}' in '{exp}'")
    # 检查括号
    if not check_bracket(exp):
        raise SyntaxError(f"bracket for '{exp}' is invalid")
    # 去除整个表达式最外层括号，避免(M)的情况
    exp = remove_outer_bracket(exp)
    if not exp:
        raise SyntaxError(f"empty expression received")
    # x
    if is_x(exp):
        return
    # >x.M
    if exp[0] == ">":
        try:
            check_syntax(exp[1])
        except:
            raise SyntaxError(f"variable syntax after first > for '{exp}' is invalid")
        try:
            check_syntax(exp[3:])
        except Exception as e:
            print(f"syntax for '{exp}' after dot is invalid:")
            raise e
        return
    # MN
    sub_exps = get_exp_from_MN(exp)
    for sub_exp in sub_exps:
        check_syntax(sub_exp)
