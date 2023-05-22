# from IPython import start_ipython
from lk_logger import start_ipython


def hello_world():
    print('[red]hello[/] [green]world[/]', ':r')


if __name__ == '__main__':
    print('call `hello_world` to see the effect')
    start_ipython(user_ns=globals())
    '''
    hello_world()
    print(':i', 'abc')
    print('[green]hello[/] [red]world[/]', ':r')
    '''
