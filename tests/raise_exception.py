import sys

import lk_logger

lk_logger.setup()


def raise_an_error() -> None:
    print('raise an zero assertion error...', ':v4s')
    a, b = 1, 0
    print(a / b)


def test_exception_panel_on_a_narrow_width() -> None:
    lk_logger.update(console_width=60)
    raise_an_error()


if __name__ == '__main__':
    # pox tests/raise_exception.py 0
    # pox tests/raise_exception.py 1
    if len(sys.argv) == 1 or sys.argv[1] == '0':
        raise_an_error()
    else:
        test_exception_panel_on_a_narrow_width()
