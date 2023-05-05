import lk_logger

lk_logger.setup()


def _try_to_do_something_wrong():
    return 3 / 0


def catch_and_print():
    try:
        _try_to_do_something_wrong()
    except Exception as e:
        print(':e', e)
        # print(':l', e)
    print('over')


if __name__ == '__main__':
    catch_and_print()
