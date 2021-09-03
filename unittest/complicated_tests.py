from lk_logger import lk


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
    
    
def general_control():
    lk.enable()
    lk.loga('enabled')
    lk.enable_lite_mode()
    lk.loga('lite mode enabled')
    lk.disable()
    lk.loga('nothing print')
    try:
        lk.disable_lite_mode()
    except Exception as e:
        print(e)
        lk.enable()
        lk.disable_lite_mode()
    lk.loga('full mode enabled')


if __name__ == '__main__':
    # hierarchy_reflections()
    # lambda_occurances()
    general_control()
