import argsense
from argsense import cli

import lk_logger

lk_logger.setup()
print(argsense.__version__)


@cli.cmd()
def raise_an_error(show_locals: bool = False) -> None:
    if show_locals:
        lk_logger.update(show_traceback_locals=True)
    print('raise an zero assertion error...', ':v4s')
    a, b = 1, 0
    print(a / b)


@cli.cmd('raise-an-error-2')
def test_exception_panel_on_a_narrow_width() -> None:
    lk_logger.update(console_width=60)
    raise_an_error()


if __name__ == '__main__':
    # pox tests/raise_exception.py raise-an-error
    # pox tests/raise_exception.py raise-an-error --show-locals
    # pox tests/raise_exception.py raise-an-error-2
    cli.run()
