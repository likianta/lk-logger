import os
import subprocess as sp
import sys


def serve_screenshots() -> None:
    from .screenshot import _get_local_ip_address
    from .screenshot import _output_dir
    print('serving at http://{}:2002'.format(_get_local_ip_address()))
    sp.run(
        (sys.executable, '-m', 'http.server', '2002', '-d', _output_dir),
        stdout=sp.PIPE, stderr=sp.PIPE,
    )


def clear_cache() -> None:
    from .screenshot import _output_dir
    for f in os.listdir(_output_dir):
        if f != '.gitkeep':
            print(':ri', '[red]remove {}[/]'.format(f))
            os.remove(os.path.join(_output_dir, f))


if __name__ == '__main__':
    # py -m lk_logger serve-screenshots
    # py -m lk_logger clear-cache
    cmd = sys.argv[1]
    if cmd == 'serve-screenshots':
        serve_screenshots()
    elif cmd == 'clear-cache':
        clear_cache()
    else:
        raise ValueError('invalid command: {}'.format(cmd))
