#!/usr/bin/env python3
import sys
import argparse
import pathlib
from typing import Optional

from SubC2PV import SubC2PV


def args_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser('subc2pv')

    # Options:
    p.add_argument('-o', '--output', type=pathlib.Path, metavar='MODEL',
                   help='Path to output file, default ${input_path/.c/.pv}')

    p.add_argument('-l', '--lut', type=pathlib.Path, metavar='LUT',
                   help='Path to look-up-table, default ${input_path/.c/.lut}')

    # Arguments:
    p.add_argument('file', metavar='IMPL', type=pathlib.Path,
                   help='Path to implementation')
    return p


def path_or_default(path: Optional[pathlib.Path], default: str) -> pathlib.Path:
    return path if path is not None else pathlib.Path(default)


def main() -> int:
    args = args_parser().parse_args()

    infile: pathlib.Path = args.file
    basename: str = str(infile).removesuffix('.c')
    outfile: pathlib.Path = path_or_default(args.output, basename + '.pv')
    lut: pathlib.Path = path_or_default(args.lut, basename + '.lut')

    subc2pv = SubC2PV.from_path(infile, lut)
    subc2pv.extract_to_path(outfile)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print('Aborted!')
        sys.exit(1)