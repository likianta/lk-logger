from time import sleep

import lk_logger

lk_logger.setup(
    show_source=True,
    show_funcname=True,
    show_varnames=True,
    sourcemap_alignment='right',
)

_a, _b = 1, 2


def normal():
    lk_logger.update(console_width=200)
    print(':di', 'console_width=200')
    print('hello world')
    print(_a, _b, _a + _b)
    print('hello world ' * 5)
    print('hello world ' * 5 + '\n' + 'hello world ' * 5)
    print(':fs')


def narrow() -> None:
    sleep(0.5)
    lk_logger.update(console_width=100)
    print(':di', 'console_width=100')
    print('hello world')
    print(_a, _b, _a + _b)
    print('hello world ' * 5)
    print('hello world ' * 5 + '\n' + 'hello world ' * 5)
    print(':fs')


def very_narrow():
    sleep(0.5)
    lk_logger.update(console_width=40)
    print(':di', 'console_width=40')
    print('hello world ' * 5)
    print('hello world ' * 5 + '\n' + 'hello world ' * 5)
    print(':fs')


if __name__ == '__main__':
    normal()
    narrow()
    very_narrow()
