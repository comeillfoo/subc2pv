#!/usr/bin/env python3
import sys


def main():
    print('Hello, World')


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!')
        sys.exit(1)