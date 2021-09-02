from lk_logger import lk


def print_values():
    lk.loga(1)
    lk.loga(1, 2, 3)
    lk.loga(1, 2, 3, True)
    lk.loga(1, 2, 3, True, [])
    lk.loga(1, 2, 3, True, {})
    lk.loga(1, 2, 3, True, {'a': 'aa'})


def print_values_with_varnames():
    a = 1
    b = 2
    c = 'c'
    d = 'd'
    
    lk.loga(a)
    lk.loga(a, b, c)
    lk.loga(a, b, a + b)
    lk.loga(a, b, e := (a + b), e)
    lk.loga({a: b, c: d})


def print_with_linebreaks():
    a = 1
    b = 2
    
    lk.loga(1,
            2,
            3, )
    lk.loga({
        'a': 'aa',
        'b': 'bb',
    })
    lk.loga('''
        """
        xxx
        yyy
        \\\'
    ''')
    lk.loga(a, r'''
        """
        xxx
        yyy
        \\\'
        {}
    '''.format(b), b)


def hierarchy_reflections():
    def _aaa():
        def _bbb():
            def _ccc():
                def _ddd():
                    a = 123
                    lk.loga('assert _ddd.<here>', a, h='self')
                    lk.loga('assert _ccc._ddd()', a, h='parent')
                    lk.loga('assert _bbb._ccc()', a, h='grand_parent')
                    lk.loga('assert _aaa._bbb()', a, h='great_grand_parent')
                    lk.loga('assert main._aaa()', a, h=5)
                    lk.loga('assert root.main()', a, h=6)
                    try:
                        lk.loga('assert ...', a, h=7)
                    except AssertionError as e:
                        lk.loga('assert outbound error happend', e)
                
                _ddd()  # _ccc._ddd()
            
            _ccc()  # _bbb._ccc()
        
        _bbb()  # _aaa._bbb()
    
    _aaa()  # main._aaa()


if __name__ == '__main__':
    # print_values()
    # print_values_with_varnames()
    # print_with_linebreaks()
    hierarchy_reflections()
