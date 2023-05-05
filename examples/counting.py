import lk_logger

lk_logger.setup()


def simple_counting() -> None:
    print(':i', 'monday')
    print(':i', 'tuesday')
    print(':i', 'wednesday')


def scoped_counting() -> None:
    
    def create_text(text: str, indent: int = 0) -> str:
        return '\t' + ' ' * indent + text
    
    for _ in range(3):
        print(':i2', create_text('aaa'))
    
    def closure(text: str) -> None:
        for _ in range(3):
            print(':i2p', text)
    
    for _ in range(3):
        print(':i2', create_text('bbb'))
        for _ in range(3):
            print(':i2', create_text('ccc', 4))
            closure(create_text('ddd', 8))
        _sibling(create_text('eee', 4))
        
    for _ in range(3):
        print(':i2', create_text('fff'))
        closure(create_text('ggg', 4))
        _sibling(create_text('hhh', 4))


def _sibling(text: str) -> None:
    for _ in range(3):
        print(':i2p', text)


if __name__ == '__main__':
    simple_counting()
    scoped_counting()
