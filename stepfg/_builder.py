import operator
import re
from numbers import Number

from ._geometry import normalize, cross_product, rotate, convert_3d, convert_to_clockwise
from ._template import step_header


def _line_index(line):
    m = re.search(r'#(.+?)=', line)
    return 0 if m is None else int(m.group(1))


def _to_coord(clist):
    if len(clist) != 3:
        raise ValueError("to_coord: coordinates must be 3D")
    return str(clist[0]) + ',' + str(clist[1]) + ',' + str(clist[2])


def _to_step_list(slist):
    if not isinstance(slist, list):
        return '#' + str(slist)
    return ','.join('#' + str(s) for s in slist)


def _fort_bool(bool_in):
    return '.T.' if (bool_in is True) or (bool_in == '.T.') else '.F.'


class StepBuilder:
    def __init__(self, filename='part_out.stp'):
        self._filename = filename
        self._file_array, self._index1, highest = step_header(filename)
        self._current_index = highest + 1
        self._work_array = []
        self._part_body_index = 1

    def _item_exists(self, string_in):
        if not self._work_array:
            return False
        return any(item.endswith(string_in) for item in self._work_array)

    def _existing_item_ln(self, string_in):
        if not self._work_array or not self._item_exists(string_in):
            return False
        match = next(item for item in self._work_array if item.endswith(string_in))
        return _line_index(match)

    def new_item(self, string_in):
        if self._item_exists(string_in):
            return self._existing_item_ln(string_in)
        self._work_array.append('#' + str(self._current_index) + '=' + string_in)
        idx = self._current_index
        self._current_index += 1
        return idx

    def point(self, coord_in):
        return self.new_item(
            "CARTESIAN_POINT('',(" + _to_coord(coord_in) + ")) ;\n")

    def line(self, origin, direction):
        coord_ln = self.new_item(
            "CARTESIAN_POINT('Origin Line',(" + _to_coord(origin) + ")) ;\n")
        dir_ln = self.new_item(
            "DIRECTION('Vector Direction',("
            + _to_coord(normalize(direction)) + ")) ;\n")
        vec_ln = self.new_item(
            "VECTOR('Line Direction',#" + str(dir_ln) + ",1.) ;\n")
        return self.new_item(
            "LINE('Line',#" + str(coord_ln) + ",#" + str(vec_ln) + ") ;\n")

    def vertex(self, coord_in):
        coord_ln = self.new_item(
            "CARTESIAN_POINT('Vertex',(" + _to_coord(coord_in) + ")) ;\n")
        return self.new_item("VERTEX_POINT('',#" + str(coord_ln) + ") ;\n")

    def edge_curve(self, vertex1_ln, vertex2_ln, line_coord_ln, same_sense=True):
        return self.new_item(
            "EDGE_CURVE('',#" + str(vertex1_ln) + ",#" + str(vertex2_ln)
            + ",#" + str(line_coord_ln) + "," + _fort_bool(same_sense) + ") ;\n")

    def _edge_curve_0(self, v1, v2, same_sense=True):
        return self.edge_curve(
            self.vertex(v1), self.vertex(v2),
            self.line(
                [x / 2 for x in list(map(operator.add, v1, v2))],
                list(map(operator.sub, v2, v1))),
            _fort_bool(same_sense))

    def oriented_edge(self, edge_curve_ln, same_sense=True):
        return self.new_item(
            "ORIENTED_EDGE('',*,*,#" + str(edge_curve_ln) + ","
            + _fort_bool(same_sense) + ") ;\n")

    def edge_loop(self, lines):
        return self.new_item(
            "EDGE_LOOP('',(" + _to_step_list(lines) + ")) ;\n")

    def _edge_loop_0(self, vertices):
        return self.edge_loop([
            self.oriented_edge(self._edge_curve_0(x1, x2))
            for x1, x2 in zip(vertices, rotate(vertices, -1))
        ])

    def face_outer_bound(self, edge_loop_ln, same_sense=True):
        return self.new_item(
            "FACE_OUTER_BOUND('',#" + str(edge_loop_ln) + ","
            + _fort_bool(same_sense) + ") ;\n")

    def _edge_loop_1(self, vertices, same_sense=True):
        return self.face_outer_bound(self._edge_loop_0(vertices), same_sense)

    def _axis2_placement_3d(self, origin_coord, direction1, direction2):
        origin_ln = self.new_item(
            "CARTESIAN_POINT('Axis2P3D Location',("
            + _to_coord(origin_coord) + ")) ;\n")
        d1_ln = self.new_item(
            "DIRECTION('Axis2P3D ZDirection',("
            + _to_coord(direction1) + ")) ;\n")
        d2_ln = self.new_item(
            "DIRECTION('Axis2P3D XDirection',("
            + _to_coord(direction2) + ")) ;\n")
        return self.new_item(
            "AXIS2_PLACEMENT_3D('Plane Axis2P3D',#" + str(origin_ln)
            + ",#" + str(d1_ln) + ",#" + str(d2_ln) + ") ;\n")

    def plane(self, axis2_placement_3d_ln):
        return self.new_item(
            "PLANE('',#" + str(axis2_placement_3d_ln) + ") ;\n")

    def advanced_face(self, face_outer_bound_ln, plane_ln, same_sense_plane=True):
        return self.new_item(
            "ADVANCED_FACE('PartBody',(" + _to_step_list(face_outer_bound_ln)
            + "),#" + str(plane_ln) + "," + _fort_bool(same_sense_plane) + ") ;\n")

    def _advanced_face_0(self, vertices, zaxis, same_sense_1=True, same_sense_2=True):
        cp = cross_product(
            list(map(operator.sub, vertices[2], vertices[1])),
            list(map(operator.sub, vertices[2], vertices[0])))
        if list(map(operator.add, normalize(zaxis), normalize(cp))) == [0, 0, 0]:
            return self.advanced_face(
                self._edge_loop_1(vertices, same_sense_1),
                self.plane(self._axis2_placement_3d(
                    vertices[0], normalize(zaxis),
                    normalize(list(map(operator.sub, vertices[1], vertices[0]))))),
                same_sense_2)
        else:
            rev = list(reversed(vertices))
            return self.advanced_face(
                self._edge_loop_1(rev, same_sense_1),
                self.plane(self._axis2_placement_3d(
                    vertices[0], normalize(zaxis),
                    normalize(list(map(operator.sub, rev[1], rev[0]))))),
                same_sense_2)

    def closed_shell(self, advanced_face_ln_list):
        return self.new_item(
            "CLOSED_SHELL('Closed Shell',("
            + _to_step_list(advanced_face_ln_list) + ")) ;\n")

    def manifold_solid_brep(self, closed_shell_ln):
        msb = self.new_item(
            "MANIFOLD_SOLID_BREP('PartBody." + str(self._part_body_index)
            + "',#" + str(closed_shell_ln) + ") ;\n")
        self._part_body_index += 1
        return msb

    def _advanced_brep_shape_representation(self, msb_list, init_ln=45):
        return self.new_item(
            "ADVANCED_BREP_SHAPE_REPRESENTATION('NONE',("
            + _to_step_list(msb_list) + "),#" + str(init_ln) + ") ;\n")

    def _shape_representation_relationship(self, absr_ln, sr_ln=48):
        return self.new_item(
            "SHAPE_REPRESENTATION_RELATIONSHIP(' ',' ',#" + str(sr_ln)
            + ",#" + str(absr_ln) + ") ;\n")

    def zface(self, vertex1, vertex2, geom_depth_list):
        z_neg, z_pos = geom_depth_list
        return self._advanced_face_0(
            [list(map(operator.add, vertex1, [0, 0, z_neg])),
             list(map(operator.add, vertex2, [0, 0, z_neg])),
             list(map(operator.add, vertex2, [0, 0, z_pos])),
             list(map(operator.add, vertex1, [0, 0, z_pos]))],
            normalize(cross_product(
                list(map(operator.sub, vertex2, vertex1)),
                [0, 0, -(z_pos - z_neg)])))

    def xyface(self, vertex_list, depth, zdir):
        return self._advanced_face_0(
            [list(map(operator.add, x, [0, 0, depth])) for x in vertex_list],
            zdir)

    def af2d3d(self, vertex_list, geom_depth_list):
        z_neg, z_pos = geom_depth_list
        faces = [
            self.xyface(vertex_list, z_pos, [0, 0, 1]),
            self.xyface(vertex_list, z_neg, [0, 0, -1]),
        ]
        faces += [
            self.zface(x1, x2, geom_depth_list)
            for x1, x2 in zip(vertex_list, rotate(vertex_list, -1))
        ]
        return faces

    def generate_part(self, vert_list, geom_depth):
        return self.manifold_solid_brep(
            self.closed_shell(self.af2d3d(vert_list, geom_depth)))

    def generate_assembly(self, list_vert_list, geom_depth_list, p_coeff=1):
        if not isinstance(p_coeff, Number):
            raise ValueError("NaN supplied for proportionality coefficient")
        if p_coeff == 0:
            raise ValueError("Zero supplied as the proportionality coefficient")
        if not isinstance(geom_depth_list, list) or len(geom_depth_list) != 2:
            raise ValueError("z-coordinate interval [z1, z2] expected")
        for d in geom_depth_list:
            if not isinstance(d, Number):
                raise ValueError("NaN found in the z-coordinate interval")
        if geom_depth_list[0] == geom_depth_list[1]:
            raise ValueError("z2 must be different from z1")
        if geom_depth_list[0] > geom_depth_list[1]:
            geom_depth_list = [geom_depth_list[1], geom_depth_list[0]]
        if not isinstance(list_vert_list, list) or not list_vert_list:
            raise ValueError("Non-empty list of vertex lists expected")
        for part in list_vert_list:
            if not isinstance(part, list) or not part:
                raise ValueError("Non-empty list of vertices expected")
            for v in part:
                if not isinstance(v, list) or not v:
                    raise ValueError("Non-empty vertex coordinate list expected")
                if len(v) < 2 or len(v) > 3:
                    raise ValueError(
                        f"Vertex must have 2 or 3 coordinates, got {len(v)}")
                for c in v:
                    if not isinstance(c, Number):
                        raise ValueError("NaN supplied for a vertex coordinate")

        list_vert_list = [
            [convert_3d(v) for v in part] for part in list_vert_list
        ]
        list_vert_list = [convert_to_clockwise(x) for x in list_vert_list]
        list_vert_list = [
            [[p_coeff * 1.0 * c for c in v] for v in part]
            for part in list_vert_list
        ]
        geom_depth_list = [p_coeff * 1.0 * i for i in geom_depth_list]

        part_list = [self.generate_part(x, geom_depth_list) for x in list_vert_list]
        self._shape_representation_relationship(
            self._advanced_brep_shape_representation(part_list))

    def to_string(self):
        result = (self._file_array[:self._index1]
                  + self._work_array
                  + self._file_array[self._index1 + 1:])
        return ''.join(result)

    def to_file(self, path):
        with open(path, 'w') as f:
            f.write(self.to_string())
