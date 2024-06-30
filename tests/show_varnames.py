from argsense import cli

import lk_logger

lk_logger.setup(show_varnames=True)


@cli.cmd()
def simple():
    a = 1
    b = 2
    print(a, b, a + b)


if __name__ == '__main__':
    cli.run()
