import lk_logger

lk_logger.setup(show_varnames=True)

# -----------------------------------------------------------------------------
print(':dr', '`:e` is [yellow][u]E[/]xception[/]')

try:
    raise Exception('this is an exception with locals info')
except Exception as e:
    print(':e1', e)

# -----------------------------------------------------------------------------
print(':dr', '`:i` is [yellow][u]I[/]ndexing[/]')

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
print(':dr', '`:l` is [yellow][u]L[/]ong/[u]L[/]oose[/] format')

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
print(':dr', '`:p` is [yellow][u]P[/]arent[/] frame')


def func1():
    print('who is calling me?')
    print('i am', ':p1')
    return 'ok'


response = func1()
print(response)

# -----------------------------------------------------------------------------
print(':dr', '`:r` is [yellow][u]R[/]ich[/] format')

print(':r', '[cyan]hello[/] [yellow]world[/]')

# print a rich renderable object
print(
    ':r2',
    '''
    # Hello World
    
    This is a markdown document.
    
    - item 1
    - item 2
    - item 3
    
    Find more usages at [rich](https://github.com/textualize/rich)
    documentation.
    '''
)

# automatically convert a dict to a table
print(':r2', {
    'Name': ('Alice', 'Bob', 'Charlie'),
    'Age': (18, 19, 20),
    'City': ('Shanghai', 'Beijing', 'Guangzhou'),
})

# -----------------------------------------------------------------------------
print(':dr', '`:s` [yellow][u]S[/]hort/[u]S[/]imple/[u]S[/]ingle-line[/] format')

a, b = 1, 2
print(':s', a, b, a + b)  # without varnames
print(':s1', a, b, a + b)  # similar to built-in print (but kept color style)
print(':s2', a, b, a + b)  # totally same with built-in print

# -----------------------------------------------------------------------------
print(':dr', '`:t` is [yellow][u]T[/]iming[/]')

print(':t', 'for now')

# -----------------------------------------------------------------------------
print(':dr', '`:v` is [yellow][u]V[/]erbosity[/]')

print(':v0', 'this is a  DEBUG            message')
print(':v1', 'this is an INFO (negative)  message')
print(':v2', 'this is an INFO (positive)  message')
print(':v3', 'this is a  SUCCESS (dimmed) message')
print(':v4', 'this is a  SUCCESS          message')
print(':v5', 'this is a  WARNING (dimmed) message')
print(':v6', 'this is a  WARNING          message')
print(':v7', 'this is an ERROR (dimmed)   message')
print(':v8', 'this is an ERROR            message')

a, b, c = 1, 2, 3
print(':v', a, b, c)
