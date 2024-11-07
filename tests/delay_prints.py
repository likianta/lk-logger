from time import sleep

from lk_logger import spinner
from lk_logger import track

with spinner('working...'):
    for i in range(10):
        print('A', i)
        sleep(0.1)

for i in track(range(10)):
    print('B', i)
    sleep(0.1)

# pox tests/delay_prints.py
