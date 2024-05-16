import lk_logger

lk_logger.setup()

print('raise an exception...')
print(1 / 0)

# pox tests/raise_exception.py
