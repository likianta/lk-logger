import lk_logger
lk_logger.setup(show_varnames=True)


def test_control():
    print('lk logging')
    
    lk_logger.disable()
    print('lk logging disabled')
    
    lk_logger.enable()
    print('lk logging enabled')

    lk_logger.unload()
    print('built-in print')
