def setup_as_builtin_print():
    import builtins
    from .terminals.pycharm_console import lk
    setattr(builtins, 'print', lk.loga)
