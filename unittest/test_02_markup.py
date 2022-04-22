import lk_logger
lk_logger.setup(show_varnames=True)


def test_loose_format():
    print({
        'name'                             : 'joe',
        'age'                              : 32,
        
        # special colors for int, bool, None, type, builtin, etc.
        123                                : True,
        456                                : False,
        789                                : None,
        float                              : 1.23,
        open                               : lambda x: None,
        
        # test builtin keywords
        'eval'                             : 'eval',
        'print'                            : 'print',
        
        # is there markup parsing error?
        '[!rainbow]hello[/!rainbow]'       : 'world',
        '[!gradient(197)]hello[/!gradient]': '[blue]world[/]',
        '[invalid markup]hello[/]'         : '[!gradient(197)]world[/!gradient]',
        '[green]hello[/]'                  : '[cyan]None[/]',
    }, ':l')


def test_nested_color_scope():
    print(':rv2', '[green]hello[/] [red]world[/] hi')
    print(':v3', 'aaa', 'bbb', 123)
