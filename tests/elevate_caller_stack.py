from lk_logger import logger


def aaa():
    print(':p', 'hello')


def bbb():
    with logger.elevate_caller_stack():
        aaa()  # the source pointer of `aaa:print` should point to its caller
    aaa()  # `aaa:print` should point here


bbb()

# pox tests/elevate_caller_stack.py
