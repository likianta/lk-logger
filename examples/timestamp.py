from time import sleep

import lk_logger

lk_logger.setup()

print(':t0')

print(':t', 'one')
sleep(0.3)
print(':t', 'two')
sleep(0.7)
print(':t', 'three')
sleep(1.2)
print(':t', 'four')
sleep(5)
print(':t', 'five')
