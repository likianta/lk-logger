from lk_logger import lk


def complicated_nest_structure():
    lk.loga({
        'a': 'aa',
        'b': 'bb',
        'c': {
            (x := 'cc'): None,
            (
                'd', 'dd',
            )          : {x: x + x * len(x)}
        }
    }, x)


def general_control():
    lk.switch_mode('full_mode')
    lk.loga('enabled')
    lk.enable_lite_mode()
    lk.loga('lite mode enabled')
    lk.disable()
    lk.loga('nothing print')
    try:
        lk.disable_lite_mode()
    except Exception as e:
        print(e)
        lk.switch_mode('full_mode')
        lk.disable_lite_mode()
    lk.loga('full mode enabled')


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


def lambda_occurances():
    lk.loga(lambda *args, **kwargs: (len(args), len(kwargs)))
    lk.loga((lambda *args, **kwargs: (len(args), len(kwargs)))(1, 2, a=3))


def black_magic():
    from lk_logger import setup_as_builtin_print
    setup_as_builtin_print()
    a = 1
    b = 2
    print(a, b, a + b)


def main():
    complicated_nest_structure()
    general_control()
    hierarchy_reflections()
    lambda_occurances()


if __name__ == '__main__':
    # complicated_nest_structure()
    # general_control()
    # hierarchy_reflections()
    # lambda_occurances()
    black_magic()
    # main()
