import lk_logger
from lk_logger.console import console

lk_logger.setup()


def normal():
    print(':d', 'aaa')
    print(':di', 'bbb')
    print(':di', 'ccc')
    

def narrow_width():
    # console.width = 80
    print(':d', 'long string ' * 10)


if __name__ == '__main__':
    normal()
    narrow_width()
