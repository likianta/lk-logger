# from IPython import start_ipython
from lk_logger import start_ipython


def print_xx():
    print('[red]hello[/] [green]world[/]', ':r')


start_ipython(user_ns=globals())