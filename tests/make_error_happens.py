from argsense import cli

import lk_logger

lk_logger.setup()


@cli.cmd()
def raise_an_error(show_locals: bool = False) -> None:
    if show_locals:
        lk_logger.update(show_traceback_locals=True)
    print('raise an zero assertion error...', ':v4s')
    a, b = 1, 0
    print(a / b)


@cli.cmd()
def catch_an_error() -> None:
    try:
        raise_an_error()
    except ZeroDivisionError as e:
        print(':d', 'here is the error caught')
        print(':e', e)
        print('over')


@cli.cmd()
def save_error_to_image(ext: str = 'png') -> None:
    try:
        raise_an_error()
    except ZeroDivisionError as e:
        lk_logger.save_error_to_image(e, f'tests/_error.{ext}')


@cli.cmd('raise-an-error-2')
def test_exception_panel_on_a_narrow_width() -> None:
    lk_logger.update(console_width=60)
    raise_an_error()


if __name__ == '__main__':
    # pox tests/make_error_happens.py raise-an-error
    # pox tests/make_error_happens.py raise-an-error --show-locals
    # pox tests/make_error_happens.py raise-an-error-2
    # pox tests/make_error_happens.py catch-an-error
    # pox tests/make_error_happens.py save-error-to-image
    cli.run()
