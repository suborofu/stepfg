import pytest
from stepfg import StepBuilder


class TestStepBuilder:
    def test_square_extrusion(self):
        b = StepBuilder()
        square = [[[0, 0], [1, 0], [1, 1], [0, 1]]]
        b.generate_assembly(square, [0, 1])
        content = b.to_string()

        assert content.startswith("ISO-10303-21;\n")
        assert content.endswith("END-ISO-10303-21;\n")
        assert "CLOSED_SHELL" in content
        assert "MANIFOLD_SOLID_BREP" in content
        assert "ADVANCED_FACE" in content

    def test_entity_count(self):
        b = StepBuilder()
        square = [[[0, 0], [1, 0], [1, 1], [0, 1]]]
        b.generate_assembly(square, [0, 1])
        content = b.to_string()
        # Count ADVANCED_FACE entities: 4 sides + 2 caps = 6
        assert content.count("ADVANCED_FACE") == 6

    def test_scale_factor(self):
        b = StepBuilder()
        square = [[[0, 0], [1, 0], [1, 1], [0, 1]]]
        b.generate_assembly(square, [0, 5], p_coeff=10)
        content = b.to_string()
        # Vertices should be scaled: 10.0 instead of 1.0
        assert "10.0" in content

    def test_multi_polygon(self):
        b = StepBuilder()
        polys = [
            [[0, 0], [1, 0], [1, 1], [0, 1]],
            [[2, 0], [3, 0], [3, 1], [2, 1]],
        ]
        b.generate_assembly(polys, [0, 1])
        content = b.to_string()
        # Two closed shells → two manifold solid breps
        assert content.count("MANIFOLD_SOLID_BREP") == 2

    def test_to_file(self, tmp_path):
        b = StepBuilder()
        square = [[[0, 0], [1, 0], [1, 1], [0, 1]]]
        b.generate_assembly(square, [0, 1])
        out = tmp_path / "test.stp"
        b.to_file(str(out))
        assert out.exists()
        assert out.stat().st_size > 0
        assert out.read_text() == b.to_string()


class TestValidation:
    def test_zero_coeff(self):
        with pytest.raises(ValueError, match="Zero"):
            StepBuilder().generate_assembly([[[0, 0], [1, 0], [1, 1]]], [0, 1], 0)

    def test_nan_coeff(self):
        with pytest.raises(ValueError, match="NaN"):
            StepBuilder().generate_assembly([[[0, 0], [1, 0], [1, 1]]], [0, 1], "x")

    def test_equal_z(self):
        with pytest.raises(ValueError, match="different"):
            StepBuilder().generate_assembly([[[0, 0], [1, 0], [1, 1]]], [5, 5])

    def test_empty_polygons(self):
        with pytest.raises(ValueError):
            StepBuilder().generate_assembly([], [0, 1])
