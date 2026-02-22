"""CLI entry point: python -m stepfg"""

import argparse
import ast
import sys
from pathlib import Path

from . import __version__, generate_step


BANNER = """\
----------------------------------------------------
                STEP File Generator
              E. Valetov and M. Berz
             Michigan State University
                Created 03-Feb-2017
              Email: valetove@msu.edu
----------------------------------------------------"""


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog='stepfg',
        description='Convert 2D polygon geometry into 3D STEP files via extrusion.',
    )
    parser.add_argument('input', nargs='?', default='part_geometry.txt',
                        help='Input file containing 2D geometry data (default: part_geometry.txt)')
    parser.add_argument('output', nargs='?', default='part_out.stp',
                        help='Output STEP file (default: part_out.stp)')
    parser.add_argument('-V', '--version', action='version', version=f'stepfg {__version__}')

    args = parser.parse_args(argv)

    print(BANNER)

    input_path = Path(args.input)
    if not input_path.is_file():
        print(f"Error: input file '{args.input}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Reading 2D geometry file {args.input}... ", end="")
    data = ast.literal_eval(input_path.read_text())
    if not isinstance(data, list) or len(data) != 3:
        print("[FAILED]")
        print("Error: input must be a list of [polygons, z_range, scale].", file=sys.stderr)
        sys.exit(1)
    print("[DONE]")

    polygons, z_range, scale = data

    print("Generating assembly... ", end="")
    try:
        content = generate_step(polygons, z_range, scale, args.output)
    except ValueError as e:
        print("[FAILED]")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print("[DONE]")

    print(f"Writing STEP file {args.output}... ", end="")
    Path(args.output).write_text(content)
    print("[DONE]")


if __name__ == '__main__':
    main()
