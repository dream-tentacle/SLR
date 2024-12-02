RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
NORMAL = "\033[0m"
from typing import Callable, Tuple, List
from typeguard import typechecked


@typechecked
def test_scheme(tests: List[Tuple], func: Callable):
    print("=" * 10, func.__name__, "=" * 10)
    passed = 0
    for test in tests:
        try:
            assert func(test[0]) == test[1]
        except Exception as e:
            if isinstance(test[1], Exception):
                if str(test[1]) == str(e):
                    passed += 1
                    continue
                else:
                    print(f"got exception '{str(e)}'\nexpected: '{str(test[1])}")
            print(
                "=" * 10,
                f"test failed ('{test[0]}', '{test[1] if test[1] else 'None'}')",
                "=" * 10,
            )
            print(f"Exception {type(e).__name__}: ")
            if str(e):
                print(str(e))
            else:
                print(f"{func(test[0])} != {test[1]}")
        else:
            passed += 1
    if passed == len(tests):
        print(f"{GREEN}ALL PASSED!{NORMAL}")
    else:
        print(f"{RED}{passed} out of {len(tests)} passed{NORMAL}")


def is_x(exp: str):
    """判断是不是单个大写/小写字母

    Args:
        exp (str): 字符串
    """
    return len(exp) == 1 and (
        (ord(exp) <= ord("Z") and ord(exp) >= ord("A"))
        or (ord(exp) <= ord("z") and ord(exp) >= ord("a"))
    )


def is_eng(exp: str):
    """判断是不是全由英语构成

    Args:
        exp (str): 字符串
    """
    return all([is_x(i) for i in exp])
