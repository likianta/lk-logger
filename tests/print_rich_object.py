import lk_logger

lk_logger.setup()

print(':r2', 'old -> new')
print(':r2', 'title: old -> new')
print(':v2ir2', 'title: old -> new')

print(
    ':r2',
    '''
    This is a **markdown** document.
    
    - item 1
    - item 2
    - item 3
    
    | Name    | Age | City      |
    |---------|-----|-----------|
    | Alice   | 18  | Shanghai  |
    | Bob     | 19  | Beijing   |
    | Charlie | 20  | Guangzhou |
    
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

print(':r2', {
    'Name': ('Alice', 'Bob', 'Charlie'),
    'Age' : (18, 19, 20),
    'City': ('Shanghai', 'Beijing', 'Guangzhou'),
})

print(':r2', (
    ('Name', 'Age', 'City'),
    ('Alice', 18, 'Shanghai'),
    ('Bob', 19, 'Beijing'),
    ('Charlie', 20, 'Guangzhou'),
))

# pox tests/print_rich_object.py
