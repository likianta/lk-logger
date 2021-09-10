# TOKENS
TOKEN_A00 = 0x000  # ( <==> )
TOKEN_B00 = 0x001  # ' <==> ' | " <==> " | ''' <==> ''' | """ <==> """
TOKEN_B10 = 0x011  # ' <==> ' | " <==> "
TOKEN_B20 = 0x012  # ''' <==> ''' | """ <==> """
TOKEN_B21 = 0x121  # '''?? | """?? (safe period)
TOKEN_B22 = 0x122  # '''xx | """xx (ridden off safe period)
TOKEN_C00 = 0x003  # \ <==> *
TOKEN_D00 = 0x004  # # <==> ***

# RETURN CODE
INIT = 0
SUBMITTABLE = 1
CONTINUE = 2
BREAK_OUT = 3
UNREACHABLE_CASE = 4

# scanner.py > func:get_variables
VARIABLE_NAME = 0  # varname. e.g. 'a', 'b', 'c'
SUBSCRIPTABLE = 1  # varname with '(' or '[' or '{'. e.g. 'requests.get(...)'
QUOTED_STRING = 2  # qstring. e.g. '"hello world"'
SIMPLE_NUMBER = 3  # simple int or float. e.g. 1, 2, 3, 1.0, 2.0, 3.0, and
#   negative number. but not support 1E10, 1., 2., 3., (they are treated as
#   VARIABLE_NAME)
NESTED_STRUCT = 4  # starts with '(' or '[' or '{'

# PAIRED SYMBOLS
PAIRED_SYMBOLS = {
    '(' : (')', TOKEN_A00),
    '[' : (']', TOKEN_A00),
    '{' : ('}', TOKEN_A00),
    '"' : ('"', TOKEN_B00),
    "'" : ("'", TOKEN_B00),
    '\\': ('*', TOKEN_C00),
    '#' : ('*', TOKEN_D00),
}
