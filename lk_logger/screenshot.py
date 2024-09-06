import os
import typing as t
from contextlib import redirect_stdout
from shutil import move

import rich.terminal_theme
from rich.traceback import Traceback

from .console import console
from .message_builder import builder


def save_error_to_image(
    error: BaseException, path: str, show_locals: bool = True
) -> str:
    """
    test case: tests/make_error_happens.py : save_error_to_image
    """
    assert path.endswith(('.html', '.png', '.svg', '.txt')), path
    path_htm = path if path.endswith('.html') else ''
    path_png = path if path.endswith('.png') else ''
    path_svg = path if path.endswith('.svg') else ''
    path_txt = path if path.endswith('.txt') else ''
    # path_tmp = '' if path.endswith('.png') else '__lk_logger_temp.svg'
    path_tmp = '__lk_logger_temp.html' if path.endswith('.png') else ''
    path_out = path_png or path_htm or path_svg or path_txt
    
    traceback = builder.compose_exception(error, show_locals)
    console.record = True
    # temp redirect stdout to DEVNULL
    with redirect_stdout(open(os.devnull, 'w')):
        console.print(traceback, soft_wrap=False)
        # console.print(rich.align.Align(traceback, align='center'))
    if path_htm:
        console.save_html(path_htm, theme=rich.terminal_theme.MONOKAI)
        _fix_font_face(path_htm)
    elif path_svg:
        console.save_svg(path_svg, title='Error Stack Trace')
    elif path_txt:
        console.save_text(path_txt)
    else:
        console.save_html(path_tmp, theme=rich.terminal_theme.MONOKAI)
        _fix_font_face(path_tmp)
    console.record = False
    
    if not path_png:
        print('[green dim]the error stack image is saved to "{}"[/]'
              .format(path_out), ':rp')
        return path_out
    
    # convert `path_tmp` to `path_png`
    try:
        from html2image import Html2Image
    except ImportError:
        path_out = '{}.{}'.format(path_out[:-4], path_tmp.rsplit('.', 1)[1])
        print(
            '"html2image" is not installed, cannot generate png file '
            '(fallback to "{}")'.format(path_out),
            ':pv4'
        )
        _move_and_overwrite(path_tmp, path_out)
        return path_out
    
    # workaround: html2image can only generate result in the current working
    # directory. we should move the result to the target path.
    size_ch = _get_dimension_info(traceback)  # character size
    size_px = (round(size_ch[0] * 8.2), round(size_ch[1] * 17.5))
    #   character size in pixel
    print(size_ch, size_px, ':v')
    with redirect_stdout(open(os.devnull, 'w')):  # FIXME: mute doesn't work
        Html2Image().screenshot(
            html_file=path_tmp, save_as='__lk_logger_temp.png', size=size_px
        )
    _move_and_overwrite('__lk_logger_temp.png', path_png)
    os.remove(path_tmp)
    
    print('[green dim]the error stack image is saved to "{}"[/]'
          .format(path_png), ':rp')
    return path_png


def _fix_font_face(html_file: str) -> None:
    """
    the default font-family in <pre> tag (<pre style="font-family:Menlo,'DejaVu
    Sans Mono',consolas,'Courier New',monospace>...</pre>) doesn't look good,
    we need to change it to 'monospace'.
    """
    with open(html_file, 'r') as f:
        content = f.read()
    old = '''<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas''' + \
          ''','Courier New',monospace">'''
    # new = '''<pre style="font-family:monospace">'''
    new = '''<pre style="font-family: 'Agave Nerd Font Regular'">'''
    assert old in content, \
        'please check the <pre> tag in this file: ' + html_file
    content = content.replace(old, new, 1)
    with open(html_file, 'w') as f:
        f.write(content)


def _get_dimension_info(traceback: Traceback) -> t.Tuple[int, int]:
    console.record = True
    with redirect_stdout(open(os.devnull, 'w')):
        console.print(traceback, soft_wrap=False)
    console.save_text('__lk_logger_temp.txt')
    console.record = False
    with open('__lk_logger_temp.txt', 'r') as f:
        lines = f.readlines()
        width = max(len(line) for line in lines)
        height = len(lines)
    os.remove('__lk_logger_temp.txt')
    return width, height


def _move_and_overwrite(src: str, dst: str) -> None:
    if os.path.exists(dst):
        os.remove(dst)
    move(src, dst)
