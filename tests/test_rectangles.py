"""Comprehensive tests for RectangleAnalyzer.

Categories:
- Validation cases    : malformed or invalid input
- Normal cases        : typical multi-rectangle scenarios from the task
- Boundary cases      : rectangles touching edges but not overlapping
- Edge (input) cases  : empty list, single rect, zero dimensions, negatives
- Stress cases        : many rectangles, large coordinates
"""

import math
import time
import pytest

from rectangle_analyzer.analyzer import RectangleAnalyzer


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_analyzer(*rects: dict) -> RectangleAnalyzer:
    return RectangleAnalyzer(list(rects))


def rect(x, y, w, h) -> dict:
    return {"x": x, "y": y, "width": w, "height": h}


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION CASES
# ─────────────────────────────────────────────────────────────────────────────


class TestValidation:
    """Input validation — malformed or invalid data must raise immediately."""

    def test_not_a_list_raises(self):
        with pytest.raises(TypeError, match="must be a list"):
            RectangleAnalyzer({"x": 0, "y": 0, "width": 1, "height": 1})

    def test_item_not_a_dict_raises(self):
        with pytest.raises(TypeError, match="must be a dict"):
            RectangleAnalyzer([(0, 0, 1, 1)])

    def test_missing_key_raises(self):
        with pytest.raises(KeyError, match="missing required keys"):
            RectangleAnalyzer([{"x": 0, "y": 0, "width": 1}])  # no height

    def test_non_numeric_value_raises(self):
        with pytest.raises(TypeError, match="must be a number"):
            RectangleAnalyzer([{"x": "0", "y": 0, "width": 1, "height": 1}])

    def test_bool_value_raises(self):
        # bool is a subclass of int — must be rejected explicitly
        with pytest.raises(TypeError, match="must be a number"):
            RectangleAnalyzer([{"x": True, "y": 0, "width": 1, "height": 1}])

    def test_none_value_raises(self):
        with pytest.raises(TypeError, match="must be a number"):
            RectangleAnalyzer([{"x": None, "y": 0, "width": 1, "height": 1}])

    def test_extra_keys_are_allowed(self):
        # Extra keys should not cause errors
        a = RectangleAnalyzer([{"x": 0, "y": 0, "width": 2, "height": 2, "label": "A"}])
        assert math.isclose(a.calculate_coverage_area(), 4.0)

    def test_error_reports_correct_index(self):
        with pytest.raises(KeyError, match=r"rectangles\[1\]"):
            RectangleAnalyzer([
                {"x": 0, "y": 0, "width": 1, "height": 1},
                {"x": 0, "y": 0, "width": 1},           # bad rect at index 1
            ])


# ─────────────────────────────────────────────────────────────────────────────
# NORMAL CASES
# ─────────────────────────────────────────────────────────────────────────────


class TestNormalCases:
    """Examples directly from the task description."""

    def test_two_rect_overlaps(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3))
        assert a.find_overlaps() == [(0, 1)]

    def test_two_rect_coverage_area(self):
        # Union of (0,0,4,3) and (2,1,3,3): 12 + 9 - overlap(2x2=4) = 17
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3))
        assert math.isclose(a.calculate_coverage_area(), 17.0)

    def test_two_rect_overlap_region(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3))
        regions = a.get_overlap_regions()
        assert len(regions) == 1
        r = regions[0]["region"]
        assert r == {"x": 2, "y": 1, "width": 2, "height": 2}

    def test_three_rect_overlaps(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3), rect(1, 2, 2, 4))
        pairs = a.find_overlaps()
        assert set(pairs) == {(0, 1), (0, 2), (1, 2)}

    def test_three_rect_coverage_area_less_than_sum(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3), rect(1, 2, 2, 4))
        total = a.calculate_coverage_area()
        individual_sum = 4 * 3 + 3 * 3 + 2 * 4
        assert total < individual_sum

    def test_is_point_covered_true(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3))
        assert a.is_point_covered(3, 2) is True

    def test_is_point_covered_false(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3))
        assert a.is_point_covered(10, 10) is False

    def test_max_overlap_point_count(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3))
        hot = a.find_max_overlap_point()
        assert hot["count"] == 2

    def test_stats_keys(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3))
        stats = a.get_stats()
        assert set(stats.keys()) == {
            "total_rectangles", "overlapping_pairs",
            "total_area", "overlap_area", "coverage_efficiency",
        }

    def test_stats_values_two_rects(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(2, 1, 3, 3))
        s = a.get_stats()
        assert s["total_rectangles"] == 2
        assert s["overlapping_pairs"] == 1
        assert math.isclose(s["total_area"], 17.0)
        assert math.isclose(s["overlap_area"], 4.0)
        # efficiency = 17 / (12+9) ≈ 0.809
        assert math.isclose(s["coverage_efficiency"], 17 / 21, rel_tol=1e-6)

    def test_no_overlap_pair(self):
        # Two separated rectangles
        a = make_analyzer(rect(0, 0, 2, 2), rect(5, 5, 2, 2))
        assert a.find_overlaps() == []
        assert math.isclose(a.calculate_coverage_area(), 8.0)

    def test_contained_rectangle(self):
        # R1 fully inside R0
        a = make_analyzer(rect(0, 0, 10, 10), rect(2, 2, 3, 3))
        assert a.find_overlaps() == [(0, 1)]
        # Union area equals outer rectangle
        assert math.isclose(a.calculate_coverage_area(), 100.0)

    def test_identical_rectangles(self):
        a = make_analyzer(rect(0, 0, 5, 5), rect(0, 0, 5, 5))
        assert a.find_overlaps() == [(0, 1)]
        assert math.isclose(a.calculate_coverage_area(), 25.0)


# ─────────────────────────────────────────────────────────────────────────────
# BOUNDARY (GEOMETRIC) CASES
# ─────────────────────────────────────────────────────────────────────────────


class TestBoundaryCases:
    """Rectangles that share an edge or corner but do NOT overlap."""

    def test_shared_edge_no_overlap(self):
        # R0 right edge == R1 left edge
        a = make_analyzer(rect(0, 0, 2, 2), rect(2, 0, 2, 2))
        assert a.find_overlaps() == []

    def test_shared_corner_no_overlap(self):
        a = make_analyzer(rect(0, 0, 2, 2), rect(2, 2, 2, 2))
        assert a.find_overlaps() == []

    def test_shared_top_bottom_edge_no_overlap(self):
        a = make_analyzer(rect(0, 0, 4, 3), rect(0, 3, 4, 3))
        assert a.find_overlaps() == []

    def test_touching_chain_no_overlap(self):
        # Three side-by-side rectangles, no overlaps
        a = make_analyzer(rect(0, 0, 2, 2), rect(2, 0, 2, 2), rect(4, 0, 2, 2))
        assert a.find_overlaps() == []
        assert math.isclose(a.calculate_coverage_area(), 12.0)

    def test_coverage_touching_equals_sum(self):
        a = make_analyzer(rect(0, 0, 3, 3), rect(3, 0, 3, 3))
        assert math.isclose(a.calculate_coverage_area(), 18.0)

    def test_overlap_region_one_pixel_width(self):
        # 1-unit wide overlap strip
        a = make_analyzer(rect(0, 0, 3, 4), rect(2, 0, 3, 4))
        regions = a.get_overlap_regions()
        assert len(regions) == 1
        r = regions[0]["region"]
        assert math.isclose(r["width"], 1.0)
        assert math.isclose(r["height"], 4.0)


# ─────────────────────────────────────────────────────────────────────────────
# EDGE (INPUT) CASES
# ─────────────────────────────────────────────────────────────────────────────


class TestEdgeCases:
    """Unusual or degenerate inputs."""

    def test_empty_list(self):
        a = RectangleAnalyzer([])
        assert a.find_overlaps() == []
        assert a.calculate_coverage_area() == 0.0
        assert a.get_overlap_regions() == []
        assert a.is_point_covered(0, 0) is False
        hot = a.find_max_overlap_point()
        assert hot["count"] == 0
        s = a.get_stats()
        assert s["total_rectangles"] == 0
        assert s["coverage_efficiency"] == 0.0

    def test_single_rectangle(self):
        a = make_analyzer(rect(1, 2, 3, 4))
        assert a.find_overlaps() == []
        assert math.isclose(a.calculate_coverage_area(), 12.0)
        assert a.get_overlap_regions() == []
        assert a.is_point_covered(2, 4) is True
        assert a.is_point_covered(0, 0) is False
        s = a.get_stats()
        assert s["overlapping_pairs"] == 0
        assert math.isclose(s["coverage_efficiency"], 1.0)

    def test_zero_dimension_rectangle(self):
        # Zero-area rectangle should not create overlaps with itself or others
        a = make_analyzer(rect(0, 0, 0, 5), rect(0, 0, 3, 3))
        # zero-width rect: no area
        assert math.isclose(a.calculate_coverage_area(), 9.0)

    def test_negative_coordinates(self):
        a = make_analyzer(rect(-5, -5, 4, 4), rect(-3, -3, 4, 4))
        assert a.find_overlaps() == [(0, 1)]
        assert a.is_point_covered(-2, -2) is True
        assert math.isclose(a.calculate_coverage_area(), 28.0)

    def test_float_coordinates(self):
        a = make_analyzer(rect(0.5, 0.5, 2.5, 2.5), rect(2.0, 2.0, 2.0, 2.0))
        assert a.find_overlaps() == [(0, 1)]
        region = a.get_overlap_regions()[0]["region"]
        assert math.isclose(region["x"], 2.0)
        assert math.isclose(region["y"], 2.0)
        assert math.isclose(region["width"], 1.0)
        assert math.isclose(region["height"], 1.0)

    def test_large_single_rectangle(self):
        a = make_analyzer(rect(-1000, -1000, 2000, 2000))
        assert math.isclose(a.calculate_coverage_area(), 4_000_000.0)

    def test_point_on_boundary_is_covered(self):
        a = make_analyzer(rect(0, 0, 5, 5))
        assert a.is_point_covered(0, 0) is True   # corner
        assert a.is_point_covered(5, 5) is True   # opposite corner
        assert a.is_point_covered(5, 2) is True   # right edge
        assert a.is_point_covered(5.0001, 2) is False

    def test_coverage_efficiency_full_overlap(self):
        # Two identical rects → efficiency ≈ 0.5
        a = make_analyzer(rect(0, 0, 4, 4), rect(0, 0, 4, 4))
        s = a.get_stats()
        assert math.isclose(s["coverage_efficiency"], 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# STRESS CASES
# ─────────────────────────────────────────────────────────────────────────────


class TestStressCases:
    """Performance and correctness under large or extreme inputs."""

    def test_many_non_overlapping_rects(self):
        # 100 unit squares in a 10x10 grid — no overlaps
        rects = [rect(col * 1.0, row * 1.0, 1, 1)
                 for row in range(10) for col in range(10)]
        a = RectangleAnalyzer(rects)
        assert a.find_overlaps() == []
        assert math.isclose(a.calculate_coverage_area(), 100.0)

    def test_many_overlapping_rects(self):
        # 50 overlapping rectangles — at least one overlap must exist
        rects = [rect(i * 0.5, i * 0.5, 5, 5) for i in range(50)]
        a = RectangleAnalyzer(rects)
        assert len(a.find_overlaps()) > 0
        assert a.calculate_coverage_area() > 0

    def test_max_overlap_point_many_rects(self):
        # 20 rects all sharing the unit square (0,0,1,1)
        rects = [rect(0, 0, 1, 1)] * 20
        a = RectangleAnalyzer(rects)
        hot = a.find_max_overlap_point()
        assert hot["count"] == 20

    def test_large_coordinate_values(self):
        a = make_analyzer(
            rect(0, 0, 1_000_000, 1_000_000),
            rect(500_000, 500_000, 1_000_000, 1_000_000),
        )
        assert a.find_overlaps() == [(0, 1)]
        overlap_area = 500_000 * 500_000
        union_area = 2 * 1_000_000 ** 2 - overlap_area
        assert math.isclose(a.calculate_coverage_area(), union_area)

    def test_stats_many_rects_performance(self):
        """get_stats() should complete in reasonable time for ~200 rects."""
        rects = [rect(i % 20, i // 20, 2, 2) for i in range(200)]
        a = RectangleAnalyzer(rects)
        start = time.perf_counter()
        a.get_stats()
        elapsed = time.perf_counter() - start
        assert elapsed < 10.0, f"get_stats took {elapsed:.2f}s — too slow"
