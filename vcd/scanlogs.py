"""Logs scanner"""

import os

from colorama import Fore, Style


# pylint: disable=missing-docstring

def main():
    filenames = [x for x in os.listdir('./') if x.endswith('.log')]

    errors = 0
    warnings = 0
    nlines = 0
    for file in filenames:
        with open(file, encoding='utf-8') as file_handler:
            try:
                lines = file_handler.read().splitlines()
            except UnicodeDecodeError as ex:
                print(Fore.RED + 'ERROR WITH LOG', file, ex)
                continue

        for line in lines:
            if 'ERROR' in line or 'CRITICAL' in line:
                print(Fore.RED + file, '- -', line)
                errors += 1
            if 'WARNING' in line:
                print(Fore.LIGHTYELLOW_EX + file, '- - ', line)
                warnings += 1
            nlines += 1

    print(Style.RESET_ALL, end='')
    if errors == 0 == warnings:
        print(Fore.GREEN + f'No errors ({nlines} lines)')
    else:
        print()
        if errors:
            print(Fore.RED + f'{errors} errors found ({nlines} lines)')
        if warnings:
            print(Fore.LIGHTYELLOW_EX + f'{warnings} warnings found ({nlines} lines)')


if __name__ == '__main__':
    main()
