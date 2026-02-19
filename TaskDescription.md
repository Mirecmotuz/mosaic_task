Python
Rectangle Packing Analyzer -- Python
Developer Task
Overview
Create a Python tool that analyzes rectangles placed on a 2D plane, finding overlaps and
calculating coverage statistics.
Task Description
Build a RectangleAnalyzer class that processes a collection of axis-aligned rectangles
and provides various analytical methods.
Input Format
Rectangles are defined by their bottom-left corner position and dimensions:
rectangles = [
{'x': 0, 'y': 0, 'width': 4, 'height': 3},
{'x': 2, 'y': 1, 'width': 3, 'height': 3},
{'x': 1, 'y': 2, 'width': 2, 'height': 4},
]
Required Implementation
Core Class Structure
Python
class RectangleAnalyzer:
def __init__(self, rectangles:
list[dict]):
"""
Initialize analyzer with list of rectangles.
Each rectangle is a dict with keys: x, y, width, height
"""
self.rectangles = rectangles
def find_overlaps(self) -> list[tuple]:
"""
Find all pairs of overlapping rectangles.
Returns: List of tuples (i, j) where i < j are indices
Example: [(0, 1), (0, 2), (1, 2)]
"""
pass
def calculate_coverage_area(self) -> float:
"""
Calculate total area covered by all rectangles.
Overlapping areas should be counted only once.
Returns: float/int representing total area
"""
pass
def get_overlap_regions(self) -> list[dict]:
"""
Find actual overlap regions between rectangles.
Returns: List of dicts containing:
- 'rect_indices': tuple of rectangle indices
- 'region': dict with x, y, width, height of overlap
"""
pass
def is_point_covered(self, x: int|float, y: int|float) ->
bool:
"""
Check if a point is covered by any rectangle.
Returns: boolean
"""
pass
def find_max_overlap_point(self) -> dict:
"""
Find a point covered by maximum number of rectangles.
Returns: dict with 'x', 'y', 'count' keys
Note: There might be multiple such points, return any
one.
"""
pass
def get_stats(self) -> dict:
"""
Get coverage statistics.
Returns: dict with:
- 'total_rectangles': int
- 'overlapping_pairs': int
- 'total_area': float (union area)
- 'overlap_area': float (sum of all overlap regions)
- 'coverage_efficiency': float (total_area /
sum_of_individual_areas)
"""
pass
Part of Your Task
You should identify and implement test cases that validate your solution. Think about:
● What edge cases might break the implementation?
● What scenarios would be important to test?
● How would you structure your tests to be comprehensive?
Create a test file (test_rectangles.py) that demonstrates your solution handles various
scenarios correctly. Consider including:
● Normal cases
● Boundary cases (from the geometrical configuration perspective)
● Edge cases (from the input structure perspective)
● Stress cases (extreme input)
Python
Example Usage
# Example 1: Simple overlap case
rectangles = [
{'x': 0, 'y': 0, 'width': 4, 'height': 3},
{'x': 2, 'y': 1, 'width': 3, 'height': 3},
]
analyzer = RectangleAnalyzer(rectangles)
overlaps = analyzer.find_overlaps()
print(f"Overlapping pairs: {overlaps}") # [(0, 1)]
total_area = analyzer.calculate_coverage_area()
print(f"Total coverage: {total_area}") # Should be less than 12 +
9 = 21
overlap_regions = analyzer.get_overlap_regions()
print(f"Overlap region: {overlap_regions[0]['region']}")
# {'x': 2, 'y': 1, 'width': 2, 'height': 2}
# Example 2: Point checking
is_covered = analyzer.is_point_covered(3, 2)
print(f"Point (3, 2) covered: {is_covered}") # True
hotspot = analyzer.find_max_overlap_point()
print(f"Max overlap point: {hotspot}") # {'x': 3, 'y': 2,
'count': 2}
Rules
● The task should take approximately 4 hours for a Middle Python programmer. If it
takes longer you can either spend more time with it or stop any moment. And we
will discuss the solution.
● The solution should be provided as a repository on github.com
● Python environment should be defined with pyproject.toml or pixi.toml or any other
environment file which defines the environment for the specific
environment/packaging tools. Avoid using environment.txt/requirement.txt type of
files.
● Have minimal documentation in the README.md file which says how to run the
project and what to expect.
● Document core functions, use typehints.
● Avoid any OS specific implementations