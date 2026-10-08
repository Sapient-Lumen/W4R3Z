from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    print('rev0489 is an already-applied archive revision; files are present in-place.')
    print('No transformation is required when this continuation bundle is opened directly.')


if __name__ == '__main__':
    main()
