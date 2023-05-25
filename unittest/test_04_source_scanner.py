import lk_logger
lk_logger.setup(show_varnames=True)


def test_code_include_linebreaks():
    a = 1
    b = 2
    
    print(1,
          2,
          3, )
    print({  # commnet A
        'c': 'cc',
        # comment B
        'd': 'dd',
    })
    print('''
        """
        xxx
        yyy
        \\\'
    ''')
    print(a, r'''
        """
        xxx
        yyy
        \\\'
        {}
    '''.format(b), b)
    
    print(
        'overview',
        (a, b),
        (b, a),
        a + b + a,
    )


def test_source_scanning():
    # test if comment crashes souce scanner.
    a, b = 1, 2
    print(a, b)  # this is a comment
    print(a, b)


if __name__ == '__main__':
    test_code_include_linebreaks()
    test_source_scanning()
