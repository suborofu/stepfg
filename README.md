# stepfg: STEP File Generator

**Python 3.8+** | **Zero dependencies** | [MIT License](LICENSE.md)

Authors: E. Valetov and M. Berz
Organization: Michigan State University
Creation date: 03-Feb-2017

## Introduction

stepfg converts lists of 2D polygons (specified by vertices in the x-y plane)
into 3D STEP files (ISO 10303-242) by extruding the polygon interiors along
the z-axis. Pure Python, no external dependencies.

## Installation

```
pip install stepfg
```

Or from source:

```
git clone https://github.com/evvaletov/stepfg.git
cd stepfg
pip install -e .
```

## Library usage

```python
from stepfg import StepBuilder, generate_step

# Quick one-liner
content = generate_step(
    polygons=[[[0, 0], [1, 0], [1, 1], [0, 1]]],
    z_range=[0, 10],
    scale=1,
)

# Or use StepBuilder for more control
builder = StepBuilder('output.stp')
builder.generate_assembly(
    list_vert_list=[[[0, 0], [1, 0], [1, 1], [0, 1]]],
    geom_depth_list=[0, 10],
    p_coeff=1,
)
builder.to_file('output.stp')
```

## Command-line usage

```
stepfg [input_file [output_file]]
python -m stepfg [input_file [output_file]]
```

Run with the included sample geometry (a Muon g-2 quadrupole):

```
stepfg part_geometry.txt quadrupole.stp
```

## Input file format

Both Python literal and JSON formats are supported.

### Python literal (original format)

```python
[polygons, z_range, scale]
```

See `part_geometry.txt` for a full example (Muon g-2 quadrupole).

### JSON (object or array)

```json
{
  "polygons": [[[0, 0], [4, 0], [4, 4], [0, 4]]],
  "z_range": [0, 10],
  "scale": 1
}
```

The `scale` key is optional (defaults to 1). A JSON array `[polygons, z_range, scale]`
is also accepted. See `part_geometry.json` for a full example.

### Fields

- **polygons**: `[[vertex, ...], ...]` — each vertex is `[x, y]` or `[x, y, 0]`
- **z_range**: `[z1, z2]` — extrusion interval
- **scale**: proportionality coefficient (output is in mm; use 10 for cm input)

## Copyright Notice

© 2017 Eremey Valetov and Martin Berz
