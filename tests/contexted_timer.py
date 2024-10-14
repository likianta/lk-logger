import lk_logger
from time import sleep

with lk_logger.timing():
    sleep(0.5)
print(':t', 'aaa')

with lk_logger.timing('bbb'):
    sleep(0.5)

# should raise a TypeError:
#   TypeError: timing() got some positional-only arguments passed as keyword
#   arguments: 'left_message'
with lk_logger.timing(left_message='ccc'):
    sleep(0.5)

# pox tests/contexted_timer.py
