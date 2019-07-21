import argparse

from core import start

if __name__ == '__main__':
    parser = argparse.ArgumentParser('vcd')

    parser.add_argument('--root-folder', default=None)

    opt = parser.parse_args()
    start(root_folder=opt.root_folder)
