import hashlib
import os
import pickle


def get_content_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


def get_file_hash(path: str) -> str:
    """
    if file is too big, read the first 8192 bytes.
    https://blog.csdn.net/qq_26373925/article/details/115409308
    """
    file = open(path, 'rb')
    md5 = hashlib.md5()
    if os.path.getsize(path) > 3 * 1024 * 1024:
        md5.update(file.read(8192))
    else:
        md5.update(file.read())
    file.close()
    return md5.hexdigest()


def pickle_load(file: str) -> dict:
    with open(file, 'rb') as f:
        return pickle.load(f)


def pickle_dump(obj: dict, file: str):
    with open(file, 'wb') as f:
        pickle.dump(obj, f)
