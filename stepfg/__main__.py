"""CLI entry point: python -m stepfg"""

import argparse
import ast
import json
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
    raw = input_path.read_text()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = ast.literal_eval(raw)

    if isinstance(data, dict):
        try:
            polygons = data['polygons']
            z_range = data['z_range']
            scale = data.get('scale', 1)
        except KeyError as e:
            print("[FAILED]")
            print(f"Error: JSON input missing required key {e}.", file=sys.stderr)
            sys.exit(1)
    elif isinstance(data, list) and len(data) == 3:
        polygons, z_range, scale = data
    else:
        print("[FAILED]")
        print("Error: input must be [polygons, z_range, scale] or a JSON object "
              "with 'polygons' and 'z_range' keys.", file=sys.stderr)
        sys.exit(1)
    print("[DONE]")

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
