from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional
import sqlite3
import json


# DB
def get_conn():
    con = sqlite3.connect("projects.db")
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    return con


def init_db():
    con = get_conn()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS project (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        title             TEXT NOT NULL,
        short_description TEXT,
        description       TEXT,
        github            TEXT,
        website           TEXT,
        status            TEXT NOT NULL CHECK(status IN ('idea','active','paused','done'))
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS task (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id  INTEGER NOT NULL,
        title       TEXT NOT NULL,
        desc        TEXT,
        status      TEXT NOT NULL CHECK(status IN ('open','in_progress','done')) DEFAULT 'open',
        labels_json TEXT NOT NULL DEFAULT '[]',
        FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS note (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id  INTEGER NOT NULL,
        body        TEXT NOT NULL,
        FOREIGN KEY (project_id) REFERENCES project(id) ON DELETE CASCADE
    )
    """)
    con.commit()
    con.close()

def row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row) if row is not None else {}

def build_project_dict(project_row: sqlite3.Row) -> dict:
    if project_row is None:
        return {}

    project = {
        "id": project_row["id"],
        "title": project_row["title"],
        "short_description": project_row["short_description"],
        "description": project_row["description"],
        "github": project_row["github"],
        "website": project_row["website"],
        "status": project_row["status"],
        "notes": [],
        "open": [],
        "in_progress": [],
        "done": [],
    }

    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id, body FROM note WHERE project_id = ? ORDER BY id ASC",
        (project["id"],)
    )
    project["notes"] = [
        {"id": row["id"], "desc": row["body"]}
        for row in cur.fetchall()
    ]

    cur.execute(
        "SELECT id, title, desc, status, labels_json FROM task WHERE project_id = ? ORDER BY id ASC",
        (project["id"],)
    )
    for row in cur.fetchall():
        try:
            labels = json.loads(row["labels_json"]) if row["labels_json"] else []
        except Exception:
            labels = []
        task = {
            "id": row["id"],
            "title": row["title"],
            "desc": row["desc"],
            "status": row["status"],
            "labels": labels,
        }
        project[row["status"]].append(task)

    con.close()
    return project

# models
class ProjectCreate(BaseModel):
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    status: Literal["idea", "active", "paused", "done"]

class ProjectModel(BaseModel):
    id: int
    title: str
    short_description: str | None
    description: str | None
    github: str | None
    website: str | None
    status: Literal["idea", "active", "paused", "done"]
    notes: list[dict]
    open: list[dict]
    in_progress: list[dict]
    done: list[dict]


# FastAPI app
app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def read_root():
    return {"Hello": "World"}


# -------- Projects --------
@app.get("/getProjects", response_model=list[ProjectModel])
async def get_projects():
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT * FROM project ORDER BY id ASC")
    rows = cur.fetchall()
    con.close()

    projects = [build_project_dict(row) for row in rows]
    return projects

@app.get("/getProject/{project_id}", response_model=ProjectModel)
async def get_project(project_id: int):
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT * FROM project WHERE id = ?", (project_id,))
    row = cur.fetchone()
    con.close()

    if not row:
        raise HTTPException(status_code=404, detail="Project not found")
    return build_project_dict(row)

@app.post("/addProject/", response_model=ProjectModel)
async def add_project(project_data: ProjectCreate):
    con = get_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO project (title, short_description, description, github, website, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            project_data.title,
            project_data.short_description,
            project_data.description,
            project_data.github,
            project_data.website,
            project_data.status,
        ),
    )
    new_id = cur.lastrowid
    con.commit()
    con.close()

    return await get_project(new_id)

@app.patch("/projects/{project_id}", response_model=ProjectModel)
async def edit_project(project_id: int, updates: dict):
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT * FROM project WHERE id = ?", (project_id,))
    row = cur.fetchone()
    if not row:
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    allowed = {"title", "short_description", "description", "github", "website", "status"}
    sets = []
    params = []
    for key, value in updates.items():
        if key in allowed:
            sets.append(f"{key} = ?")
            params.append(value)

    if sets:
        params.append(project_id)
        sql = f"UPDATE project SET {', '.join(sets)} WHERE id = ?"
        cur.execute(sql, tuple(params))
        con.commit()

    con.close()
    return await get_project(project_id)


# -------- Tasks --------
@app.post("/projects/{project_id}/tasks", response_model=ProjectModel)
async def add_task(project_id: int, task: dict):
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT id FROM project WHERE id = ?", (project_id,))
    if cur.fetchone() is None:
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    title = task.get("title").strip()

    desc = task.get("desc")
    status = task.get("status") or "open"
    if status not in ("open", "in_progress", "done"):
        con.close()
        raise HTTPException(status_code=400, detail="Invalid task status")

    labels = task.get("labels") or []
    try:
        labels_json = json.dumps(labels, ensure_ascii=False)
    except Exception:
        labels_json = "[]"

    cur.execute(
        """
        INSERT INTO task (project_id, title, desc, status, labels_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (project_id, title, desc, status, labels_json),
    )
    con.commit()
    con.close()

    return await get_project(project_id)

@app.delete("/projects/{project_id}/tasks/{task_id}", response_model=ProjectModel)
async def delete_task(project_id: int, task_id: int):
    con = get_conn()
    cur = con.cursor()

    cur.execute("SELECT id FROM project WHERE id = ?", (project_id,))
    if cur.fetchone() is None:
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    cur.execute("DELETE FROM task WHERE id = ? AND project_id = ?", (task_id, project_id))
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404, detail="Task not found")

    con.commit()
    con.close()
    return await get_project(project_id)

@app.patch("/projects/{project_id}/tasks/{task_id}", response_model=ProjectModel)
async def update_task(project_id: int, task_id: int, updates: dict):
    con = get_conn()
    cur = con.cursor()

    cur.execute("SELECT id FROM task WHERE id = ? AND project_id = ?", (task_id, project_id))
    if cur.fetchone() is None:
        con.close()
        raise HTTPException(status_code=404, detail="Task not found")

    allowed = {"title", "desc", "status", "labels"}
    sets = []
    params = []

    for key, value in updates.items():
        if key not in allowed:
            continue
        if key == "labels":
            try:
                value = json.dumps(value or [], ensure_ascii=False)
            except Exception:
                value = "[]"
            sets.append("labels_json = ?")
            params.append(value)
        elif key == "status":
            if value not in ("open", "in_progress", "done"):
                con.close()
                raise HTTPException(status_code=400, detail="Invalid task status")
            sets.append("status = ?")
            params.append(value)
        elif key == "title":
            if not (value or "").strip():
                con.close()
                raise HTTPException(status_code=400, detail="Task title cannot be empty")
            sets.append("title = ?")
            params.append(value)
        elif key == "desc":
            sets.append("desc = ?")
            params.append(value)

    if sets:
        params.extend([task_id, project_id])
        sql = f"UPDATE task SET {', '.join(sets)} WHERE id = ? AND project_id = ?"
        cur.execute(sql, tuple(params))
        con.commit()

    con.close()
    return await get_project(project_id)


# -------- Notes --------
@app.get("/projects/{project_id}/notes", response_model=list[dict])
async def get_notes(project_id: int):
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT id, desc FROM note WHERE project_id = ?", (project_id,))
    notes = [{"id": row[0], "desc": row[1]} for row in cur.fetchall()]
    con.close()
    return notes


@app.post("/projects/{project_id}/notes", response_model=dict)
async def add_note(project_id: int, note: dict):
    con = get_conn()
    cur = con.cursor()
    cur.execute("INSERT INTO note (project_id, body) VALUES (?, ?)", (project_id, note.get("desc")))
    con.commit()
    # note_id = cur.lastrowid
    con.close()
    return await get_project(project_id)


@app.patch("/projects/{project_id}/notes/{note_id}", response_model=dict)
async def edit_note(project_id: int, note_id: int, updates: dict):
    con = get_conn()
    cur = con.cursor()
    cur.execute("UPDATE note SET desc = ? WHERE id = ? AND project_id = ?", (updates.get("desc"), note_id, project_id))
    con.commit()
    con.close()
    return {"id": note_id, "desc": updates.get("desc")}


@app.delete("/projects/{project_id}/notes/{note_id}")
async def delete_note(project_id: int, note_id: int):
    con = get_conn()
    cur = con.cursor()
    cur.execute("DELETE FROM note WHERE id = ? AND project_id = ?", (note_id, project_id))
    con.commit()
    con.close()
    return await get_project(project_id)
