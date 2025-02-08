import os
os.chdir('misc/demo_code_for_readme_doc')

import lk_logger
lk_logger.setup()

print('hello world')

print(':d', 'divider line')

print('verbose', ':v')
print('info', ':v2')
print('success', ':v4')
print('warning', ':v6')
print('error', ':v8')

print('alpha', ':i')
print('beta', ':i')
print('gamma', ':i')

print(
    [
        {'name': 'Alpha', 'email': 'alpha@example.com'},
        {'name': 'Beta', 'email': 'beta@example.com'},
        {'name': 'Gamma', 'email': 'gamma@example.com'},
    ],
    ':l'
)

print('done', ':t')
