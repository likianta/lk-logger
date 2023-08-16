from time import sleep

import lk_logger

lk_logger.setup()

print(':t0')

print(':t', 'ONE')
sleep(0.3)
print(':t', 'TWO')
sleep(0.7)
print(':t', 'THREE')
sleep(1.2)
print(':t', 'FOUR')
sleep(5)
print(':t', 'FIVE')

# -----------------------------------------------------------------------------

print(':d', 'the temporary timer')
print(':t0s')
print(':t2s')  # this is a  trick to reset temp timer.

sleep(0.3)
print(':t2', '1st end')
sleep(0.7)
print(':t2', '2nd end')
sleep(1.2)
print(':t2', '3rd end')

print(':dt')
