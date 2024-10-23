import lk_logger
lk_logger.setup()

for i in range(10):
    print(i)

print(input)
name = input('what is your name? ')
# name = input('what is your name? ', 1)
# name = lk_logger.input('what is your name? ', 1)
print(f'hello {name}')
