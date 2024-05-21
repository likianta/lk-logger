from functools import partial

import lk_logger
from lk_logger import bprint
from lk_logger import parallel_printing

lk_logger.setup()


def test_exclusive_rule() -> None:
    p1 = partial(bprint, '[printer 1]')
    p2 = partial(bprint, '[printer 2]')
    p3 = partial(bprint, '[printer 3]')
    p4 = partial(bprint, '[printer 4]')
    p5 = partial(bprint, '[printer 5]')
    
    with parallel_printing(p1, p2):
        print('aaa')
        with parallel_printing(p3):
            print('bbb')
        with parallel_printing(p4, inherit=False):
            print('ccc')
            with parallel_printing(p5):
                print('ddd')


def circular_prints() -> None:
    p1 = partial(print, '[printer 1]')
    with parallel_printing(p1):
        print('hello')


if __name__ == '__main__':
    # py tests/test_parallel_printing.py
    # test_exclusive_rule()
    circular_prints()
