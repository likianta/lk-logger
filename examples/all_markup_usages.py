import lk_logger
lk_logger.setup(show_varnames=True)

# -----------------------------------------------------------------------------
print(':d', '`:i` usage')

print(':i', 'sunday')
print(':i', 'monday')
print(':i', 'tuesday')
print(':i', 'wednesday')
print(':i', 'thursday')
print(':i', 'friday')
print(':i', 'saturday')
print(':i0')
print(':i', 'sunday in new week')
print(':i', 'monday in new week')
print(':i', 'tuesday in new week')
print(':i', 'wednesday in new week')
print(':i', 'thursday in new week')
print(':i', 'friday in new week')
print(':i', 'saturday in new week')

# -----------------------------------------------------------------------------
print(':d', '`:l` usage')

print(':l', {
    'name': 'John',
    'age': 30,
    'address': {
        'country': 'USA',
        'city': 'New York',
        'street': 'Wall Street'
    }
})

# -----------------------------------------------------------------------------
print(':d', '`:p` usage')


def func1():
    print('who is calling me?')
    print('i am', ':p1')
    return 'ok'


response = func1()
print(response)

# -----------------------------------------------------------------------------
print(':d', '`:r` usage')

print(':r', '[cyan]hello[/] [yellow]world[/]')

# -----------------------------------------------------------------------------
print(':d', '`:s` usage')

a, b = 1, 2
print(':s', a, b, a + b)

# -----------------------------------------------------------------------------
print(':d', '`:t` usage')

print(':t', 'for now')

# -----------------------------------------------------------------------------
print(':d', '`:v` usage')

print(':v0', 'this is a TRACE message')
print(':v1', 'this is a DEBUG message')
print(':v2', 'this is a INFO  message')
print(':v3', 'this is a WARN  message')
print(':v4', 'this is a ERROR message')
print(':v5', 'this is a FATAL message')

a, b, c = 1, 2, 3
print(':v', a, b, c)
