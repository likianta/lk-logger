"""
run ipython:
    from tests import source_info_in_ipython
    source_info_in_ipython.bbb()
    
    def ddd():
        print('eee')
    ddd()
"""

import lk_logger
lk_logger.setup(show_source=True)

print('aaa')


def bbb():
    print('ccc')
