import sys
from typeguard import typechecked
from dataclasses import dataclass
from typing import Union, Optional, Dict

sys.path.append("./")
from common.utilities import *


class TermType:
    pass


@dataclass
class VariableType(TermType):
    name: str

    def __eq__(self, value: object) -> bool:
        return isinstance(value, VariableType) and self.name == value.name

    def __str__(self) -> str:
        return self.name


@dataclass
class FunctionType(TermType):
    type1: TermType
    type2: TermType

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, FunctionType):
            return False
        return self.type1 == value.type1 and self.type2 == value.type2

    def __str__(self) -> str:
        return f"({self.type1}->{self.type2})"


@dataclass
class CallFunctionType(TermType):
    type1: FunctionType
    type2: TermType


class UnrecognizedType(TermType):
    pass


def count_outer_bracket(exp):
    bracket_stack = []
    corres_end = {}
    for i, c in enumerate(exp):
        if c == "(":
            bracket_stack.append(i)
        elif c == ")":
            corres_end[bracket_stack.pop()] = i
    for i in range(len(exp)):
        if corres_end.get(i, None) != len(exp) - i - 1:
            return i
    return 0


class TermError(Exception):
    def __init__(self, msg, offset: int = None, text: str = None):
        self.msg = msg
        self.offset = offset
        self.text = text

    def __str__(self) -> str:
        res = self.msg + "\n"
        res += self.text + "\n"
        res += "~" * self.offset + "^"
        return res


class TermSyntaxError(TermError):
    pass


class TermTypeError(TermError):
    pass


class Term:
    @typechecked
    def __init__(self, exp: str, type: Optional[TermType] = None):
        self.exp = exp
        self.orig_exp = exp
        if type:
            self.type = type
        else:
            count = count_outer_bracket(self.exp)
            if count * 2 == len(self.exp):
                raise TermSyntaxError(msg="Empty content received", offset=0, text=self.exp)
            self.exp = self.exp[count : len(self.exp) - count]
            self.type = None
            self.seperate()

    def seperate(self):
        """
        M, N = x | >x:tau.M | MN
        """
        if is_eng(self.exp):
            self.type = VariableType("")
            return
        if self.exp[0] == ">":
            self.type = FunctionType(UnrecognizedType(), UnrecognizedType())
            if ":" not in self.exp:
                raise TermSyntaxError(
                    msg="No Corresponding ':' for '>'", offset=0, text=self.exp
                ) from None
            if "." not in self.exp:
                raise TermSyntaxError(
                    msg="No Corresponding '.' for '>'", offset=0, text=self.exp
                ) from None
            if not is_eng(self.exp.split(":")[0][1:]):
                raise TermSyntaxError(
                    msg="Wrong variable after '>'", offset=1, text=self.exp
                ) from None
            self.child1 = Term(
                self.exp.split(":")[0][1:], type=VariableType(self.exp.split(":")[1].split(".")[0])
            )
            if not is_eng(self.exp.split(":")[1].split(".")[0]):
                raise TermSyntaxError(
                    msg=f"Wrong type for {self.child1.exp}",
                    offset=self.exp.find(":") + 1,
                    text=self.exp,
                ) from None
            child2 = ".".join(self.exp.split(".")[1:])
            try:
                self.child2 = Term(child2)
            except TermSyntaxError as e:
                raise TermSyntaxError(
                    msg=e.msg,
                    offset=e.offset + self.exp.find(".") + 1 + count_outer_bracket(child2),
                    text=self.exp,
                ) from None
        else:
            self.type = CallFunctionType(
                FunctionType(UnrecognizedType, UnrecognizedType), UnrecognizedType
            )
            child1 = None
            child2 = None
            if self.exp[0] == "(":
                # 说明是()(...)形式
                bracket_count = 0
                child1 = None
                for i, c in enumerate(self.exp):
                    if c == "(":
                        bracket_count += 1
                    elif c == ")":
                        bracket_count -= 1
                        if bracket_count == 0:
                            child1 = self.exp[0 : i + 1]
                            break
            else:
                # 说明是M(...)形式
                child1 = self.exp.split("(")[0]
            if child1 is None:
                raise TermSyntaxError(
                    msg="Wrong bracket expression",
                    offset=0,
                    text=self.exp,
                ) from None
            child2 = self.exp[len(child1) :]
            try:
                self.child1 = Term(child1)
            except TermSyntaxError as e:
                raise TermSyntaxError(
                    msg=e.msg,
                    offset=e.offset + count_outer_bracket(child1),
                    text=self.exp,
                ) from None
            try:
                self.child2 = Term(child2)
            except TermSyntaxError as e:
                raise TermSyntaxError(
                    msg=e.msg,
                    offset=e.offset + count_outer_bracket(child2) + len(child1),
                    text=self.exp,
                ) from None

    def get_type(self, context: Dict[str, str]):
        if isinstance(self.type, VariableType) and self.type.name == "":
            if context[self.exp]:
                return VariableType(context[self.exp])
            raise TermTypeError(msg=f"Can't find type of '{self.exp}'", offset=0, text=self.exp)
        if isinstance(self.type, FunctionType):
            new_context = context
            if self.child1.type.name != "":
                if context.get(self.child1.exp, self.child1.type.name) != self.child1.type.name:
                    raise TermTypeError(
                        msg=f"Collision types for variable '{self.child1.type.name}: "
                        f"{context[self.child1.exp]} and {self.child1.type.name}",
                        offset=1,
                        text=self.exp,
                    )
                new_context[self.child1.exp] = self.child1.type.name
            try:
                child2_type = self.child2.get_type(new_context)
            except TermTypeError as e:
                raise TermTypeError(
                    msg=e.msg, offset=e.offset + len(self.exp.split(".")[0]) + 1, text=self.exp
                )
            return FunctionType(self.child1.type, child2_type)
        if isinstance(self.type, CallFunctionType):
            try:
                child1_type = self.child1.get_type(context)
            except TermTypeError as e:
                raise TermTypeError(
                    msg=e.msg,
                    offset=e.offset + count_outer_bracket(self.child1.orig_exp),
                    text=self.exp,
                )
            try:
                child2_type = self.child2.get_type(context)
            except TermTypeError as e:
                raise TermTypeError(
                    msg=e.msg,
                    offset=e.offset
                    + len(self.child1.orig_exp)
                    + count_outer_bracket(self.child2.orig_exp),
                    text=self.exp,
                )
            if not isinstance(child1_type, FunctionType):
                raise TermTypeError(
                    msg=f"Non-function term '{self.child1.exp}' cannot be called",
                    offset=0,
                    text=self.exp,
                )
            if not isinstance(child1_type.type1, type(child2_type)):
                raise TermTypeError(
                    msg=f"Expect type '{child2_type}''{self.child1.exp}' cannot be called",
                    offset=0,
                    text=self.exp,
                )
            if child1_type.type1 != child2_type:
                raise TermTypeError(
                    msg=f"Wrong variable type for function '{self.child1.exp}'",
                    offset=len(self.child1.orig_exp) + count_outer_bracket(self.child2.orig_exp),
                    text=self.exp,
                )
            return child1_type.type2
        raise TermTypeError(msg=f"Unknown Error!", offset=0, text=self.exp)


print(Term("(>z:tau.>x:tau.x)(>y:tau.y)x").get_type({"x": "tau"}))
