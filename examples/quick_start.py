import lk_logger

lk_logger.setup(show_varnames=True)

print('hello world')

a = 1
b = 2
print(a + b)
print(a, b, a + b)

print(':i', 'monday')
print(':i', 'tuesday')
print(':i', 'wednesday')

print(':d', 'this is a divider line')
print(':r', '[blue]this is a[/] [yellow]rich text[/]')

print(':v0', 'this is a DEBUG message')
print(':v2', 'this is a INFO  message')
print(':v4', 'this is a WARN  message')
print(':v6', 'this is a ERROR message')

x = {
    'name'   : 'Johnnie',
    'age'    : 42,
    'address': {
        'country' : 'USA',
        'city'    : 'New York',
        'zip'     : '10001'
    },
}
print(x, ':l')


def func1():
    print('who is calling me?')
    print('i am', ':p1')
    return 'ok'


response = func1()
print(response)
