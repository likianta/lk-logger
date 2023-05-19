import lk_logger

lk_logger.setup()


def normal():
    print(':d', 'aaa')
    print(':di', 'bbb')
    print(':di', 'ccc')


def narrow_width():
    # console.width = 80
    print(':d', ('long string ' * 10).rstrip())


if __name__ == '__main__':
    normal()
    narrow_width()
