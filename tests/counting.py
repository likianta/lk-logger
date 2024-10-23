import lk_logger

lk_logger.setup(show_source=False, show_funcname=False)


def simple_counting() -> None:
    print(':i', 'monday')
    print(':i', 'tuesday')
    print(':i', 'wednesday')


def classic_scoped_counting() -> None:
    print(':d', 'classic scoped counting')
    for _ in range(3):
        print(':i2r', _create_text('aaa'))
        for _ in range(3):
            print(':i2r', _create_text('bbb', 4))
            for _ in range(3):
                print(':i2r', _create_text('ccc', 8))
                _another_for_loop(_create_text('ddd', 12))


def complicated_scoped_counting() -> None:
    print(':d', 'complicated scoped counting')
    
    for _ in range(3):
        print(':i2r', _create_text('aaa'))
    
    def closure(text: str) -> None:
        for _ in range(3):
            print(':i2pr', text)
    
    for _ in range(3):
        print(':i2r', _create_text('bbb'))
        for _ in range(3):
            print(':i2r', _create_text('ccc', 4))
            closure(_create_text('ddd', 8))
        _another_for_loop(_create_text('eee', 4))
    
    for _ in range(3):
        print(':i2r', _create_text('fff'))
        closure(_create_text('ggg', 4))
        _another_for_loop(_create_text('hhh', 4))


def _create_text(text: str, indent: int = 0) -> str:
    # return ' ' * indent + text
    if indent:
        return '[dim]{}[/] {}'.format('-' * indent, text)
    else:
        return text


def _another_for_loop(text: str) -> None:
    for _ in range(3):
        print(':i2pr', text)


if __name__ == '__main__':
    simple_counting()
    classic_scoped_counting()
    complicated_scoped_counting()
