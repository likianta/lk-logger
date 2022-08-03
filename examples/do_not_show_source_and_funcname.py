import lk_logger

lk_logger.setup(quiet=True, show_source=False, show_funcname=False)

print(':d', 'show varnames')
lk_logger.setup(show_varnames=True)

print('hello world')

a, b = 1, 2
print(a, b, a + b)

# -----------------------------------------------------------------------------

print(':d', 'do not show varnames')
lk_logger.setup(show_varnames=False)

print('hello world')

a, b = 1, 2
print(a, b, a + b)
