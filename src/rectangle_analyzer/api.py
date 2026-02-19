"""FastAPI application exposing the RectangleAnalyzer via HTTP."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from rectangle_analyzer.analyzer import RectangleAnalyzer

app = FastAPI(
    title="Rectangle Analyzer",
    description="Analyze overlaps and coverage of axis-aligned rectangles.",
    version="0.1.0",
)

_STATIC_DIR = Path(__file__).parent / "static"
_TEMPLATES_DIR = Path(__file__).parent / "templates"
app.mount("/static", StaticFiles(directory=_STATIC_DIR), name="static")


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------


class RectangleModel(BaseModel):
    x: float
    y: float
    width: float
    height: float

    @field_validator("width", "height")
    @classmethod
    def must_be_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("width and height must be non-negative")
        return v


class AnalyzeRequest(BaseModel):
    rectangles: list[RectangleModel]
    check_point: dict | None = None  # optional: {"x": ..., "y": ...}


class OverlapRegion(BaseModel):
    rect_indices: tuple[int, int]
    region: RectangleModel


class AnalyzeResponse(BaseModel):
    overlaps: list[tuple[int, int]]
    coverage_area: float
    overlap_regions: list[OverlapRegion]
    max_overlap_point: dict
    stats: dict


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
async def serve_ui() -> FileResponse:
    """Serve the single-page Web UI."""
    return FileResponse(_TEMPLATES_DIR / "index.html")


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze the provided rectangles and return full statistics.

    Args:
        payload: JSON body with a ``rectangles`` list and an optional
                 ``check_point`` dict ``{"x": ..., "y": ...}``.

    Returns:
        Overlap pairs, coverage area, overlap regions, max-overlap point
        and aggregated statistics.
    """
    rects = [r.model_dump() for r in payload.rectangles]

    if not rects:
        return AnalyzeResponse(
            overlaps=[],
            coverage_area=0.0,
            overlap_regions=[],
            max_overlap_point={"x": 0, "y": 0, "count": 0},
            stats={
                "total_rectangles": 0,
                "overlapping_pairs": 0,
                "total_area": 0.0,
                "overlap_area": 0.0,
                "coverage_efficiency": 0.0,
            },
        )

    analyzer = RectangleAnalyzer(rects)

    try:
        overlaps = analyzer.find_overlaps()
        coverage_area = analyzer.calculate_coverage_area()
        raw_regions = analyzer.get_overlap_regions()
        max_point = analyzer.find_max_overlap_point()
        stats = analyzer.get_stats()
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    overlap_regions = [
        OverlapRegion(
            rect_indices=entry["rect_indices"],
            region=RectangleModel(**entry["region"]),
        )
        for entry in raw_regions
    ]

    return AnalyzeResponse(
        overlaps=overlaps,
        coverage_area=coverage_area,
        overlap_regions=overlap_regions,
        max_overlap_point=max_point,
        stats=stats,
    )
