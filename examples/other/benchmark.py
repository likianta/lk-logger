from time import time
from uuid import uuid1

import lk_logger


def forloop(print):  # noqa
    lk_logger.bprint('start', (s := time()))
    for i in range(1000):
        print(i, uuid1().hex)
    lk_logger.bprint('end', (d := time() - s))
    return d


if __name__ == '__main__':
    d0 = forloop(print)
    
    # d1 = forloop(lk_logger.console.con_print)
    
    lk_logger.setup(quiet=True, show_varnames=True)
    d2 = forloop(lk_logger.logger.log)
    
    print('{:5.2f}, {:5.2f}, {:5.2f}'.format(
        d0, d2, d2 / d0
    ))
    
    # print('{:.2f}, {:.2f}, {:.2f}\n'
    #       '{:.2f}, {:.2f}, {:.2f}'.format(
    #     d0, d1, d2,
    #     d1 / d0, d2 / d0, d2 / d1
    # ))
