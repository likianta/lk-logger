from random import randint
from time import sleep

from argsense import cli

from lk_logger import logger


@cli.cmd()
def elevate_caller_stack() -> None:
    def aaa() -> None:
        print(':p', 'hello')
    
    def bbb() -> None:
        with logger.elevate_caller_stack():
            aaa()  # the source pointer of `aaa:print` should point to its caller
        aaa()  # `aaa:print` should point here
    
    bbb()


@cli.cmd()
def counting() -> None:
    for _ in range(2):
        with logger.counting():
            print(':i', 'one')
            print(':i', 'two')
            print(':i', 'three')


@cli.cmd()
def timing() -> None:
    for _ in range(2):
        with logger.timing():
            sleep(randint(100, 1000) / 1000)
            print(':t', 'done')
        sleep(1)


if __name__ == '__main__':
    # pox tests/scoped_test.py elevate-caller-stack
    # pox tests/scoped_test.py counting
    cli.run()
