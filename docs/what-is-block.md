# What Is Block

A Block is a "complete" code line or code block, it must contain an even number 
of paring symbols, no matter how many line breaks in it.

The following examples help you understand more quickly:

```
This isn't a block:
    print(a, b
    
This is a block:
    print(a, b)
    
This isn't a block:
    print(
        a,
        b
        
This is a block:
    print(
        a,
        b
    )
```

Our aim is receiving any number of text segs, remerge them and extract all 
complete blocks.
