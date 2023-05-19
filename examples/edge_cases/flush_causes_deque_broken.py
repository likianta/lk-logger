import lk_logger

lk_logger.setup(quiet=True)


def main() -> None:
    for i in range(1000):
        print(i)
    print(':f1', 'done')


if __name__ == '__main__':
    main()
