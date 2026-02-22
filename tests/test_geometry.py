import math
import pytest
from stepfg._geometry import normalize, cross_product, convert_3d, convert_to_clockwise


class TestNormalize:
    def test_unit_vector(self):
        assert normalize([1, 0, 0]) == [1, 0, 0]

    def test_scales_to_unit(self):
        result = normalize([3, 4, 0])
        assert math.isclose(result[0], 0.6)
        assert math.isclose(result[1], 0.8)
        assert math.isclose(result[2], 0.0)

    def test_magnitude_one(self):
        result = normalize([1, 2, 3])
        mag = math.sqrt(sum(x ** 2 for x in result))
        assert math.isclose(mag, 1.0)

    def test_rejects_non_3d(self):
        with pytest.raises(ValueError):
            normalize([1, 2])


class TestCrossProduct:
    def test_x_cross_y(self):
        assert cross_product([1, 0, 0], [0, 1, 0]) == [0, 0, 1]

    def test_y_cross_x(self):
        assert cross_product([0, 1, 0], [1, 0, 0]) == [0, 0, -1]

    def test_parallel_is_zero(self):
        assert cross_product([1, 0, 0], [2, 0, 0]) == [0, 0, 0]


class TestConvert3d:
    def test_2d_to_3d(self):
        assert convert_3d([1, 2]) == [1, 2, 0]

    def test_3d_unchanged(self):
        assert convert_3d([1, 2, 3]) == [1, 2, 3]

    def test_non_numeric_unchanged(self):
        assert convert_3d([[1, 2], [3, 4]]) == [[1, 2], [3, 4]]


class TestConvertToClockwise:
    def test_ccw_square_reversed(self):
        ccw = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
        result = convert_to_clockwise(ccw)
        assert result == list(reversed(ccw))

    def test_cw_square_unchanged(self):
        cw = [[0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, 0]]
        result = convert_to_clockwise(cw)
        assert result == cw

    def test_degenerate_raises(self):
        with pytest.raises(ValueError):
            convert_to_clockwise([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
