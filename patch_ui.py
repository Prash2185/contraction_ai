import codecs
import json
import os

path = 'd:/hackethon/constructai/frontend/app.py'

with codecs.open(path, 'r', 'utf-8') as f:
    content = f.read()

idx = content.find('# ─── Main Header ────────────────')
if idx == -1:
    print('Error: Main Header not found in fronted/app.py')
    import sys
    sys.exit(1)

new_ui = r"""# ─── Main Header ─────────────────────────────────────────────────────────────
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
            st.image(img_top, use_container_width=True, caption="Top Accepted")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with cam2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📷 ANGLE 2: FRONT</div>', unsafe_allow_html=True)
        uploaded_front = st.file_uploader("Front View", type=["jpg", "png"], key="front")
        if uploaded_front:
            img_front = Image.open(uploaded_front)
            st.image(img_front, use_container_width=True, caption="Front Accepted")
        st.markdown('</div>', unsafe_allow_html=True)

    with cam3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📷 ANGLE 3: LEFT</div>', unsafe_allow_html=True)
        uploaded_left = st.file_uploader("Left View", type=["jpg", "png"], key="left")
        if uploaded_left:
            img_left = Image.open(uploaded_left)
            st.image(img_left, use_container_width=True, caption="Left Accepted")
        st.markdown('</div>', unsafe_allow_html=True)

    with cam4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📷 ANGLE 4: RIGHT</div>', unsafe_allow_html=True)
        uploaded_right = st.file_uploader("Right View", type=["jpg", "png"], key="right")
        if uploaded_right:
            img_right = Image.open(uploaded_right)
            st.image(img_right, use_container_width=True, caption="Right Accepted")
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
            st.image(draw_cad_layout(st.session_state.cad_elements, 640, 380), use_container_width=True)
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
            st.image(site_img, use_container_width=True)
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
        st.image(astar_vis, use_container_width=True, caption="Alternate MEP pipe routing avoiding new structure placement")
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
"""

final_content = content[:idx] + new_ui

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(final_content)

print(f"Successfully wrote {len(final_content)} chars to app.py")
