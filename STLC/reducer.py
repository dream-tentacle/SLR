import sys

sys.path.append("./")
from lambda_calculus.reducer import normal_order_reduce, is_normal_form
from lambda_calculus.checker import check_syntax
from term import *


def reduce(term: Term, context):
    print(f"term has type {term.get_type(context)} in the context")
    exp = term.exp
    removes = []
    last = 0
    for i, ch in enumerate(exp):
        if ch == ":":
            last = i
        elif ch == ".":
            removes.append(exp[last:i])
    for remove in removes:
        exp = exp.replace(remove, "")
    check_syntax(exp)
    while not is_normal_form(exp):
        exp = normal_order_reduce(exp)
    return exp


if __name__ == "__main__":
    term = Term("(>z:(sigma->sigma).((>b:tau.b)x))(>y:sigma.y)")
    print(reduce(term, {"x": VariableType("tau")}))
