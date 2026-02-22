"""stepfg — convert 2D polygon cross-sections to 3D STEP files via extrusion."""

__version__ = "2.0.0"

from ._builder import StepBuilder
from ._geometry import normalize, cross_product, convert_3d, convert_to_clockwise


def generate_step(polygons, z_range, scale=1, filename='part_out.stp'):
    """Generate STEP content from polygon cross-sections.

    Args:
        polygons: List of polygons, each a list of [x,y] or [x,y,z] vertices.
        z_range: [z1, z2] extrusion interval.
        scale: Proportionality coefficient (default 1). Use 10 for cm→mm.
        filename: Filename embedded in the STEP header.

    Returns:
        STEP file content as a string.
    """
    builder = StepBuilder(filename)
    builder.generate_assembly(polygons, z_range, scale)
    return builder.to_string()
