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
