import contextlib
import os
import shutil
import socket
import sys
import typing as t
from contextlib import redirect_stdout
from textwrap import dedent
from time import time

import rich.terminal_theme
from rich.traceback import Traceback

from .console import console
from .message_builder import builder

# ref: misc/compose_terminal_theme.py
_CATPPUCCIN_MACCHIATO_THEME = rich.terminal_theme.TerminalTheme(
    (36, 39, 58),
    (202, 211, 245),
    [
        (73, 77, 100),
        (237, 135, 150),
        (166, 218, 149),
        (238, 212, 159),
        (138, 173, 244),
        (245, 189, 230),
        (139, 213, 202),
        (184, 192, 224),
    ],
    [
        (91, 96, 120),
        (237, 135, 150),
        (166, 218, 149),
        (238, 212, 159),
        (138, 173, 244),
        (245, 189, 230),
        (139, 213, 202),
        (165, 173, 203),
    ],
)

_output_dir = os.getenv(
    'LK_LOGGER_SCREENSHOT_DIR',
    os.path.normpath('{}/../_screenshots'.format(__file__))
)


def save_error(
    error: BaseException, path: str = None, show_locals: bool = True
) -> str:
    """
    test case: tests/make_error_happens.py : save_error
    params:
        path:
            support '.html', '.png', '.svg', '.txt'.
            suggest '.html', it has the smallest size and color highlights.
    """
    if path is None:
        path = '{}/{}.html'.format(_output_dir, int(time() * 1000))
    assert path.endswith(('.html', '.png', '.svg', '.txt')), path
    path_htm = path if path.endswith('.html') else ''
    path_png = path if path.endswith('.png') else ''
    path_svg = path if path.endswith('.svg') else ''
    path_txt = path if path.endswith('.txt') else ''
    path_tmp = '__lk_logger_temp.svg' if path.endswith('.png') else ''
    # path_tmp = '__lk_logger_temp.html' if path.endswith('.png') else ''
    path_out = path_png or path_htm or path_svg or path_txt
    path_url = (  # str | False | None
        path.endswith('.html') and
        (url := _is_serving_url()) and
        '{}/{}'.format(url, os.path.basename(path_htm))  # noqa
    )
    
    bak = console.width
    console.width = 120
    console.record = True
    # temp redirect stdout to DEVNULL
    with redirect_stdout(open(os.devnull, 'w')):
        traceback = builder.compose_exception(error, show_locals)
        console.print(traceback, soft_wrap=False)
        # console.print(rich.align.Align(traceback, align='center'))
    if path_htm:
        # console.save_html(path_htm, theme=rich.terminal_theme.MONOKAI)
        console.save_html(path_htm, theme=_CATPPUCCIN_MACCHIATO_THEME)
        _fix_font_face(path_htm)
    elif path_svg:
        console.save_svg(path_svg, title='Error Stack Trace')
    elif path_txt:
        console.save_text(path_txt)
    else:
        console.save_svg(path_tmp, title='Error Stack Trace')
        # console.save_html(path_tmp, theme=_CATPPUCCIN_MACCHIATO_THEME)
        # _fix_font_face(path_tmp)
    console.record = False
    console.width = bak
    
    if path_png:
        # with spinner('generating screenshot...'):
        #     _convert_html_to_png(path_tmp, path_png)
        _convert_svg_to_png(path_tmp, path_png)
        os.remove(path_tmp)
        print('[green dim]the error stack image is saved to "{}"[/]'
              .format(path_png), ':rp')
        return path_png
    else:
        if path_url:
            print('[green][dim]the error stack image is saved at:[/] '
                  '[b u]{}[/][/]'
                  .format(path_url), ':rp')
        else:
            print('[green dim]the error stack image is saved to "{}"[/]'
                  .format(path_out), ':rp')
        return path_out


# DELETE
def _convert_html_to_png(file_i: str, file_o: str) -> None:
    """
    this function requires selenium and chrome browser.
    if you encounter ImportError, remember to install selenium.
    FIXME: this is very slow (takes 7 ~ 30 seconds), we need to find a better
        way.
    """
    # noinspection PyUnresolvedReferences
    from selenium import webdriver
    # noinspection PyUnresolvedReferences
    from selenium.webdriver.chrome.options import Options
    
    opt = Options()
    opt.add_argument('--disable-dev-shm-usage')
    opt.add_argument('--disable-extensions')
    opt.add_argument('--disable-gpu')
    opt.add_argument('--headless=new')
    opt.add_argument('--hide-scrollbars')
    opt.add_argument('--no-sandbox')
    opt.add_argument('--log-level=3')
    # opt.add_argument('--window-size=800,800')
    opt.add_experimental_option('excludeSwitches', ['enable-logging'])
    opt.set_capability('browserVersion', '117')
    
    driver = webdriver.Chrome(options=opt, keep_alive=False)
    
    driver.get('file:///{}'.format(os.path.abspath(file_i).replace('\\', '/')))
    from time import sleep
    sleep(0.5)
    
    element = driver.find_element(value='my-code')
    print((element.size['width'], element.size['height']), ':vs')
    driver.set_window_size(
        element.size['width'] + 60, element.size['height'] + 100
    )
    element.screenshot(file_o)
    driver.close()
    driver.quit()


def _convert_svg_to_png(file_i: str, file_o: str) -> None:
    """
    this function requires svg-ultralight and [inkspace](
    https://inkscape.org/release/inkscape-1.3.2/windows/64-bit/).
    the inkspace package is recommended 7z format.
    add inkspace executable to "INKSPACE_EXE" environment.
    """
    import svg_ultralight
    inkspace = os.environ['INKSPACE_EXE']
    svg_ultralight.write_png_from_svg(inkspace, file_i, file_o)


def _fix_font_face(html_file: str) -> None:
    """
    the default font-family in <pre> tag (<pre style="font-family:Menlo,'DejaVu
    Sans Mono',consolas,'Courier New',monospace>...</pre>) doesn't look good,
    we need to change it to 'monospace'.
    """
    with open(html_file, 'r') as f:
        content = f.read()
    old = dedent(
        '''
        <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier \\
        New',monospace">
        '''
    ).strip().replace(' \\\n', ' ')
    new = dedent(
        '''
        <pre style="font-family: 'Cascadia Mono', 'Agave Nerd Font Regular', \\
        Menlo, 'DejaVu Sans Mono', consolas, 'Courier New', monospace; \\
        padding: 12px;" id="my-code">
        '''
    ).strip().replace(' \\\n', ' ')
    assert old in content, \
        'please check the <pre> tag in this file: ' + html_file
    content = content.replace(old, new, 1)
    with open(html_file, 'w') as f:
        f.write(content)


# DELETE
def _get_dimension_info(traceback: Traceback) -> t.Tuple[int, int]:
    bak = console.width
    console.width = 120
    console.record = True
    with redirect_stdout(open(os.devnull, 'w')):
        console.print(traceback, soft_wrap=False)
    console.save_text('__lk_logger_temp.txt')
    console.record = False
    console.width = bak
    
    with open('__lk_logger_temp.txt', 'r') as f:
        lines = f.readlines()
        width = max(len(line) for line in lines)
        height = len(lines)
    os.remove('__lk_logger_temp.txt')
    return width, height


def _get_local_ip_address() -> str:
    # https://stackoverflow.com/a/166520/9695911
    if sys.platform == 'linux':
        return socket.gethostbyname(socket.getfqdn())
    else:
        return socket.gethostbyname(socket.gethostname())


def _is_serving_url() -> t.Optional[str]:
    host, port = _get_local_ip_address(), 2002
    with contextlib.closing(
        socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ) as s:
        s.settimeout(5e-3)  # 5ms
        try:
            s.connect((host, port))
        except TimeoutError:
            return None
        else:
            return 'http://{}:{}'.format(host, port)


def _move_and_overwrite(src: str, dst: str) -> None:
    if os.path.exists(dst):
        os.remove(dst)
    shutil.move(src, dst)
