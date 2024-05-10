import lk_logger

lk_logger.setup(show_varnames=True)


def test_d__divider_line():
    pass


def test_l__loose_format():
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


def test_p__parent_layer():
    def _aaa():
        def _bbb():
            def _ccc():
                def _ddd():
                    a = 123
                    print('assert _ddd.<here>', a, ':p0')
                    print('assert _ccc._ddd()', a, ':p1')
                    print('assert _bbb._ccc()', a, ':p2')
                    print('assert _aaa._bbb()', a, ':p3')
                    print('assert main._aaa()', a, ':p4')
                    print('assert root.main()', a, ':p5')
                    try:
                        print('assert ...', a, ':p6')
                    except AttributeError as e:
                        print('assert outbound error happend', e, ':v4')
                
                _ddd()  # _ccc._ddd()
            
            _ccc()  # _bbb._ccc()
        
        _bbb()  # _aaa._bbb()
    
    _aaa()  # main._aaa()


def test_s__short():
    a, b = 1, 2
    
    # test `:s0`
    print(a, b, a + b, ':s')
    
    # test `:s1`
    print(a, b, a + b, ':s1')
    
    # `:s` shouldn't break no effect expression.
    print('hello world', ':s')


# -----------------------------------------------------------------------------

def test_nested_color_scope():
    print(':rv2', '[green]hello[/] [red]world[/] hi')
    print(':v3', 'aaa', 'bbb', 123)


if __name__ == '__main__':
    test_d__divider_line()
    test_l__loose_format()
    test_p__parent_layer()
    test_s__short()
    test_nested_color_scope()
