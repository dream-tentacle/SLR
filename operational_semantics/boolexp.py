import sys, re
from typing import Union
from intexp import IntExp, IntExpSyntaxError, int_valid_contents

sys.path.append("./")
from common.utilities import *


class BoolExpSyntaxError(TermError):
    pass


bool_valid_contents = "TF=<>!&|" + int_valid_contents

bool_operation = {
    "&": lambda x, y: x and y,
    "|": lambda x, y: x or y,
    "!=": lambda x, y: x != y,
    "==": lambda x, y: x == y,
}


class BoolExp:
    exp: str
    left: Union["BoolExp", "IntExp"] | None
    right: Union["BoolExp", "IntExp"] | None
    op: str | None
    value: int | str | None

    @typechecked
    def __init__(self, exp: str):
        self.left = None
        self.right = None
        self.op = None
        self.value = None
        if len(exp) == 0:
            raise BoolExpSyntaxError(msg="Empty expression received", offset=0, text="")
        for i, ch in enumerate(exp):
            if ch not in bool_valid_contents:
                raise BoolExpSyntaxError(msg=f"Invalid charactor: '{ch}'", offset=i, text=exp)
        self.exp = exp
        outer_count = 0
        try:
            outer_count = count_outer_bracket(self.exp)
        except SyntaxError as e:
            raise BoolExpSyntaxError(
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
            elif ch in "&|" and bracket_count == outer_count:
                try:
                    self.left = BoolExp(exp[outer_count:i])
                except BoolExpSyntaxError as e:
                    raise BoolExpSyntaxError(msg=e.msg, offset=e.offset, text=exp) from None
                except IntExpSyntaxError as e:
                    raise IntExpSyntaxError(msg=e.msg, offset=e.offset, text=exp) from None
                try:
                    if outer_count == 0:
                        self.right = BoolExp(exp[i + 1 :])
                    else:
                        self.right = BoolExp(exp[i + 1 : -outer_count])
                except BoolExpSyntaxError as e:
                    raise BoolExpSyntaxError(msg=e.msg, offset=e.offset + i + 1, text=exp) from None
                except IntExpSyntaxError as e:
                    raise IntExpSyntaxError(msg=e.msg, offset=e.offset + i + 1, text=exp) from None
                self.op = ch
                return
        for i in range(len(exp) - 1, -1, -1):
            ch = exp[i]
            if ch == ")":
                bracket_count += 1
            elif ch == "(":
                bracket_count -= 1
            elif ch in "=" and bracket_count == outer_count and i > 0:
                if exp[i - 1] in "!=":
                    try:
                        self.left = IntExp(exp[outer_count : i - 1])
                    except IntExpSyntaxError as e:
                        raise IntExpSyntaxError(msg=e.msg, offset=e.offset, text=exp) from None
                    try:
                        if outer_count == 0:
                            self.right = IntExp(exp[i + 1 :])
                        else:
                            self.right = IntExp(exp[i + 1 : -outer_count])
                    except IntExpSyntaxError as e:
                        raise IntExpSyntaxError(
                            msg=e.msg, offset=e.offset + i + 1, text=exp
                        ) from None
                    self.op = exp[i - 1] + ch
                    return
                else:
                    raise BoolExpSyntaxError(msg=f"Unexpected '=' in '{exp}'", offset=i, text=exp)
        if self.exp[outer_count] == "!":
            self.op = "!"
            self.left = None
            try:
                if outer_count == 0:
                    self.right = IntExp(exp[i + 1 :])
                else:
                    self.right = IntExp(exp[i + 1 : -outer_count])
            except IntExpSyntaxError as e:
                raise IntExpSyntaxError(msg=e.msg, offset=e.offset + i + 1, text=exp) from None
            return
        exp = exp[outer_count:-outer_count] if outer_count != 0 else exp
        if exp == "T" or exp == "F":
            self.value = exp == "T"
        else:
            raise BoolExpSyntaxError(
                msg=f"Unknown syntax in '{exp}'", offset=outer_count, text=self.exp
            )

    def print_tree(self, layer):
        print("|" + layer * "-" + str(self))
        if self.op:
            self.left.print_tree(layer + 2)
            self.right.print_tree(layer + 2)

    @typechecked
    def reduce(self, state: dict) -> bool | None:
        """进行一步reduce

        Args:
            state (dict): 从variable name到值的映射

        Raises:
            IntExpSyntaxError: 语法错误

        Returns:
            bool: True表示进行了规约，False表示没有规约但去除了括号，None表示不可规约
        """
        if self.op == "==" or self.op == "!=":
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
                        self.value = bool_operation[self.op](self.left.value, self.right.value)
                        self.op = None
                        self.right = None
                        self.left = None
                        return True
                except IntExpSyntaxError as e:
                    raise IntExpSyntaxError(msg=e.msg, offset=len(self.left.exp) + 3, text=self)
            else:
                try:
                    result = self.left.reduce(state)
                except IntExpSyntaxError as e:
                    raise IntExpSyntaxError(msg=e.msg, offset=e.offset, text=self)
                return result
        elif self.op == "&" or self.op == "|":
            if isinstance(self.left.value, bool) and self.left.outer_count == 0:
                try:
                    result = self.right.reduce(state)
                    if result:
                        return True
                    elif result is False:
                        return False
                    else:
                        assert isinstance(self.left.value, bool)
                        assert isinstance(self.right.value, bool)
                        self.value = bool_operation[self.op](self.left.value, self.right.value)
                        self.op = None
                        self.right = None
                        self.left = None
                        return True
                except BoolExpSyntaxError as e:
                    raise BoolExpSyntaxError(msg=e.msg, offset=len(self.left.exp) + 2, text=self)
            else:
                try:
                    result = self.left.reduce(state)
                except BoolExpSyntaxError as e:
                    raise BoolExpSyntaxError(msg=e.msg, offset=e.offset, text=self)
                return result
        elif self.op == "!":
            assert self.left is None
            try:
                result = self.right.reduce(state)
                if result:
                    return True
                elif result is False:
                    return False
                else:
                    assert isinstance(self.right.value, bool)
                    self.value = not self.right.value
                    self.op = None
                    self.right = None
                    self.left = None
            except BoolExpSyntaxError as e:
                raise BoolExpSyntaxError(msg=e.msg, offset=e.offset + 1, text=self)
        else:
            if self.outer_count > 0:
                self.outer_count -= 1
                return False
            if isinstance(self.value, str):
                if self.value in state.keys():
                    self.value = state[self.value]
                    return True
                else:
                    raise BoolExpSyntaxError(
                        msg=f"Unknown variable '{self.value}", offset=0, text=self
                    )
            return None

    def __str__(self):
        if self.op:
            return (
                self.outer_count * "("
                + (str(self.left) if self.left else "")
                + self.op
                + str(self.right)
                + self.outer_count * ")"
            )
        else:
            return self.outer_count * "(" + str(self.value) + self.outer_count * ")"

    @typechecked
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
    x = BoolExp("T&(F|x+3!=5-6)|F")
    x.print_tree(0)
    x.reduce_till_the_end({"x": 1})
