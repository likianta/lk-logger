import lk_logger
from lk_logger import bprint

lk_logger.setup(quiet=True,
                show_source=True,
                show_funcname=True,
                show_varnames=True,
                async_=False)


def hide_source() -> None:
    lk_logger.update(show_source=True)
    print('no source prefix (before)', ':v4s')
    
    lk_logger.update(show_source=False)  # <- 1
    bprint(' ' * 40, end='')
    print('no source prefix  (after)', ':v2s')
    print('[dim]~[/]' * 40, ':rs1f')
    
    bprint()
    bprint()


def hide_funcname() -> None:
    lk_logger.update(show_funcname=True)
    print('no funcname prefix (before)', ':v4s')
    
    lk_logger.update(show_funcname=False)  # <- 2
    bprint(' ' * 20, end='')
    print('no funcname prefix  (after)', ':v2s')
    print('[dim]~[/]' * 20, ':rs1f')
    
    bprint()
    bprint()


def hide_varnames() -> None:
    a, b = '1', '2'
    c, d = 3, 4
    
    lk_logger.update(show_varnames=True)
    print('[red]no varname shown (before)[/]',
          a, b, a + b,
          c, d, c + d, ':r')
    
    bprint(' ' * 29, end='')
    # print('[dim]~[/]' * 59, ':rs1f')
    print('[dim]'
          '~~~~     '
          '~~~~     '
          '~~~~~~~~      '
          '~~~~     '
          '~~~~     '
          '~~~~~~~~      '
          '[/]', ':rs1f')
    
    lk_logger.update(show_varnames=False)  # <- 3
    print('[cyan]no varname shown  (after)[/]',
          a, b, a + b,
          c, d, c + d, ':r')
    
    bprint()
    bprint()


if __name__ == '__main__':
    hide_source()
    hide_funcname()
    hide_varnames()
