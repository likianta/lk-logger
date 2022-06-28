class LoggingConfig:
    """
    options:
        show_source: bool[true]
            add source info (filepath and line number) prefix to log messages.
            example:
                lk.log('hello world')
                # enabled : './main.py:10  >>  hello world'
                # disabled: 'hello world'
        show_varnames: bool[false]
            show both var names and values. (magic reflection)
            example:
                a, b = 1, 2
                lk.log(a, b, a + b)
                # enabled : 'main.py:11  >>  a = 1; b = 2; a + b = 3'
                # disabled: 'main.py:11  >>  1, 2, 3'
        show_external_lib: bool[true]
            if `param source` came from an external library, whether to print.
            for example, if a third-party library 'xxx' also used `lk.log`,
            its source path (relative to current working dir) may be very long,
            if you don't want to see any prints except your own project, you'd
            set this to False.

        # the following options are only available if `show_external_lib` is
        # true.
        path_format_for_external_lib: literal
            literal:
                'pretty_relpath': default
                    trunscate the source path of external lib to be shorter.
                    example:
                        before:
                            '../../../../site-packages/lk_logger/sourcemap.py'
                            # there may be a lot of '../'.
                        after:
                            '[lk_logger]/sourcemap.py'
                'relpath':
                    a relative path to current working dir. (<- `os.getcwd()`)
                    note there may be a lot of '../../../...' if external lib
                    is far beyond the current working dir.
                'lib_name_only':
                    show only the library name (surrounded by brackets).
                    example: '[lk_logger]'
            ps: if you don't want to show anything, you should turn to set
            `show_external_lib` to False.
    """
    show_source = True
    show_varnames = False
    show_external_lib = True
    path_format_for_external_lib = 'pretty_relpath'
    separator = ';   '  # suggests: ';   ' | ';\t' | '    ' | ...
    
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(LoggingConfig, k):
                setattr(self, k, v)
    
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
    
    def reset(self):
        self.show_source = True
        self.show_varnames = False
        self.show_external_lib = True
        self.path_format_for_external_lib = 'pretty_relpath'
