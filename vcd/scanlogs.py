"""Logs scanner"""

import os

from colorama import Fore, Style, init


# pylint: disable=missing-docstring

def scanlogs():
    init()
    filenames = [x for x in os.listdir('../logs') if x.endswith('.log')]

    errors = 0
    warnings = 0
    nlines = 0
    for file in filenames:
        file = os.path.join('../logs', file)
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


def detect_guilty(nthreads=30):
    print(Style.RESET_ALL)

    with open('../logs/vcd.log', encoding='utf-8') as fh:
        content = fh.read().splitlines()

    for n in range(nthreads):
        name = f'W-{n + 1:02d}'
        name_plus_dot = name + '.'
        thread_lines = [x for x in content if name_plus_dot in x]
        if 'ready to continue working' not in thread_lines[-1]:
            print(f'GUILTY :: {name} :: {thread_lines[-1]}')


if __name__ == '__main__':
    scanlogs()
    detect_guilty()
