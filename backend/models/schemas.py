# backend/models/schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CADCoordinate(BaseModel):
    """One element from the CAD design layout"""
    object_type: str          # "Pillar", "Beam", "Column", "Wall"
    x: int
    y: int
    width: int
    height: int


class DetectionResult(BaseModel):
    """YOLOv8 detection output for one object"""
    object_type: str
    confidence: float
    detected_x: int
    detected_y: int
    bbox_width: int
    bbox_height: int


class MismatchResult(BaseModel):
    """Comparison between detected vs expected position"""
    object_type: str
    confidence: float
    detected_x: int
    detected_y: int
    expected_x: int
    expected_y: int
    delta_x: int
    delta_y: int
    offset_inches: float
    is_error: bool


class PathNode(BaseModel):
    col: int
    row: int


class PathfindRequest(BaseModel):
    """Input to A* pathfinding"""
    grid_cols: int = 20
    grid_rows: int = 10
    obstacle_nodes: List[PathNode]
    start: PathNode
    end: PathNode


class PathfindResult(BaseModel):
    """A* output"""
    success: bool
    path: List[PathNode]
    nodes_explored: int
    path_length: int
    compute_ms: float
    message: str


class AnalyzeRequest(BaseModel):
    site_name: str = "Site A"
    engineer: Optional[str] = None
    cad_coordinates: List[CADCoordinate]


class ReportResponse(BaseModel):
    id: int
    created_at: datetime
    site_name: str
    object_type: str
    confidence: float
    detected_x: int
    detected_y: int
    expected_x: int
    expected_y: int
    delta_x: int
    delta_y: int
    offset_inches: float
    rerouted_path: Optional[list]
    status: str

    class Config:
        from_attributes = True
