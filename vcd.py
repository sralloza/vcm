import argparse

import vcd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--root-folder', default=None)

    opt = parser.parse_args()
    vcd.start(root_folder=opt.root_folder)
