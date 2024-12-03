import sys, re
from typing import Optional

sys.path.append("./")
from common.utilities import *


class IntExpSyntaxError(TermError):
    pass


import string

# 获取小写字母 a-z
lowercase = list(string.ascii_lowercase)

# 获取大写字母 A-Z
uppercase = list(string.ascii_uppercase)

# 合并小写字母和大写字母
all_letters = lowercase + uppercase

int_valid_contents = "".join(all_letters) + "0123456789" + "+-*/()"

int_operation = {
    "+": lambda x, y: x + y,
    "-": lambda x, y: x - y,
    "*": lambda x, y: x * y,
    "/": lambda x, y: x / y,
}


class IntExp:
    exp: str
    left: Optional["IntExp"]
    right: Optional["IntExp"]
    op: str | None
    value: int | str | None

    def __init__(self, exp: str):
        self.left = None
        self.right = None
        self.op = None
        self.value = None
        if len(exp) == 0:
            raise IntExpSyntaxError(msg="Empty expression received", offset=0, text="")
        for i, ch in enumerate(exp):
            if ch not in int_valid_contents:
                raise IntExpSyntaxError(msg=f"Invalid charactor: {ch}", offset=i, text=exp)
        self.exp = exp
        outer_count = 0
        try:
            outer_count = count_outer_bracket(self.exp)
        except SyntaxError as e:
            raise IntExpSyntaxError(
                msg=f"Invalid bracket pair '{exp}'", offset=0, text=exp
            ) from None
        self.outer_count = outer_count
        bracket_count = 0
        for i in range(len(exp) - 1, -1, -1):
            ch = exp[i]
            if ch == ")":
                bracket_count += 1
            elif ch == "(":
                bracket_count -= 1
            elif ch in "+-*/" and bracket_count == outer_count:
                try:
                    self.left = IntExp(exp[outer_count:i])
                except IntExpSyntaxError as e:
                    raise IntExpSyntaxError(msg=e.msg, offset=e.offset, text=exp) from None
                try:
                    if outer_count == 0:
                        self.right = IntExp(exp[i + 1 :])
                    else:
                        self.right = IntExp(exp[i + 1 : -outer_count])
                except IntExpSyntaxError as e:
                    raise IntExpSyntaxError(msg=e.msg, offset=e.offset + i + 1, text=exp) from None
                self.op = ch
                return
        exp = exp[outer_count:-outer_count] if outer_count != 0 else exp
        try:
            self.value = int(exp)
        except:
            if exp[0] in "1234567890":
                raise IntExpSyntaxError(
                    msg="Can't use number to start a variable", offset=outer_count, text=self.exp
                )
            self.value = exp

    def print_tree(self, layer):
        print("|" + layer * "-" + str(self))
        if self.op:
            self.left.print_tree(layer + 2)
            self.right.print_tree(layer + 2)

    def reduce(self, state: dict) -> bool | None:
        """进行一步reduce

        Args:
            state (dict): 从variable name到值的映射

        Raises:
            IntExpSyntaxError: 语法错误

        Returns:
            bool: True表示进行了规约，False表示没有规约但去除了括号，None表示不可规约
        """

        if self.op:
            if isinstance(self.left.value, int) and self.left.outer_count == 0:
                try:
                    result = self.right.reduce(state)
                    if result:
                        return True
                    elif result is False:
                        return False
                    else:
                        assert isinstance(self.left.value, int)
                        assert isinstance(self.right.value, int)
                        self.value = int_operation[self.op](self.left.value, self.right.value)
                        self.op = None
                        self.right = None
                        self.left = None
                        return True
                except IntExpSyntaxError as e:
                    raise IntExpSyntaxError(msg=e.msg, offset=len(self.left.exp) + 2, text=self)

            else:
                try:
                    result = self.left.reduce(state)
                except IntExpSyntaxError as e:
                    raise IntExpSyntaxError(msg=e.msg, offset=e.offset, text=self)
                return result
        else:
            if self.outer_count > 0:
                self.outer_count -= 1
                return False
            if isinstance(self.value, str):
                if self.value in state.keys():
                    self.value = state[self.value]
                    return True
                else:
                    raise IntExpSyntaxError(
                        msg=f"Unknown variable '{self.value}", offset=0, text=self
                    )
            return None

    def __str__(self):
        if self.op:
            return (
                self.outer_count * "("
                + str(self.left)
                + self.op
                + str(self.right)
                + self.outer_count * ")"
            )
        else:
            return self.outer_count * "(" + str(self.value) + self.outer_count * ")"

    def reduce_till_the_end(self, state: dict = {}):
        print(self)
        result = self.reduce(state)
        while result is not None:
            if result:
                print("->", self)
            else:
                print(" =", self)
            result = self.reduce(state)


if __name__ == "__main__":
    x = IntExp("5+((a+b)*3)-(1+2)")
    x.print_tree(0)
    x.reduce_till_the_end({"a": 1, "b": 4})
