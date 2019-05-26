import argparse

import vcd

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--root-folder', default=None)
    parser.add_argument('--nthreads', default=None, type=int)
    parser.add_argument('--no-killer', action='store_true')

    opt = parser.parse_args()
    vcd.start(root_folder=opt.root_folder, nthreads=opt.nthreads, no_killer=opt.no_killer)
