# Rectangle Analyzer

A Python tool that analyzes axis-aligned rectangles placed on a 2D plane —
finding overlaps, calculating union coverage area, and serving an interactive
Web UI for manual input.

## Features

- Find all overlapping rectangle pairs
- Calculate the total union coverage area (overlapping regions counted once)
- Find the exact overlap region for every overlapping pair
- Check whether any point is covered
- Find the point covered by the most rectangles
- Aggregated statistics (total area, overlap area, coverage efficiency)
- **Web UI** — add rectangles interactively, visualise results on a Canvas
- **Docker** — runs identically on any OS

---

## Requirements

- [Docker](https://docs.docker.com/get-docker/)

---

## Build & Run

```bash
docker build -t rectangle-analyzer .
docker run -p 8000:8000 rectangle-analyzer
```

Open **http://localhost:8000** in your browser.

---

## Running Tests

```bash
docker run --rm rectangle-analyzer pytest tests/ -v
```

Expected: all tests pass across normal, boundary, edge, and stress scenarios.

### Test design rationale

**What edge cases might break the implementation?**
- Empty rectangle list — all methods must return sensible defaults without crashing
- Single rectangle — no overlaps, coverage equals its own area, efficiency = 1.0
- Zero-dimension rectangle (width or height = 0) — must not contribute area
- Negative coordinates — coordinate compression must handle negative origins
- Float coordinates — intersection calculations must stay numerically correct
- Point exactly on a boundary — `is_point_covered` treats boundaries as inclusive
- `bool` values (`True`/`False`) — Python's `bool` is a subclass of `int`; explicitly rejected by validation
- Malformed input (missing keys, wrong types, not a list) — caught in `__init__` before any computation

**What scenarios are important to test?**
- Two and three overlapping rectangles matching the task description examples
- One rectangle fully contained inside another — union area equals the outer rectangle
- Identical rectangles — coverage efficiency = 0.5
- Rectangles that share only an edge or corner — must **not** be counted as overlapping
- A chain of side-by-side touching rectangles — total area equals the sum of individuals
- Large coordinate values (10⁶) — verifies there is no integer overflow or precision loss

**How are the tests structured?**

Tests are split into four classes, each covering a distinct concern:

| Class | Focus |
|---|---|
| `TestValidation` | Malformed or invalid input rejected before computation |
| `TestNormalCases` | Correct results for typical multi-rectangle scenarios |
| `TestBoundaryCases` | Geometric edge cases — touching but not overlapping |
| `TestStressCases` | Correctness and performance under large or extreme inputs |

---

## Web UI

After starting the container, open **http://localhost:8000**:

1. Add rectangles using the form on the left (x, y, width, height)
2. Click **Analyze**
3. The canvas shows the rectangles, overlap regions (cross-hatched), and the
   maximum overlap point (white dot)
4. Statistics appear in the bottom bar

---

## API

Interactive docs: **http://localhost:8000/docs**

### `POST /analyze`

**Request**
```json
{
  "rectangles": [
    {"x": 0, "y": 0, "width": 4, "height": 3},
    {"x": 2, "y": 1, "width": 3, "height": 3}
  ]
}
```

**Response**
```json
{
  "overlaps": [[0, 1]],
  "coverage_area": 17.0,
  "overlap_regions": [
    {"rect_indices": [0, 1], "region": {"x": 2, "y": 1, "width": 2, "height": 2}}
  ],
  "max_overlap_point": {"x": 3.0, "y": 2.0, "count": 2},
  "stats": {
    "total_rectangles": 2,
    "overlapping_pairs": 1,
    "total_area": 17.0,
    "overlap_area": 4.0,
    "coverage_efficiency": 0.8095238095238095
  }
}
```

---

## Project Structure

```
mosaic_task/
├── src/
│   └── rectangle_analyzer/
│       ├── __init__.py           # public exports
│       ├── analyzer.py           # RectangleAnalyzer core class
│       ├── api.py                # FastAPI application
│       ├── templates/
│       │   └── index.html        # HTML page
│       └── static/
│           ├── style.css         # styles
│           └── app.js            # canvas + API logic
├── tests/
│   └── test_rectangles.py        # pytest test suite
├── Dockerfile
├── .dockerignore
├── pyproject.toml
└── README.md
```
