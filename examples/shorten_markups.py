import lk_logger

lk_logger.setup(show_varnames=True)


def shorten_verbosities() -> None:
    a, b = 1, 2
    print(':vs', a, b)
    print(':v1s', a, b)
    print(':v2s', a, b)
    print(':v3s', a, b)
    print(':v4s', a, b)
    print(':v5s', a, b)


def shorten_rich_style() -> None:
    a, b = 1, 2
    print(':s0r', '[green]hello world[/]', a, b)
    print(':s1r', '[green]hello world[/]', a, b)
    print(':s2r', '[green]hello world[/]', a, b)


if __name__ == '__main__':
    shorten_verbosities()
    shorten_rich_style()
