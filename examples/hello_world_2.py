import lk_logger
from time import sleep

lk_logger.setup(show_varnames=True)

print('hello world')

a, b = 1, 2
print(a, b, a + b)

print(':i', 'monday')
print(':i', 'tuesday')
print(':i', 'wednesday')

sleep(50e-3)
print(':t', 'done')
