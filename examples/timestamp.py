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

# -----------------------------------------------------------------------------

print(':t0')

print(':t2', '1st start')
sleep(0.3)
print(':t3', '1st end')
sleep(0.7)
print(':t2', '2nd start')
sleep(1.2)
print(':t3', '2nd end')

print(':t')
