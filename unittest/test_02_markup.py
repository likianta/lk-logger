import lk_logger
lk_logger.setup(show_varnames=True)


def test_loose_format():
    print(a := {
        'a': {
            'aa': {
                'aaa': 100,
            },
            'bb': [
                200, 300, {400, 500, 600},
                {700: 7000, 800: 8000},
            ]
        }
    }, ':l')
    
    print(a,
          b := [True, False, 0, 1],
          {'aaa', 'bbb', 'ccc', (
              'ddd', 'eee', 'fff',
          )}, b, ':l')
    
    print({True, False,
           str({
               'k': 'kkk',
               'v': 'vvv',
           })}, ':l')
