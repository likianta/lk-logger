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

# -----------------------------------------------------------------------------

"""
this example is often used for an ipython console.
here is a classic use case:
    import lk_logger
    from IPython import start_ipython  # pip install ipython
    
    lk_logger.setup(quiet=True,
                    show_source=False,
                    show_funcname=False,
                    show_varnames=False)
    start_ipython(user_ns=globals())
"""
