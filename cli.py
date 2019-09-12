import argparse

from vcd import start
from vcd._requests import Connection

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--root-folder', default=None)
    parser.add_argument('--nthreads', default=None, type=int)
    parser.add_argument('--no-killer', action='store_true')
    parser.add_argument('-d', '--debug', action='store_true')

    opt = parser.parse_args()

    if opt.debug:
        import webbrowser

        chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
        webbrowser.get(chrome_path).open_new('localhost')

    start(root_folder=opt.root_folder, nthreads=opt.nthreads, no_killer=opt.no_killer)
