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
VARIABLE_NAME = 0  # varname
QUOTED_STRING = 1  # qstring
SIMPLE_NUMBER = 2
NESTED_STRUCT = 3

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
