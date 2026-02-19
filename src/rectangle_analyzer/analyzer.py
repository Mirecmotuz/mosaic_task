"""Core rectangle analysis logic."""

from __future__ import annotations

import numpy as np


class RectangleAnalyzer:
    """Analyzes axis-aligned rectangles on a 2D plane.

    Each rectangle is represented as a dict with keys:
    ``x``, ``y`` (bottom-left corner), ``width``, and ``height``.
    """

    _REQUIRED_KEYS: frozenset[str] = frozenset({"x", "y", "width", "height"})

    def __init__(self, rectangles: list[dict]) -> None:
        """Initialize the analyzer.

        Args:
            rectangles: List of rectangle dicts, each with keys
                        ``x``, ``y``, ``width``, ``height``.

        Raises:
            TypeError: If ``rectangles`` is not a list or any item is not a dict.
            KeyError: If any rectangle is missing a required key.
            TypeError: If any key value is not a real number (int or float).
        """
        self._validate(rectangles)
        self.rectangles = rectangles

    def _validate(self, rectangles: list[dict]) -> None:
        """Validate that ``rectangles`` is a properly structured list of dicts.

        Raises:
            TypeError: If ``rectangles`` is not a list or any item is not a dict.
            KeyError: If any rectangle is missing a required key.
            TypeError: If any key value is not a real number (int or float).
        """
        if not isinstance(rectangles, list):
            raise TypeError(
                f"rectangles must be a list, got {type(rectangles).__name__}"
            )
        for i, r in enumerate(rectangles):
            if not isinstance(r, dict):
                raise TypeError(
                    f"rectangles[{i}] must be a dict, got {type(r).__name__}"
                )
            missing = self._REQUIRED_KEYS - r.keys()
            if missing:
                raise KeyError(
                    f"rectangles[{i}] is missing required keys: {sorted(missing)}"
                )
            for key in self._REQUIRED_KEYS:
                if not isinstance(r[key], (int, float)) or isinstance(r[key], bool):
                    raise TypeError(
                        f"rectangles[{i}]['{key}'] must be a number, "
                        f"got {type(r[key]).__name__}"
                    )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _rect_bounds(self, r: dict) -> tuple[float, float, float, float]:
        """Return (x_min, y_min, x_max, y_max) for a rectangle."""
        return r["x"], r["y"], r["x"] + r["width"], r["y"] + r["height"]

    def _intervals_overlap(
        self, a_min: float, a_max: float, b_min: float, b_max: float
    ) -> bool:
        """Return True when two 1-D intervals strictly overlap (not just touch)."""
        return a_min < b_max and b_min < a_max

    def _rect_intersection(
        self, r1: dict, r2: dict
    ) -> dict | None:
        """Return the intersection rectangle of two rectangles, or None."""
        x1_min, y1_min, x1_max, y1_max = self._rect_bounds(r1)
        x2_min, y2_min, x2_max, y2_max = self._rect_bounds(r2)

        ix_min = max(x1_min, x2_min)
        iy_min = max(y1_min, y2_min)
        ix_max = min(x1_max, x2_max)
        iy_max = min(y1_max, y2_max)

        if ix_max <= ix_min or iy_max <= iy_min:
            return None

        return {
            "x": ix_min,
            "y": iy_min,
            "width": ix_max - ix_min,
            "height": iy_max - iy_min,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def find_overlaps(self) -> list[tuple[int, int]]:
        """Find all pairs of overlapping rectangles.

        Two rectangles overlap when their interiors intersect (touching
        edges do not count).

        Returns:
            List of tuples ``(i, j)`` where ``i < j`` are indices of
            overlapping rectangle pairs.
        """
        result: list[tuple[int, int]] = []
        rects = self.rectangles
        for i in range(len(rects)):
            xi_min, yi_min, xi_max, yi_max = self._rect_bounds(rects[i])
            for j in range(i + 1, len(rects)):
                xj_min, yj_min, xj_max, yj_max = self._rect_bounds(rects[j])
                if self._intervals_overlap(
                    xi_min, xi_max, xj_min, xj_max
                ) and self._intervals_overlap(yi_min, yi_max, yj_min, yj_max):
                    result.append((i, j))
        return result

    def calculate_coverage_area(self) -> float:
        """Calculate the total area covered by the union of all rectangles.

        Overlapping regions are counted only once.  Uses coordinate
        compression to avoid floating-point grid artefacts.

        Returns:
            Total union area as a float.
        """
        if not self.rectangles:
            return 0.0

        #we make grid out of edges of triangles and discard duplicates
        xs: list[float] = []
        ys: list[float] = []
        for r in self.rectangles:
            x_min, y_min, x_max, y_max = self._rect_bounds(r)
            xs.extend([x_min, x_max])
            ys.extend([y_min, y_max])

        xs_sorted = sorted(set(xs))
        ys_sorted = sorted(set(ys))

        #we test every cell of the grid if its center is in any rectangle and add the cell
        total: float = 0.0
        for i in range(len(xs_sorted) - 1):
            for j in range(len(ys_sorted) - 1):
                cx = (xs_sorted[i] + xs_sorted[i + 1]) / 2
                cy = (ys_sorted[j] + ys_sorted[j + 1]) / 2
                if self.is_point_covered(cx, cy):
                    total += (xs_sorted[i + 1] - xs_sorted[i]) * (
                        ys_sorted[j + 1] - ys_sorted[j]
                    )
        return total

    def get_overlap_regions(self) -> list[dict]:
        """Find the actual rectangular region for every overlapping pair.

        Returns:
            List of dicts, each containing:
            - ``rect_indices``: tuple of the two rectangle indices
            - ``region``: dict with ``x``, ``y``, ``width``, ``height``
        """
        result: list[dict] = []
        rects = self.rectangles
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                intersection = self._rect_intersection(rects[i], rects[j])
                if intersection is not None:
                    result.append(
                        {"rect_indices": (i, j), "region": intersection}
                    )
        return result

    def is_point_covered(self, x: int | float, y: int | float) -> bool:
        """Check whether the point ``(x, y)`` is covered by any rectangle.

        Args:
            x: Horizontal coordinate.
            y: Vertical coordinate.

        Returns:
            ``True`` if at least one rectangle contains the point
            (boundary inclusive).
        """
        for r in self.rectangles:
            x_min, y_min, x_max, y_max = self._rect_bounds(r)
            if x_min <= x <= x_max and y_min <= y <= y_max:
                return True
        return False

    def find_max_overlap_point(self) -> dict:
        """Find a point that is covered by the maximum number of rectangles.

        Uses coordinate compression to enumerate all distinct grid cells
        and counts how many rectangles cover each cell centre.

        Returns:
            Dict with keys ``x``, ``y`` (coordinates of the point) and
            ``count`` (number of rectangles covering it).  Returns
            ``{'x': 0, 'y': 0, 'count': 0}`` when there are no rectangles.
        """
        if not self.rectangles:
            return {"x": 0, "y": 0, "count": 0}

        xs: list[float] = []
        ys: list[float] = []
        #we make grid like in calculate_coverage_area
        for r in self.rectangles:
            x_min, y_min, x_max, y_max = self._rect_bounds(r)
            xs.extend([x_min, x_max])
            ys.extend([y_min, y_max])

        xs_sorted = sorted(set(xs))
        ys_sorted = sorted(set(ys))

        best_x: float = xs_sorted[0]
        best_y: float = ys_sorted[0]
        best_count: int = 0

        bounds = [self._rect_bounds(r) for r in self.rectangles]

        #we count in how many rectangles is the center of the cell
        for i in range(len(xs_sorted) - 1):
            cx = (xs_sorted[i] + xs_sorted[i + 1]) / 2
            for j in range(len(ys_sorted) - 1):
                cy = (ys_sorted[j] + ys_sorted[j + 1]) / 2
                count = sum(
                    1
                    for x_min, y_min, x_max, y_max in bounds
                    if x_min < cx < x_max and y_min < cy < y_max
                )
                if count > best_count:
                    best_count = count
                    best_x = cx
                    best_y = cy

        return {"x": best_x, "y": best_y, "count": best_count}

    def get_stats(self) -> dict:
        """Return coverage statistics for the current set of rectangles.

        Returns:
            Dict with:
            - ``total_rectangles``: number of rectangles
            - ``overlapping_pairs``: number of overlapping pairs
            - ``total_area``: union area of all rectangles
            - ``overlap_area``: sum of all pairwise overlap regions
            - ``coverage_efficiency``: ratio of union area to the sum of
              individual areas (1.0 means no overlaps; lower means more
              overlap).  Returns 0.0 when all rectangles have zero area.
        """
        total_rectangles = len(self.rectangles)
        overlapping_pairs = len(self.find_overlaps())
        total_area = self.calculate_coverage_area()

        overlap_regions = self.get_overlap_regions()
        overlap_area: float = sum(
            r["region"]["width"] * r["region"]["height"]
            for r in overlap_regions
        )

        sum_individual: float = sum(
            r["width"] * r["height"] for r in self.rectangles
        )
        coverage_efficiency = (
            total_area / sum_individual if sum_individual > 0 else 0.0
        )

        return {
            "total_rectangles": total_rectangles,
            "overlapping_pairs": overlapping_pairs,
            "total_area": total_area,
            "overlap_area": overlap_area,
            "coverage_efficiency": coverage_efficiency,
        }
