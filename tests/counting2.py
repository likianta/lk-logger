# example.py
import lk_logger
lk_logger.setup(show_funcname=True)

print(':i', 'aaa')
print(':i', 'bbb')
print(':i', 'ccc')

for x in ('ddd', 'eee', 'fff'):
    print(':i', '--- ' + x)
    for y in ('ggg', 'hhh', 'iii'):
        print(':i', '------ ' + y)


def foo():
    print(':i', 'ggg')
    print(':i', 'hhh')
    print(':i', 'iii')
    
    for x in ('jjj', 'kkk', 'lll'):
        print(':i', '--- ' + x)
        for y in ('mmm', 'nnn', 'ooo'):
            print(':i', '------ ' + y)


foo()
foo()
