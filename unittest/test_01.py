import lk_logger
lk_logger.setup(show_varnames=True)


def test_source_scanner():
    # test if comment crashes souce scanner.
    a, b = 1, 2
    print(a, b)  # this is a comment
    print(a, b)


def test_backslash_brackets():
    # test backslash brackets (`\\[` and `\[`) behaviors.
    print(':i', 'hello [world] ---')  # 1 -> r'hello [world] ---'
    # what if it is a color mark.
    print(':i', 'hello [red] ---')  # 2 -> r'hello [red] ---'
    
    print(':i', 'hello \\[world]')  # 3 -> r'hello \[world]'
    print(':i', 'hello \\["world"]')  # 4 -> r'hello \["world"]'
    print(':i', 'hello \\[\\[world]')  # 5 -> r'hello \[\[world]'
    print(':i', 'hello \\[\\["world"]')  # 6 -> r'hello \[\["world"]'
    print(':i', 'hello \\world]')  # 7 -> r'hello \world]'
    print(':i', 'hello [world(]')  # 8 -> r'hello [world(]'
    print(':i', 'hello [world()]')  # 9 -> r'hello [world()]'
    print(':i', 'hello [world(a:b)]')  # 10 -> r'hello [world(a:b)]'
    
    x = {'a': 'aaa'}
    print(':i0', x['a'])  # 1 -> "x['a'] = aaa"


if __name__ == '__main__':
    import pytest
    pytest.main()
