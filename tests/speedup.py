from time import time

import lk_logger

lk_logger.setup()
# lk_logger.setup(async_=True)
# lk_logger.setup(clear_unfinished_stream=True)


def simple_loop() -> None:
    temp = time()
    ls = []
    for i in range(1000):
        ls.append(i)
    duration = time() - temp
    print('{:.3f} ms'.format(duration * 1000))
    del ls
    
    ls = []
    with lk_logger.timing(True):
        for i in range(1000):
            ls.append(i)
            lk_logger.bprint(i, end='\r')
    
    ls = []
    with lk_logger.timing(True):
        for i in range(1000):
            ls.append(i)
            print(i, end='\r')
            # print(i)


if __name__ == '__main__':
    # pox tests/speedup.py
    simple_loop()
