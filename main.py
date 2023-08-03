from bot.tradingviewbot import TradingViewBot
import os
import sys
import argparse
from typing import AnyStr, Sequence, Literal


def find_file(path: AnyStr) -> Literal[True, False]:
    try:
        if not os.path.exists(path):
            sys.stderr.write(f'File "{path}" not found')
            return False
        return True
    except TypeError as e:
        sys.stderr.write(f'Invalid path format: {path}')
        return False


def get_lines(path: AnyStr) -> Sequence[AnyStr]:
    with open(path, 'r') as file:
        lines = [line.strip() for line in file.readlines()]
    return lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--links')
    parser.add_argument('-c', '--comments')
    parser.add_argument('--logs')
    args = parser.parse_args()

    if not (find_file(args.links) and find_file(args.comments)):
        sys.exit()

    if args.logs:
        if not os.path.isfile(args.logs):
            sys.stderr.write(f'Invalid path format: {args.logs}')
            sys.exit()

    links = get_lines(args.links)
    comments = get_lines(args.comments)

    print('Running over URLs...')
    bot = TradingViewBot(links, comments, args.logs)
    bot.run()

