import lk_logger

lk_logger.setup()


def try_to_do_something_wrong():
    return 3 / 0


try_to_do_something_wrong()
