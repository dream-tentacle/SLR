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
