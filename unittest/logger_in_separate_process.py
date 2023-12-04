from time import sleep

import lk_logger

lk_logger.setup()

for i in range(10):
    print(f'hello world {i}')
    sleep(100e-3)

if __name__ == '__main__':
    sleep(1)

# pox unittest/logger_in_separate_process.py
