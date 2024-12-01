import sys

sys.path.append(".")
from common.utilities import *
import checker


def test_get_exp_from_MN():
    tests = [
        ("MN", ["M", "N"]),
        ("(>x.M)N", [">x.M", "N"]),
        ("(>x.M(>x.M))(>x.M)N", [">x.M(>x.M)", ">x.M", "N"]),
    ]
    test_scheme(tests, func=checker.get_exp_from_MN)


def test_check_syntax():
    tests = [
        ("x", None),
        ("MN", None),
        ("(", SyntaxError("bracket for '(' is invalid")),
        ("()", SyntaxError("empty expression received")),
        ("(M)", None),
        ("(N)(((M)(MN))M)", None),
        ("(>x.N)M", None),
        ("N(>x.M)", None),
    ]
    test_scheme(tests, func=checker.check_syntax)


test_get_exp_from_MN()
test_check_syntax()
