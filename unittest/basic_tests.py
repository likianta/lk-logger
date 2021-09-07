from lk_logger import lk
# from lk_logger_3_6 import lk

# lk.enable_lite_mode()


def print_values():
    lk.loga(1)
    lk.loga(1, 2, 3)
    lk.loga(1, 2, 3, True)
    lk.loga(1, 2, 3, True, [])
    lk.loga(1, 2, 3, True, {})
    lk.loga(1, 2, 3, True, {'a': 'aa'})


def print_values_with_varnames():
    a = 1
    b = 2
    c = 'c'
    d = 'd'
    
    lk.loga(a)
    lk.loga(a, b, c)
    lk.loga(a, b, a + b)
    lk.loga(a, b, e := (a + b), e)
    lk.loga({a: b, c: d})


def print_with_linebreaks():
    a = 1
    b = 2
    
    lk.loga(1,
            2,
            3, )
    lk.loga({
        'a': 'aa',
        'b': 'bb',
    })
    lk.loga({  # commnet A
        'c': 'cc',
        # comment B
        'd': 'dd',
    })
    lk.loga('''
        """
        xxx
        yyy
        \\\'
    ''')
    lk.loga(a, r'''
        """
        xxx
        yyy
        \\\'
        {}
    '''.format(b), b)


def print_with_countings():
    a = [1, 2, 3]
    b = [1, 2, 3, 4, 5, 6]
    
    with lk.counting(a):
        for i in a:
            lk.logax(i)
            
    with lk.counting(a):
        for i in a:
            lk.logax(i)
            
        with lk.counting(b):
            for j in b:
                lk.logax(j)

        for i in a:
            lk.logax(i)

    with lk.counting(a):
        for i in a:
            with lk.counting(b):
                for j in b:
                    lk.logax(i, j)
                    

def pretty_print():
    lk.logp(a := {
        'a': {
            'aa': {
                'aaa': 100,
            },
            'bb': [
                200, 300, {400, 500, 600},
                {700: 7000, 800: 8000},
            ]
        }
    })
    lk.logp(a,
            b := [True, False, 0, 1],
            {'aaa', 'bbb', 'ccc', (
                'ddd', 'eee', 'fff',
            )}, b)
  
                    
def other():
    lk.loga(lk.position)


def main():
    print_values()
    print_values_with_varnames()
    print_with_linebreaks()
    print_with_countings()
    pretty_print()
    other()
    
    
if __name__ == '__main__':
    main()
    # print_values()
    # print_values_with_varnames()
    # print_with_linebreaks()
    # print_with_countings()
    # pretty_print()
    # other()
