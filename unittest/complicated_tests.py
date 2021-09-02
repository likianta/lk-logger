from lk_logger import lk


def lambda_occurances():
    lk.loga(lambda *args, **kwargs: (len(args), len(kwargs)))
    lk.loga((lambda *args, **kwargs: (len(args), len(kwargs)))(1, 2, a=3))


if __name__ == '__main__':
    lambda_occurances()
