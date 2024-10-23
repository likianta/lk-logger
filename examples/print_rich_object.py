import lk_logger

lk_logger.setup(quiet=True, show_source=False)

print(
    ':r2',
    '''
    - alpha
    - beta
    - gamma
    
    ```javascript
    console.log('hello world')
    ```
    
    ```html
    <div>hello world</div>
    ```
    
    ```python
    print('hello world')
    ```
    '''
)

print(
    ':r2',
    'version changed: 0.1.0 -> 0.2.0'
)
