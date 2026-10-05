from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from .config import ROOT

DB_PATH = ROOT / "data" / "projects.db"
SCHEMA = {
    "status": "TEXT DEFAULT 'rascunho'",
    "selected_title": "TEXT DEFAULT ''",
    "description": "TEXT DEFAULT ''",
    "thumbnail_path": "TEXT DEFAULT ''",
    "video_path": "TEXT DEFAULT ''",
    "youtube_video_id": "TEXT DEFAULT ''",
    "similarity_score": "REAL DEFAULT 0",
}

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            theme TEXT NOT NULL,
            audience TEXT,
            duration_minutes INTEGER,
            visual_style TEXT,
            ambient TEXT,
            frequency INTEGER,
            package_json TEXT,
            output_dir TEXT
        )
    """)
    cols = {r[1] for r in conn.execute("PRAGMA table_info(projects)").fetchall()}
    for name, ddl in SCHEMA.items():
        if name not in cols:
            conn.execute(f"ALTER TABLE projects ADD COLUMN {name} {ddl}")
    conn.commit()
    return conn

def save_project(meta: dict, package: dict, output_dir: str, status: str = "pacote_gerado", similarity_score: float = 0.0) -> int:
    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO projects
            (created_at, theme, audience, duration_minutes, visual_style, ambient, frequency,
             package_json, output_dir, status, selected_title, description, similarity_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now().isoformat(timespec="seconds"),
                meta.get("theme", ""),
                meta.get("audience", ""),
                int(meta.get("duration_minutes", 60)),
                meta.get("visual_style", ""),
                meta.get("ambient", ""),
                int(meta.get("frequency", 0) or 0),
                json.dumps(package, ensure_ascii=False),
                output_dir,
                status,
                (package.get("titles") or [meta.get("theme", "")])[0],
                package.get("description", ""),
                float(similarity_score or 0),
            ),
        )
        return int(cur.lastrowid)

def update_project(project_id: int, **fields) -> None:
    allowed = {
        "status", "selected_title", "description", "thumbnail_path", "video_path",
        "youtube_video_id", "package_json", "similarity_score"
    }
    clean = {k: v for k, v in fields.items() if k in allowed}
    if not clean:
        return
    set_sql = ", ".join(f"{k} = ?" for k in clean)
    vals = list(clean.values()) + [project_id]
    with connect() as conn:
        conn.execute(f"UPDATE projects SET {set_sql} WHERE id = ?", vals)
        conn.commit()

def get_project(project_id: int) -> dict | None:
    with connect() as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
    return dict(row) if row else None

def recent_projects(limit: int = 12) -> list[dict]:
    with connect() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM projects ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]
