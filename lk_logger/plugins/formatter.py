"""
Abbreviations:
    bak     backup
    fmt     format, formatify
    tmp     template
"""
import re


# class Formatter:
#
#     def __init__(self, count, total_count):


def fmt_count(count, total_count,
              template='[{i}/{j}]', backup_template='[{i}]'):
    """
    Args:
        count
        total_count
        template:
            optional keys:
                key     example     note
                i       12
                I       012      <- j=100
                        001,112  <- j=0
                I1, I2, I3, ...
                        0012     <- I4
                j       100
                p       1.00%    <- i=1, j=100
                p.0, p.1, p.2, ...
                        1.0000%  <- p.4
                P       01.00%   <- i=1, j=100
                P.0, P.1, P.2, ...
                        01.000%  <- P.3
        backup_template:
            if total count is zero, will use this.

    References:
        https://www.runoob.com/python/att-string-format.html
    """
    
    data = {}
    i, j = count, total_count
    p = i / j if j else ''
    template = template if j else backup_template
    
    for x in _parse_template(template):
        if x == 'i':
            data[x] = i
        elif x == 'I':
            if j:
                data[x] = '{{:0>{}}}'.format(len(str(j))).format(i)
            else:
                dynamic_width = 3
                i_width = len(str(i))
                while dynamic_width < i_width:
                    dynamic_width += 3
                data[x] = '0' * (dynamic_width - i_width) + ':,'.format(i)
        elif x.startswith('I'):
            data[x] = '{{:0>{}}}'.format(int(x[1:])).format(i)
        elif x == 'j' and j:
            data[x] = j
        elif x == 'p' and p:
            data[x] = '{:.2%}'.format(p)
        elif x.startswith('p.') and p:
            if x == 'p.0':
                data[x] = '{}%'.format(round(p))
            else:
                data[x] = '{{:.{}%}}'.format(int(x[2:])).format(p)
        elif x == 'P' and p:
            if p < 10:
                data[x] = '0' + '{:.2%}'.format(p)
            else:
                data[x] = '{:.2%}'.format(p)
        elif x.startswith('P.') and p:
            if p < 10:
                data[x] = '0' + '{{:.{}%}}'.format(int(x[2:])).format(p)
            else:
                data[x] = '{{:.{}%}}'.format(int(x[2:])).format(p)
        else:
            data[x] = ''
            # raise ValueError(x, template)
    
    return template.format(**data)


def fmt_tag(template='[{t}]'):
    pass


def _parse_template(template) -> set[str]:
    slot = re.compile(r'(?<={)[^}]+')
    return set(slot.findall(template))
