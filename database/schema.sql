-- ConstructAI Supabase Schema
-- Run this in your Supabase SQL Editor

-- -----------------------------------------------
-- Table: detection_reports
-- Stores every error detected on site
-- -----------------------------------------------
CREATE TABLE detection_reports (
    id          BIGSERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ DEFAULT NOW(),

    -- Site info
    site_name   TEXT NOT NULL DEFAULT 'Site A',
    engineer    TEXT,

    -- Detection details
    object_type TEXT NOT NULL,           -- e.g. 'Pillar', 'Beam', 'Column'
    confidence  FLOAT NOT NULL,          -- YOLOv8 confidence 0-1

    -- Coordinate mismatch
    detected_x  INT NOT NULL,
    detected_y  INT NOT NULL,
    expected_x  INT NOT NULL,
    expected_y  INT NOT NULL,
    delta_x     INT GENERATED ALWAYS AS (detected_x - expected_x) STORED,
    delta_y     INT GENERATED ALWAYS AS (detected_y - expected_y) STORED,
    offset_inches FLOAT,                 -- physical real-world offset

    -- A* result
    original_path   JSONB,              -- blocked path nodes
    rerouted_path   JSONB,              -- new A* path nodes
    path_length_m   FLOAT,

    -- Status
    status      TEXT DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'ignored')),
    notes       TEXT
);

-- -----------------------------------------------
-- Enable Realtime on this table
-- (Run in Supabase Dashboard > Database > Replication)
-- -----------------------------------------------
ALTER PUBLICATION supabase_realtime ADD TABLE detection_reports;

-- -----------------------------------------------
-- Table: cad_references
-- Stores uploaded CAD coordinate data
-- -----------------------------------------------
CREATE TABLE cad_references (
    id          BIGSERIAL PRIMARY KEY,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    name        TEXT NOT NULL,
    coordinates JSONB NOT NULL,   -- [{type, x, y, w, h}, ...]
    uploaded_by TEXT
);

-- Sample data
INSERT INTO detection_reports
    (site_name, object_type, confidence, detected_x, detected_y, expected_x, expected_y, offset_inches, status)
VALUES
    ('Site A', 'Pillar', 0.91, 310, 200, 280, 200, 3.2, 'resolved'),
    ('Site A', 'Beam',   0.87, 450, 150, 430, 150, 2.1, 'resolved');
