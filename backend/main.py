# backend/main.py
"""
ConstructAI — FastAPI Backend
The bridge between Streamlit UI, YOLO, A*, and Supabase.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.schemas import PathfindRequest, AnalyzeRequest
from ml.yolo.detector import ConstructionDetector
from ml.astar.pathfinder import compute_reroute, AStarPathfinder
from backend.utils.supabase_client import save_report, get_reports, update_report_status

app = FastAPI(
    title="ConstructAI API",
    description="Construction Site Intelligence — Vision AI + Logic AI Backend",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize detector once at startup
detector = ConstructionDetector()


# ─────────────────────────────────────────
# PHASE 2 + 3: Analyze image + pathfind
# ─────────────────────────────────────────

@app.post("/api/v1/analyze")
async def analyze_site(
    site_photo: UploadFile = File(..., description="Drone/mobile site photo"),
    cad_data: str = Form(..., description="JSON string of CAD coordinates"),
    site_name: str = Form(default="Site A"),
    engineer: str = Form(default=None),
):
    """
    Full pipeline:
    1. Receive site photo + CAD coordinates
    2. OpenCV preprocess → YOLOv8 detect → compare with CAD
    3. A* reroute for each error found
    4. Save to Supabase
    5. Return full result
    """
    try:
        image_bytes = await site_photo.read()
        cad_coords = json.loads(cad_data)
    except Exception as e:
        raise HTTPException(400, f"Invalid input: {str(e)}")

    # ── Step 2: Vision AI ──────────────────
    try:
        detections = detector.detect(image_bytes)
        mismatches = detector.compare_with_cad(detections, cad_coords)
    except Exception as e:
        raise HTTPException(500, f"YOLO detection failed: {str(e)}")

    # ── Step 3: Logic AI (A*) for each error ──
    results = []
    for m in mismatches:
        path_result = None
        if m["is_error"]:
            pf = AStarPathfinder(cols=20, rows=10)
            obstacles = pf.get_obstacle_nodes_from_mismatch(
                m["detected_x"], m["detected_y"]
            )
            path_result = compute_reroute(obstacles)

            # ── Step 4: Save to Supabase ──────
            try:
                save_report({
                    "site_name": site_name,
                    "engineer": engineer,
                    "object_type": m["object_type"],
                    "confidence": m["confidence"],
                    "detected_x": m["detected_x"],
                    "detected_y": m["detected_y"],
                    "expected_x": m["expected_x"],
                    "expected_y": m["expected_y"],
                    "offset_inches": m["offset_inches"],
                    "rerouted_path": path_result.get("path") if path_result else None,
                    "path_length_m": path_result.get("path_length", 0) * 0.3 if path_result else None,
                    "status": "open",
                })
            except Exception as e:
                print(f"Supabase save warning: {e}")

        results.append({**m, "reroute": path_result})

    return {
        "status": "ok",
        "total_detections": len(detections),
        "errors_found": sum(1 for m in mismatches if m["is_error"]),
        "mismatches": results,
    }


@app.post("/api/v1/analyze/annotated-image")
async def get_annotated_image(
    site_photo: UploadFile = File(...),
    cad_data: str = Form(...),
):
    """Returns the site photo with YOLO bounding boxes drawn on it"""
    image_bytes = await site_photo.read()
    cad_coords = json.loads(cad_data)
    detections = detector.detect(image_bytes)
    mismatches = detector.compare_with_cad(detections, cad_coords)
    annotated = detector.draw_detections(image_bytes, mismatches)
    return Response(content=annotated, media_type="image/jpeg")


# ─────────────────────────────────────────
# PHASE 3: Standalone A* endpoint
# ─────────────────────────────────────────

@app.post("/api/v1/pathfind")
async def pathfind(req: PathfindRequest):
    """Direct A* pathfinding endpoint"""
    obstacles = [{"col": n.col, "row": n.row} for n in req.obstacle_nodes]
    start = {"col": req.start.col, "row": req.start.row}
    end = {"col": req.end.col, "row": req.end.row}
    result = compute_reroute(obstacles, start, end, req.grid_cols, req.grid_rows)
    return result


# ─────────────────────────────────────────
# PHASE 4: Reports / Supabase
# ─────────────────────────────────────────

@app.get("/api/v1/reports")
async def list_reports(site_name: str = None, limit: int = 50):
    """Fetch all detection reports from Supabase"""
    try:
        return get_reports(site_name, limit)
    except Exception as e:
        raise HTTPException(500, str(e))


@app.patch("/api/v1/reports/{report_id}/status")
async def patch_status(report_id: int, status: str):
    """Update report status: open → resolved / ignored"""
    if status not in ("open", "resolved", "ignored"):
        raise HTTPException(400, "status must be: open, resolved, or ignored")
    return update_report_status(report_id, status)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ConstructAI API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
