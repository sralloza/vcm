import argparse

from vcm.downloader import download
from vcm.notifier import notify


def main():
    # TODO - Test, I don't think it works as it is supposed to
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')

    downloader_parser = subparsers.add_parser('download')
    downloader_parser.add_argument('--nthreads', default=20, type=int)
    downloader_parser.add_argument('--no-killer', action='store_true')
    downloader_parser.add_argument('-d', '--debug', action='store_true')

    notifier_parser = subparsers.add_parser('notify')
    notifier_parser.add_argument('--nthreads', default=20, type=int)
    notifier_parser.add_argument('--no-icons', action='store_true')

    opt = parser.parse_args()

    if opt.command is None:
        return parser.error('Invalid use: use download or notify')

    elif opt.command == 'download':

        if opt.debug:
            import webbrowser

            chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
            webbrowser.get(chrome_path).open_new('localhost')

        return download(nthreads=opt.nthreads, no_killer=opt.no_killer)

    elif opt.command == 'notify':
        return notify('sralloza@gmail.com', not opt.no_icons, nthreads=opt.nthreads)
    else:
        return parser.error('Invalid command: %r' % opt.command)
