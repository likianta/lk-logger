"""
enter ipython:
    print('hello')  # output 'hello'
    
    import lk_logger
    print('hello')  # still output 'hello'
    
    lk_logger.setup(quiet=True)
    print('hello')  # output `<source> <sep> <module> <sep> hello`
    print('[red]hello[/]', ':r')  # output same as above, but in red color
"""
