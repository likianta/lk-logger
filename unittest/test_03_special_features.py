import lk_logger
lk_logger.setup(show_varnames=True)


def test_print_from_external_package():
    """
    prepare:
        1. create a package under `<python>/lib/site-packages`:
        
            ```
            ~/site-packages
            |= lk_logger_test_package
               |- hello.py
            ```
        
        2. source code:
        
            ```python
            print('[cyan]hello from other side[cyan]', ':r')
            def foo():
                print('[red]foo func[/]', ':r')
            foo()
            ```
    """
    from lk_logger_test_package import hello  # noqa


def test_parent_reflections():
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
                    except AssertionError as e:
                        print('assert outbound error happend', e)
                
                _ddd()  # _ccc._ddd()
            
            _ccc()  # _bbb._ccc()
        
        _bbb()  # _aaa._bbb()
    
    _aaa()  # main._aaa()
