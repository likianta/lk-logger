import builtins

default_print = builtins.print


def normpath(path: str) -> str:
    return path.replace('\\', '/').rstrip('/')
