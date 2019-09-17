import argparse
from enum import Enum

from vcm.core.options import Options
from vcm.downloader import download
from vcm.notifier import notify


class Command(Enum):
    notify = 1
    download = 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-sc', '--show-config', action='store_true')

    subparsers = parser.add_subparsers(title='commands', dest='command')

    downloader_parser = subparsers.add_parser('download')
    downloader_parser.add_argument('--nthreads', default=20, type=int)
    downloader_parser.add_argument('--no-killer', action='store_true')
    downloader_parser.add_argument('-d', '--debug', action='store_true')

    notifier_parser = subparsers.add_parser('notify')
    notifier_parser.add_argument('--nthreads', default=20, type=int)
    notifier_parser.add_argument('--no-icons', action='store_true')

    opt = parser.parse_args()

    if opt.show_config:
        data = ['root_folder', 'logs_folder', 'logging_level', 'database_path', 'config_path',
                'credentials_path', 'use_base64_icons']
        data.sort()

        template = '%%-%ds: %%s' % (max([len(x) for x in data]) + 1)

        def get_info(x):
            return x.replace('_', ' ').strip().capitalize(), getattr(Options, x.upper())

        message = '\n'.join([template % get_info(x) for x in data])
        exit(message)

    try:
        opt.command = Command(opt.command)
    except ValueError:
        try:
            opt.command = Command[opt.command]
        except KeyError:
            return parser.error('Invalid use: use download or notify')

    if opt.command == Command.download:
        if opt.debug:
            import webbrowser

            chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
            webbrowser.get(chrome_path).open_new('localhost')

        return download(nthreads=opt.nthreads, no_killer=opt.no_killer)

    elif opt.command == Command.notify:
        return notify(['sralloza@gmail.com'], not opt.no_icons, nthreads=opt.nthreads)
    else:
        return parser.error('Invalid command: %r' % opt.command)
