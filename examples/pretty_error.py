import lk_logger

lk_logger.setup()


def try_to_do_something_wrong():
    return 3 / 0


def catch_and_print():
    try:
        try_to_do_something_wrong()
    except Exception as e:
        print(':l', e)


if __name__ == '__main__':
    # try_to_do_something_wrong()
    catch_and_print()
