"""Logs scanner"""

import os

from colorama import Fore, Style, init


# pylint: disable=missing-docstring

def main():
    init()
    filenames = [x for x in os.listdir('../') if x.endswith('.log')]

    errors = 0
    warnings = 0
    nlines = 0
    for file in filenames:
        file = os.path.join('../', file)
        with open(file, encoding='utf-8') as file_handler:
            try:
                lines = file_handler.read().splitlines()
            except UnicodeDecodeError as ex:
                print(Fore.LIGHTRED_EX + 'ERROR WITH LOG', file, ex)
                continue

        for line in lines:
            if 'ERROR' in line or 'CRITICAL' in line:
                print(Fore.LIGHTRED_EX + file, '- -', line)
                errors += 1
            if 'WARNING' in line:
                print(Fore.LIGHTYELLOW_EX + file, '- - ', line)
                warnings += 1
            nlines += 1

    print(Style.RESET_ALL, end='')
    if errors == 0 == warnings:
        print(Fore.LIGHTGREEN_EX + f'No errors ({nlines} lines)')
    else:
        print()
        if errors:
            print(Fore.LIGHTRED_EX + f'{errors} errors found ({nlines} lines)')
        if warnings:
            print(Fore.LIGHTYELLOW_EX + f'{warnings} warnings found ({nlines} lines)')


if __name__ == '__main__':
    main()
