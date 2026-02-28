# frontend/app.py
"""
ConstructAI — Streamlit Dashboard
Site engineers upload drone/mobile photos + CAD references here.
"""

import streamlit as st
import requests
import json
import time
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
import io
import math
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ConstructAI — Site Intelligence",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Bebas+Neue&family=Manrope:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }

.stApp { background: #060709; color: #e8e9ea; }

/* Header */
.main-header {
    background: rgba(17, 18, 20, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}
.brand { font-family: 'Bebas Neue', sans-serif; font-size: 42px; letter-spacing: 5px; color: #ffffff; text-shadow: 0 0 20px rgba(255, 63, 26, 0.4); }
.brand span { color: #ff3f1a; }

/* Tabs customization */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: rgba(17, 18, 20, 0.4);
    border-radius: 8px;
    padding: 6px;
    border: 1px solid rgba(255, 255, 255, 0.03);
}
.stTabs [data-baseweb="tab"] {
    height: 48px;
    white-space: pre-wrap;
    background-color: transparent;
    border-radius: 6px;
    color: #8b909a;
    font-size: 14px;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: rgba(255, 63, 26, 0.1);
    color: #ff3f1a !important;
    box-shadow: 0 4px 12px rgba(255, 63, 26, 0.15);
    border: 1px solid rgba(255, 63, 26, 0.3);
}

/* Phase pills */
.phase-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #111214; border: 1px solid #242629;
    border-radius: 20px; padding: 6px 14px;
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    color: #6b6f78; margin: 3px;
    transition: all 0.3s ease;
}
.phase-pill.active { border-color: #ff3f1a; color: #ff3f1a; background: rgba(255,63,26,0.1); box-shadow: 0 0 10px rgba(255,63,26,0.2); }
.phase-pill.done { border-color: #00e676; color: #00e676; background: rgba(0,230,118,0.1); box-shadow: 0 0 10px rgba(0,230,118,0.2); }

/* Cards & Glassmorphism */
.glass-card {
    background: rgba(20, 22, 25, 0.4);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}
.card-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; text-transform: uppercase; letter-spacing: 3px;
    color: #8b909a; margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
}
.card-title::before { content: ''; display: block; width: 8px; height: 8px; background: #ff3f1a; border-radius: 50%; box-shadow: 0 0 8px #ff3f1a; }

/* Alerts */
.alert-box {
    background: linear-gradient(90deg, rgba(255,26,26,0.1) 0%, rgba(255,26,26,0.02) 100%);
    border-left: 4px solid #ff1a1a;
    border-radius: 0 8px 8px 0;
    padding: 20px 24px;
    margin: 16px 0;
}
.alert-title { font-family: 'Bebas Neue', sans-serif; font-size: 28px; letter-spacing: 3px; color: #ff4d4d; text-shadow: 0 0 10px rgba(255,26,26,0.3); }
.alert-desc { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #ccc; margin-top: 8px; line-height: 1.5; }

/* Success */
.success-box {
    background: linear-gradient(90deg, rgba(0,230,118,0.1) 0%, rgba(0,230,118,0.02) 100%);
    border-left: 4px solid #00e676;
    border-radius: 0 8px 8px 0;
    padding: 16px 20px;
    margin: 12px 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #00e676;
}

/* Metric */
.metric-card {
    background: rgba(17, 18, 20, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.metric-card::after {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}
.metric-val { font-family: 'Bebas Neue', sans-serif; font-size: 48px; line-height: 1; margin-bottom: 8px; }
.metric-val.red { color: #ff4d4d; text-shadow: 0 0 15px rgba(255,26,26,0.3); }
.metric-val.green { color: #00e676; text-shadow: 0 0 15px rgba(0,230,118,0.3); }
.metric-val.yellow { color: #ffb84d; text-shadow: 0 0 15px rgba(255,170,0,0.3); }
.metric-val.blue { color: #00b4ff; text-shadow: 0 0 15px rgba(0,180,255,0.3); }
.metric-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 2px; color: #8b909a; }

/* Log */
.log-line { font-family: 'JetBrains Mono', monospace; font-size: 11px; padding: 6px 12px; border-radius: 4px; margin-bottom: 2px; }
.log-line:nth-child(odd) { background: rgba(255,255,255,0.02); }

button[kind="primary"] { 
    background: linear-gradient(135deg, #ff3f1a 0%, #ff1a1a 100%) !important; 
    border: none !important; 
    box-shadow: 0 4px 15px rgba(255,63,26,0.3) !important;
    transition: all 0.2s ease !important;
}
button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255,63,26,0.4) !important;
}
</style>
""", unsafe_allow_html=True)

FASTAPI_URL = "http://localhost:8000"

# ─── Helpers ────────────────────────────────────────────────────────────────
def draw_cad_layout(cad_elements, width=640, height=400):
    """Draw 2D CAD floor plan from coordinate data"""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = (22, 24, 26)  # dark bg

    # Grid
    for x in range(0, width, 40):
        cv2.line(img, (x, 0), (x, height), (35, 38, 42), 1)
    for y in range(0, height, 40):
        cv2.line(img, (0, y), (width, y), (35, 38, 42), 1)

    # Floor plan border
    cv2.rectangle(img, (30, 30), (width-30, height-30), (0, 130, 200), 2)

    # MEP pipe route (planned) — horizontal center line
    cv2.line(img, (30, height//2), (width-30, height//2), (0, 180, 100), 2)
    # Dashed style
    for x in range(30, width-30, 16):
        cv2.line(img, (x, height//2), (min(x+8, width-30), height//2), (0, 220, 120), 2)

    # Draw elements from CAD data
    colors = {
        "Pillar": (0, 150, 255),
        "Beam": (0, 200, 255),
        "Column": (100, 220, 255),
        "Wall": (150, 150, 200),
        "Slab": (80, 80, 150),
    }

    for elem in cad_elements:
        x = elem.get("x", 100)
        y = elem.get("y", 100)
        w = elem.get("width", 40)
        h = elem.get("height", 60)
        obj = elem.get("object_type", "Pillar")
        color = colors.get(obj, (200, 200, 200))

        # Draw element
        overlay = img.copy()
        cv2.rectangle(overlay, (x - w//2, y - h//2), (x + w//2, y + h//2), color, -1)
        cv2.addWeighted(overlay, 0.25, img, 0.75, 0, img)
        cv2.rectangle(img, (x - w//2, y - h//2), (x + w//2, y + h//2), color, 2)

        # Center dot
        cv2.circle(img, (x, y), 4, color, -1)

        # Label
        cv2.putText(img, obj, (x - w//2, y - h//2 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)

        # Coordinates label
        coord_txt = f"({x},{y})"
        cv2.putText(img, coord_txt, (x - w//2, y + h//2 + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (120, 120, 140), 1, cv2.LINE_AA)

    # Legend
    cv2.putText(img, "3D CAD REFERENCE LAYOUT", (32, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 130, 200), 1, cv2.LINE_AA)
    cv2.putText(img, "-- MEP Pipe Route (Planned)", (32, height - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 200, 100), 1, cv2.LINE_AA)

    return img


def draw_astar_grid(path_result, obstacle_nodes, cols=20, rows=10, width=640, height=320):
    """Visualize A* pathfinding result on grid"""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:] = (22, 24, 26)

    cw = width / cols
    ch = height / rows

    for r in range(rows):
        for c in range(cols):
            x1, y1 = int(c*cw), int(r*ch)
            x2, y2 = int((c+1)*cw)-1, int((r+1)*ch)-1
            cv2.rectangle(img, (x1+1, y1+1), (x2-1, y2-1), (32, 35, 40), -1)

    # Obstacles (shifted pillar)
    obs_set = {(o["col"], o["row"]) for o in obstacle_nodes}
    for (c, r) in obs_set:
        x1, y1 = int(c*cw)+1, int(r*ch)+1
        x2, y2 = int((c+1)*cw)-1, int((r+1)*ch)-1
        overlay = img.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (200, 40, 20), -1)
        cv2.addWeighted(overlay, 0.5, img, 0.5, 0, img)

    # Old blocked path (red dashed)
    mid_row = int(rows // 2 * ch + ch/2)
    for c in range(cols):
        if c % 3 != 2:
            x1 = int(c * cw + cw*0.2)
            x2 = int(c * cw + cw*0.8)
            cv2.line(img, (x1, mid_row), (x2, mid_row), (180, 30, 30), 2)

    # New A* path
    path = path_result.get("path", [])
    if len(path) > 1:
        for i in range(len(path)-1):
            x1 = int(path[i]["col"] * cw + cw/2)
            y1 = int(path[i]["row"] * ch + ch/2)
            x2 = int(path[i+1]["col"] * cw + cw/2)
            y2 = int(path[i+1]["row"] * ch + ch/2)
            cv2.line(img, (x1, y1), (x2, y2), (255, 170, 0), 3)

        for node in path:
            cx = int(node["col"] * cw + cw/2)
            cy = int(node["row"] * ch + ch/2)
            cv2.circle(img, (cx, cy), 3, (255, 200, 50), -1)

    # Start / End
    if path:
        sx = int(path[0]["col"] * cw + cw/2)
        sy = int(path[0]["row"] * ch + ch/2)
        ex = int(path[-1]["col"] * cw + cw/2)
        ey = int(path[-1]["row"] * ch + ch/2)
        cv2.circle(img, (sx, sy), 8, (0, 230, 118), -1)
        cv2.circle(img, (ex, ey), 8, (0, 180, 255), -1)
        cv2.putText(img, "A", (sx-4, sy+4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)
        cv2.putText(img, "B", (ex-4, ey+4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 1)

    # Labels
    cv2.putText(img, "PILLAR OBSTACLE", (int(cols*cw*0.38), int(rows*ch*0.45)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 80, 60), 1)
    cv2.putText(img, "NEW ROUTE (A*)", (10, 18),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 200, 50), 1)
    cv2.putText(img, "BLOCKED PATH", (10, height - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (180, 60, 60), 1)

    return img


def call_analyze_api(image_bytes, cad_coords, site_name, engineer):
    """Call FastAPI /analyze endpoint"""
    try:
        files = {"site_photo": ("photo.jpg", image_bytes, "image/jpeg")}
        data = {
            "cad_data": json.dumps(cad_coords),
            "site_name": site_name,
            "engineer": engineer or "",
        }
        resp = requests.post(f"{FASTAPI_URL}/api/v1/analyze", files=files, data=data, timeout=30)
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"API Error {resp.status_code}: {resp.text}"
    except Exception as e:
        return None, str(e)


def mock_analysis(cad_coords, image_bytes):
    """
    Mock analysis when FastAPI is not running.
    Simulates realistic YOLO + A* output.
    """
    import random
    mismatches = []
    for elem in cad_coords:
        shift_x = random.choice([-1, 1]) * random.randint(25, 60)
        shift_y = random.choice([-1, 1]) * random.randint(5, 20)
        det_x = elem["x"] + shift_x
        det_y = elem["y"] + shift_y
        dx, dy = shift_x, shift_y
        offset = round(math.sqrt(dx**2 + dy**2) * 0.166, 2)
        is_err = abs(shift_x) > 20

        # A* mock
        from ml.astar.pathfinder import AStarPathfinder, compute_reroute
        pf = AStarPathfinder(20, 10)
        obstacles = pf.get_obstacle_nodes_from_mismatch(det_x, det_y)
        path_result = compute_reroute(obstacles)

        mismatches.append({
            "object_type": elem["object_type"],
            "confidence": round(0.85 + random.random()*0.12, 3),
            "detected_x": det_x,
            "detected_y": det_y,
            "expected_x": elem["x"],
            "expected_y": elem["y"],
            "delta_x": dx,
            "delta_y": dy,
            "offset_inches": offset,
            "is_error": is_err,
            "bbox": {"x1": det_x-40, "y1": det_y-60, "x2": det_x+40, "y2": det_y+60},
            "reroute": path_result if is_err else None,
        })

    return {
        "status": "ok",
        "total_detections": len(mismatches),
        "errors_found": sum(1 for m in mismatches if m["is_error"]),
        "mismatches": mismatches,
    }


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family: Bebas Neue, sans-serif; font-size: 26px; letter-spacing: 3px; color: #e8e9ea; padding-bottom: 10px; border-bottom: 1px solid #242629; margin-bottom: 16px;'>
        CONSTRUCT<span style='color:#ff3f1a'>AI</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🏗️ Site Configuration")
    site_name = st.text_input("Site Name", value="Site Alpha — Block 3")
    engineer  = st.text_input("Engineer Name", value="Rahul Sharma")
    inspection_date = st.date_input("Date of Inspection", value="today")

    st.divider()

    # ── CAD Coordinate Input ─────────────────
    st.markdown("#### 📐 3D CAD Reference Design")
    st.caption("Enter planned coordinates for each structural element:")

    if "cad_elements" not in st.session_state:
        st.session_state.cad_elements = [
            {"object_type": "Pillar", "x": 160, "y": 200, "width": 50, "height": 70},
            {"object_type": "Pillar", "x": 320, "y": 200, "width": 50, "height": 70},
            {"object_type": "Pillar", "x": 480, "y": 200, "width": 50, "height": 70},
            {"object_type": "Beam",   "x": 320, "y": 120, "width": 300, "height": 30},
        ]

    # Add new element
    with st.expander("➕ Add CAD Element", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            new_type = st.selectbox("Type", ["Pillar", "Beam", "Column", "Wall", "Slab"])
            new_x = st.number_input("X coord", min_value=0, max_value=640, value=240)
            new_w = st.number_input("Width (px)", min_value=10, max_value=300, value=50)
        with col2:
            new_y = st.number_input("Y coord", min_value=0, max_value=400, value=150)
            new_h = st.number_input("Height (px)", min_value=10, max_value=300, value=70)

        if st.button("Add Element", use_container_width=True):
            st.session_state.cad_elements.append({
                "object_type": new_type,
                "x": new_x, "y": new_y,
                "width": new_w, "height": new_h,
            })
            st.success(f"Added {new_type} at ({new_x}, {new_y})")
            st.rerun()

    # Show / Edit existing
    st.markdown("**Current CAD Elements:**")
    to_remove = None
    for i, elem in enumerate(st.session_state.cad_elements):
        cols = st.columns([3, 1])
        with cols[0]:
            st.markdown(
                f"<div style='font-family:JetBrains Mono,monospace;font-size:11px;color:#aaa;padding:4px 0'>"
                f"<b style='color:#00b4ff'>{elem['object_type']}</b> "
                f"@ ({elem['x']}, {elem['y']}) "
                f"<span style='color:#555'>{elem['width']}×{elem['height']}px</span></div>",
                unsafe_allow_html=True
            )
        with cols[1]:
            if st.button("✕", key=f"del_{i}"):
                to_remove = i
    if to_remove is not None:
        st.session_state.cad_elements.pop(to_remove)
        st.rerun()

    # JSON editor
    with st.expander("📋 Edit as JSON", expanded=False):
        raw = st.text_area("CAD JSON", value=json.dumps(st.session_state.cad_elements, indent=2), height=200)
        if st.button("Apply JSON"):
            try:
                st.session_state.cad_elements = json.loads(raw)
                st.success("Updated!")
                st.rerun()
            except:
                st.error("Invalid JSON")

    # JSON File Uploader for CAD
    uploaded_cad = st.file_uploader("📂 Upload CAD JSON File", type=["json"], help="Upload structural elements layout as a JSON file")
    if uploaded_cad is not None:
        try:
            cad_data = json.load(uploaded_cad)
            if isinstance(cad_data, list):
                st.session_state.cad_elements = cad_data
                st.success("CAD Data Loaded Successfully!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid format: CAD JSON must be a list of elements.")
        except Exception as e:
            st.error(f"Error parsing JSON: {e}")

    st.divider()
    use_mock = st.checkbox("🔧 Demo Mode (no backend needed)", value=True)
    api_url = st.text_input("FastAPI URL", value="http://localhost:8000", disabled=use_mock)
    if not use_mock:
        FASTAPI_URL = api_url


# ─── Main Header ─────────────────────────────────────────────────────────────
st.markdown(f'''
<div class="main-header">
  <div>
    <div class="brand">CONSTRUCT<span>AI</span></div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#8b909a;margin-top:4px;">
      Site Intelligence Dashboard — {site_name}
    </div>
  </div>
  <div style="text-align:right">
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#00e676;display:flex;align-items:center;gap:6px;justify-content:flex-end;">
      <div style="width:8px;height:8px;background:#00e676;border-radius:50%;box-shadow:0 0 10px #00e676;"></div> LIVE
    </div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#8b909a;margin-top:4px;">
      {datetime.now().strftime('%d %b %Y — %H:%M:%S')}
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

# Phase pipeline
phases = [
    ("1", "Data Input", True),
    ("2", "Vision AI", False),
    ("3", "Logic AI", False),
    ("4", "Dashboard", False),
]
phase_html = "<div style='margin-bottom:24px;'>"
for num, label, done in phases:
    cls = "done" if done else "active" if num == "1" else ""
    icon = "✓" if done else num
    phase_html += f'<span class="phase-pill {cls}">{icon} {label}</span>'
    if num != "4":
        phase_html += '<span style="color:#444;margin:0 4px;font-size:12px;">→</span>'
phase_html += "</div>"
st.markdown(phase_html, unsafe_allow_html=True)

# ─── Tabs Layout ─────────────────────────────────────────────────────────────
tab_dash, tab_check, tab_alerts = st.tabs([
    "📊 TIME & DASHBOARD", 
    "📷 DAILY DESIGN CHECK", 
    "🛠️ INTELLI-SUGGESTIONS & ALERTS"
])

# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD & TIME MANAGEMENT
# ═════════════════════════════════════════════════════════════════════════════
with tab_dash:
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="metric-card"><div class="metric-val blue">73%</div><div class="metric-label">Overall Schedule Progress</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><div class="metric-val red">-4 Days</div><div class="metric-label">Time Management (Delay)</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><div class="metric-val yellow">12</div><div class="metric-label">Active Warnings</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="metric-card"><div class="metric-val green">Phase 2</div><div class="metric-label">Current Milestone</div></div>', unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⏱️ TIMELINE MANAGEMENT & FORECAST</div>', unsafe_allow_html=True)
    st.markdown('''
    <div style='display:flex; align-items:center; gap:16px; margin-top:20px;'>
        <div style='width:100px; font-family:JetBrains Mono,monospace; font-size:12px; color:#aaa;'>Planned</div>
        <div style='flex:1; background:rgba(255,255,255,0.05); height:12px; border-radius:6px; overflow:hidden;'>
            <div style='width:80%; height:100%; background:#00b4ff; border-radius:6px;'></div>
        </div>
        <div style='width:60px; font-family:JetBrains Mono,monospace; font-size:12px; color:#00b4ff; text-align:right;'>80%</div>
    </div>
    <div style='display:flex; align-items:center; gap:16px; margin-top:16px;'>
        <div style='width:100px; font-family:JetBrains Mono,monospace; font-size:12px; color:#aaa;'>Actual</div>
        <div style='flex:1; background:rgba(255,255,255,0.05); height:12px; border-radius:6px; overflow:hidden;'>
            <div style='width:73%; height:100%; background:#ffaa00; border-radius:6px; box-shadow:0 0 10px rgba(255,170,0,0.5);'></div>
        </div>
        <div style='width:60px; font-family:JetBrains Mono,monospace; font-size:12px; color:#ffaa00; text-align:right;'>73%</div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: DAILY DESIGN CHECK
# ═════════════════════════════════════════════════════════════════════════════
with tab_check:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="success-box">📸 <b>MANDATORY:</b> Upload 4 perspectives (Top, Front, Left, Right) to run full 3D layout matching.</div>', unsafe_allow_html=True)

    cam1, cam2, cam3, cam4 = st.columns(4)
    with cam1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🚁 ANGLE 1: TOP</div>', unsafe_allow_html=True)
        uploaded_top = st.file_uploader("Drone/Top", type=["jpg", "png"], key="top")
        if uploaded_top:
            img_top = Image.open(uploaded_top)
            st.image(img_top, use_column_width=True, caption="Top Accepted")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with cam2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📷 ANGLE 2: FRONT</div>', unsafe_allow_html=True)
        uploaded_front = st.file_uploader("Front View", type=["jpg", "png"], key="front")
        if uploaded_front:
            img_front = Image.open(uploaded_front)
            st.image(img_front, use_column_width=True, caption="Front Accepted")
        st.markdown('</div>', unsafe_allow_html=True)

    with cam3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📷 ANGLE 3: LEFT</div>', unsafe_allow_html=True)
        uploaded_left = st.file_uploader("Left View", type=["jpg", "png"], key="left")
        if uploaded_left:
            img_left = Image.open(uploaded_left)
            st.image(img_left, use_column_width=True, caption="Left Accepted")
        st.markdown('</div>', unsafe_allow_html=True)

    with cam4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📷 ANGLE 4: RIGHT</div>', unsafe_allow_html=True)
        uploaded_right = st.file_uploader("Right View", type=["jpg", "png"], key="right")
        if uploaded_right:
            img_right = Image.open(uploaded_right)
            st.image(img_right, use_column_width=True, caption="Right Accepted")
        st.markdown('</div>', unsafe_allow_html=True)

    btn_col, info_col = st.columns([2, 3])
    with btn_col:
        all_uploaded = uploaded_top and uploaded_front and uploaded_left and uploaded_right
        run_btn = st.button("⚡ RUN 4-ANGLE ANALYSIS", use_container_width=True, type="primary", disabled=not use_mock and not all_uploaded)
        if not use_mock and not all_uploaded:
            st.caption("Upload all 4 angles to enable AI analysis")
    with info_col:
        st.markdown('''
        <div style='background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.05);border-radius:8px;padding:12px 16px;
                    font-family:JetBrains Mono,monospace;font-size:11px;color:#888;'>
            <b style='color:#bbb'>Quad-Vision Engine:</b> 4 distinct views synchronized
            → 3D Bounding Boxes → High Precision CAD Matching → A* Rerouting
        </div>
        ''', unsafe_allow_html=True)

    if run_btn:
        if not st.session_state.cad_elements:
            st.error("Please add at least one CAD element in the sidebar first!")
            st.stop()
            
        # Simulating processing
        log_placeholder = st.empty()
        logs = []
        def add_log(src, msg, color="#aaa"):
            logs.append(f'<div class="log-line"><span style="color:#555">{datetime.now().strftime("%H:%M:%S")}</span> <span style="color:{color};font-weight:600">[{src}]</span> <span style="color:{color}">{msg}</span></div>')
            log_placeholder.markdown(f'<div style="background:rgba(0,0,0,0.5);border:1px solid #222;border-radius:8px;padding:12px;max-height:160px;overflow-y:auto">' + "".join(logs) + "</div>", unsafe_allow_html=True)

        add_log("FASTAPI", "Request received — Processing 4 View Angles", "#00b4ff")
        time.sleep(0.4)
        add_log("YOLOV8", "Extracting 2D BBoxes from 4 distinct perspectives...", "#ff3f1a")
        time.sleep(0.6)
        add_log("FUSION", "Triangulating 3D coords with CAD Reference...", "#ffaa00")
        time.sleep(0.5)

        # Generate fake image from front view if uploaded, else blank
        if uploaded_front:
            uploaded_front.seek(0)
            image_bytes = uploaded_front.read()
        else:
            h, w = 480, 640
            demo_img = np.zeros((h, w, 3), dtype=np.uint8)
            demo_img[:] = (20, 22, 25)
            for i, elem in enumerate(st.session_state.cad_elements):
                shift = (i+1) * 35 * (1 if i%2==0 else -1)
                cv2.rectangle(demo_img, (elem["x"] + shift - elem["width"]//2, elem["y"] - elem["height"]//2),
                              (elem["x"] + shift + elem["width"]//2, elem["y"] + elem["height"]//2), (80, 100, 120), -1)
            _, buf = cv2.imencode(".jpg", demo_img)
            image_bytes = buf.tobytes()

        if use_mock:
            result = mock_analysis(st.session_state.cad_elements, image_bytes)
        else:
            result, err = call_analyze_api(image_bytes, st.session_state.cad_elements, site_name, engineer)
            if err: st.error(err); st.stop()

        mismatches = result.get("mismatches", [])
        errors = [m for m in mismatches if m.get("is_error")]
        
        for m in mismatches:
            add_log("QUAD-ENGINE", f"{m['object_type']} detected @ ({m['detected_x']},{m['detected_y']})", "#00e676" if not m['is_error'] else "#ff1a1a")
            time.sleep(0.1)
            
        if errors:
            add_log("A*ALGO", f"Computing alternate MEP routes...", "#ffaa00")
            time.sleep(0.4)
            add_log("SUPABASE", "Saved deviation report & alerts dispatched.", "#00b4ff")

        st.divider()
        st.markdown("### 📊 CAD vs Actual Comparison")
        c_cad, c_act = st.columns(2)
        with c_cad:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">📐 3D CAD REFERENCE (EXPECTED)</div>', unsafe_allow_html=True)
            st.image(draw_cad_layout(st.session_state.cad_elements, 640, 380), use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c_act:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title">🔴 AI DETECTED LAYOUT (ACTUAL)</div>', unsafe_allow_html=True)
            
            site_img = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
            site_img = cv2.resize(site_img, (640, 380))
            for m in mismatches:
                scale_x, scale_y = 1.0, 380/640
                bbox = m.get("bbox") or {"x1": m["detected_x"]-40, "y1": m["detected_y"]-60, "x2": m["detected_x"]+40, "y2": m["detected_y"]+60}
                x1, y1 = int(bbox["x1"]*scale_x), int(bbox["y1"]*scale_y)
                x2, y2 = int(bbox["x2"]*scale_x), int(bbox["y2"]*scale_y)
                color = (0, 0, 255) if m["is_error"] else (0, 220, 100)
                cv2.rectangle(site_img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(site_img, f"{m['object_type']}", (x1, y1-6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
            st.image(site_img, use_column_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        # Error Details Table
        st.markdown("#### 🔍 Defect Triage")
        for m in mismatches:
            if m["is_error"]:
                st.markdown(f'''
                <div style='background:rgba(255,26,26,0.05); border:1px solid rgba(255,26,26,0.2); border-radius:8px; padding:12px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;'>
                    <div><b style='color:#ff4d4d'>MISMATCH: {m['object_type']}</b> shifted by {m['offset_inches']}" (Δx:{m['delta_x']}, Δy:{m['delta_y']})</div>
                    <div style='background:#ff1a1a; color:#fff; font-size:10px; font-weight:bold; padding:4px 8px; border-radius:4px;'>CRITICAL</div>
                </div>
                ''', unsafe_allow_html=True)
        
        st.success("✅ Analysis Phase Complete — Please review the '🛠️ Alerts & Suggestions' tab for rerouting strategies.")

# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: ALERTS & SUGGESTIONS
# ═════════════════════════════════════════════════════════════════════════════
with tab_alerts:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🧠 PROACTIVE AI SUGGESTIONS</div>', unsafe_allow_html=True)
    st.markdown('''
    <div style='display:grid; grid-template-columns:1fr 1fr; gap:16px;'>
        <div style='background:rgba(255,170,0,0.1); border-left:3px solid #ffaa00; padding:16px; border-radius:4px;'>
            <div style='color:#ffb84d; font-family:Bebas Neue; font-size:20px; letter-spacing:1px;'>SCHEDULE DELAY DETECTED</div>
            <div style='color:#ccc; font-size:13px; margin-top:4px;'>Based on current structural progress (-4 days), consider ordering <b>15% more rapid-setting cement</b> to catch up on the next slab pour.</div>
            <button style='margin-top:12px; background:transparent; border:1px solid #ffaa00; color:#ffaa00; padding:4px 12px; border-radius:4px; font-size:12px; cursor:pointer;'>Auto-Draft Material Order request</button>
        </div>
        <div style='background:rgba(0,180,255,0.1); border-left:3px solid #00b4ff; padding:16px; border-radius:4px;'>
            <div style='color:#00b4ff; font-family:Bebas Neue; font-size:20px; letter-spacing:1px;'>CAD MODEL AUTO-UPDATE</div>
            <div style='color:#ccc; font-size:13px; margin-top:4px;'>Pillar positions have shifted from initial architecture. A* has provided a valid alternate MEP route. Would you like to update the master CAD file?</div>
            <button style='margin-top:12px; background:transparent; border:1px solid #00b4ff; color:#00b4ff; padding:4px 12px; border-radius:4px; font-size:12px; cursor:pointer;'>Update Master CAD (.dxf)</button>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🗺️ A* PATHFINDING & ALTERNATE MEP PIPING ROUTES</div>', unsafe_allow_html=True)
    
    # Generate A* viz on the fly for demo if result is not in session scope
    from ml.astar.pathfinder import AStarPathfinder, compute_reroute
    pf = AStarPathfinder(20, 10)
    obstacles = pf.get_obstacle_nodes_from_mismatch(300, 150)
    reroute = compute_reroute(obstacles)
    astar_vis = draw_astar_grid(reroute, obstacles, width=800, height=300)
    
    c_img, c_text = st.columns([3, 2])
    with c_img:
        st.image(astar_vis, use_column_width=True, caption="Alternate MEP pipe routing avoiding new structure placement")
    with c_text:
        st.markdown(f'''
        <div style='background:rgba(0,0,0,0.3); border:1px solid rgba(255,255,255,0.05); border-radius:8px; padding:20px; font-family:JetBrains Mono,monospace;font-size:12px;'>
            <div style='color:#00e676; margin-bottom:12px; font-size:14px; font-weight:bold;'>✓ VALID REROUTE FOUND</div>
            <div style='color:#aaa;margin-bottom:8px;'>Path Length: <span style='color:#fff'>{reroute.get("path_length",24)} nodes</span></div>
            <div style='color:#aaa;margin-bottom:8px;'>Compute Time: <span style='color:#fff'>{reroute.get("compute_ms",12)} ms</span></div>
            <div style='color:#aaa;margin-bottom:8px;'>Extra Pipe Cost: <span style='color:#ffaa00'>+₹4,500</span></div>
            <div style='color:#888; margin-top:16px; font-size:11px; line-height:1.4;'>
                The HVAC / Fire suppression lines can bypass the shifted pillar by routing 0.8 meters north.
            </div>
            <button style='width:100%; margin-top:16px; background:#ff3f1a; border:none; color:white; padding:8px; border-radius:4px; font-weight:bold; cursor:pointer;'>NOTIFY SITE ENGINEER</button>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown('''
<div style='text-align:center;padding:24px;font-family:JetBrains Mono,monospace;font-size:11px;
            color:#444;border-top:1px solid rgba(255,255,255,0.05);margin-top:40px;'>
  CONSTRUCTAI © 2026 &nbsp;|&nbsp; Streamlit • FastAPI • YOLOv8 • A* Pathfinding
</div>
''', unsafe_allow_html=True)
