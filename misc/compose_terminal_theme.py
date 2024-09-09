"""
convert catppuccion color scheme to rich.terminal_theme.TerminalTheme format.
"""
from argsense import cli
from lk_utils import fs
from lk_utils.textwrap import dedent
from lk_utils.textwrap import join


@cli.cmd()
def main(file: str) -> None:
    raw_scheme = fs.load(file)
    new_scheme = {
        'background': _hex_2_rgb(raw_scheme['background']),
        'foreground': _hex_2_rgb(raw_scheme['foreground']),
        'normal'    : (
            _hex_2_rgb(raw_scheme[x]) for x in (
                'black', 'red', 'green', 'yellow',
                'blue', 'magenta', 'cyan', 'white'
            )
        ),
        'bright'    : (
            _hex_2_rgb(raw_scheme[x]) for x in (
                'brightBlack', 'brightRed', 'brightGreen', 'brightYellow',
                'brightBlue', 'brightMagenta', 'brightCyan', 'brightWhite'
            )
        ),
    }
    fs.dump(
        dedent(
            '''
            from rich.terminal_theme import TerminalTheme
            theme = TerminalTheme(
                {},
                {},
                {},
                {},
            )
            '''
        ).format(
            # fs.barename(file),
            str(new_scheme['background']),
            str(new_scheme['foreground']),
            '[\n{}\n    ]'.format(join(
                (f'{x},' for x in new_scheme['normal']),
                indent_=8,
                lstrip=False,
            )),
            '[\n{}\n    ]'.format(join(
                (f'{x},' for x in new_scheme['bright']),
                indent_=8,
                lstrip=False,
            )),
        ),
        x := fs.replace_ext(file, 'py')
    )
    print('see result', x)


def _hex_2_rgb(hex_str: str) -> tuple[int, int, int]:
    return tuple(int(hex_str.removeprefix('#')[i:i + 2], 16) for i in (0, 2, 4))  # noqa


if __name__ == '__main__':
    # pox misc/compose_terminal_theme.py misc/catppuccin_macchiato.json
    cli.run(main)
