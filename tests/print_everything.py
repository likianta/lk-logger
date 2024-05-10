import lk_logger
lk_logger.setup(show_varnames=True)


def test_print_values():
    import os
    
    print(1)
    print(1, 2, 1 + 2, 1 / 2, {'a': 'aaa'})
    
    a, b = 1, 2
    print(a, b)
    print(a, b, (c := a + b), c)
    
    print('yes' if 1 + 1 == 2 else 'no')
    
    print(os.getcwd())
    print(os.getcwd().split('\\'))
    print(os.getcwd().format(..., ..., ))
    
    print('''
        hello
        world
    ''')


def test_print_empty():
    print()
    print('')
    print(())
    print(None)


def test_print_complicate_values():
    print(print)
    print(print(print))
    
    # lambda
    print(lambda x: None)
    print((lambda x: x + 1)(1))
    print(lambda *args, **kwargs: (len(args), len(kwargs)))
    print((lambda *args, **kwargs: (len(args), len(kwargs)))(1, 2, a=3))

    print(list(
        ('a', 'b', 'cccccccccccccccccccc',
         d := None, e := False,
         d, e)
    ))
    
    print({
        'a': 'aa',
        'b': 'bb',
        'c': {
            (x := 'cc'): None,
            (
                'd', 'dd',
            )          : {x: x + x * len(x)}
        }
    }, x)


if __name__ == '__main__':
    test_print_values()
    test_print_empty()
    test_print_complicate_values()
