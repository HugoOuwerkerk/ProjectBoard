from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
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


def row_to_dict(row: sqlite3.Row | None) -> dict:
    return dict(row) if row is not None else {}


def build_projects(rows: list[sqlite3.Row]) -> list[dict]:
    if not rows:
        return []

    project_ids = [row["id"] for row in rows]
    by_id = {
        row["id"]: {
            "id": row["id"],
            "title": row["title"],
            "short_description": row["short_description"],
            "description": row["description"],
            "github": row["github"],
            "website": row["website"],
            "status": row["status"],
            "notes": [],
            "open": [],
            "in_progress": [],
            "done": [],
        }
        for row in rows
    }

    con = get_conn()
    cur = con.cursor()

    q_marks = ",".join("?" for _ in project_ids)
    cur.execute(f"SELECT id, project_id, body FROM note WHERE project_id IN ({q_marks}) ORDER BY id ASC", project_ids)
    for r in cur.fetchall():
        by_id[r["project_id"]]["notes"].append({"id": r["id"], "desc": r["body"]})

    cur.execute(f"SELECT id, project_id, title, desc, status, labels_json FROM task WHERE project_id IN ({q_marks}) ORDER BY id ASC", project_ids)
    for r in cur.fetchall():
        try:
            labels = json.loads(r["labels_json"]) if r["labels_json"] else []
        except (TypeError, json.JSONDecodeError):
            labels = []
        task = {"id": r["id"], "title": r["title"], "desc": r["desc"], "status": r["status"], "labels": labels}
        by_id[r["project_id"]][r["status"]].append(task)

    con.close()
    return [by_id[i] for i in project_ids]



# models
class ProjectCreate(BaseModel):
    title: str
    short_description: str | None = None
    description: str | None = None
    github: str | None = None
    website: str | None = None
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
    return build_projects(rows)



@app.get("/getProject/{project_id}", response_model=ProjectModel)
async def get_project(project_id: int):
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute("SELECT * FROM project WHERE id = ?", (project_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        return build_projects([row])[0]
    finally:
        con.close()



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

    if new_id is None:
        raise HTTPException(status_code=500, detail="Failed to create project")

    return {
        "id": new_id,
        "title": project_data.title,
        "short_description": project_data.short_description,
        "description": project_data.description,
        "github": project_data.github,
        "website": project_data.website,
        "status": project_data.status,
        "notes": [],
        "open": [],
        "in_progress": [],
        "done": [],
    }

@app.patch("/projects/{project_id}", response_model=ProjectModel)
async def edit_project(project_id: int, updates: dict):
    con = get_conn()
    cur = con.cursor()

    cur.execute("SELECT id FROM project WHERE id = ?", (project_id,))
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    title             = updates.get("title")
    short_description = updates.get("short_description")
    description       = updates.get("description")
    github            = updates.get("github")
    website           = updates.get("website")
    status            = updates.get("status")

    if status is not None and status not in {"idea","active","paused","done"}:
        con.close()
        raise HTTPException(status_code=400, detail="Invalid project status")

    cur.execute(
        """
        UPDATE project
           SET title             = COALESCE(?, title),
               short_description = COALESCE(?, short_description),
               description       = COALESCE(?, description),
               github            = COALESCE(?, github),
               website           = COALESCE(?, website),
               status            = COALESCE(?, status)
         WHERE id = ?
        """,
        (title, short_description, description, github, website, status, project_id)
    )
    con.commit()
    con.close()
    # chane in future to return updated fields only
    return await get_project(project_id)


# -------- Tasks --------
@app.post("/projects/{project_id}/tasks", response_model=dict)
async def add_task(project_id: int, task: dict):
    con = get_conn()
    cur = con.cursor()

    cur.execute("SELECT id FROM project WHERE id = ?", (project_id,))
    if cur.fetchone() is None:
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    title = (task.get("title") or "").strip()
    if not title:
        con.close()
        raise HTTPException(status_code=400, detail="Task title cannot be empty")

    desc = task.get("desc")
    status = task.get("status") or "open"
    if status not in {"open", "in_progress", "done"}:
        con.close()
        raise HTTPException(status_code=400, detail="Invalid task status")

    labels = task.get("labels") or []
    try:
        labels_json = json.dumps(labels, ensure_ascii=False)
    except (TypeError, json.JSONDecodeError):
        labels = []
        labels_json = "[]"

    try:
        cur.execute(
            """
            INSERT INTO task (project_id, title, desc, status, labels_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (project_id, title, desc, status, labels_json),
        )
        task_id = cur.lastrowid
        con.commit()
    except sqlite3.IntegrityError as e:
        con.close()
        raise HTTPException(status_code=400, detail=str(e))

    con.close()

    return {
        "id": task_id,
        "title": title,
        "desc": desc,
        "status": status,
        "labels": labels,
    }


@app.delete("/projects/{project_id}/tasks/{task_id}", response_model=dict)
async def delete_task(project_id: int, task_id: int):
    con = get_conn()
    cur = con.cursor()

    cur.execute("SELECT id FROM project WHERE id = ?", (project_id,))
    if cur.fetchone() is None:
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    cur.execute(
        "DELETE FROM task WHERE id = ? AND project_id = ?",
        (task_id, project_id)
    )
    if cur.rowcount == 0:
        con.close()
        raise HTTPException(status_code=404, detail="Task not found")

    con.commit()
    con.close()

    return {"success": True, "deleted_task_id": task_id}


@app.patch("/projects/{project_id}/tasks/{task_id}", response_model=dict)
async def update_task(project_id: int, task_id: int, updates: dict):
    con = get_conn()
    cur = con.cursor()

    cur.execute("SELECT id FROM task WHERE id = ? AND project_id = ?",(task_id, project_id))
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Task not found")

    title  = updates.get("title")
    desc   = updates.get("desc")
    status = updates.get("status")
    labels_json = (
        json.dumps(updates["labels"], ensure_ascii=False)
        if "labels" in updates else None
    )

    try:
        cur.execute(
            """
            UPDATE task
               SET title       = COALESCE(?, title),
                   desc        = COALESCE(?, desc),
                   status      = COALESCE(?, status),
                   labels_json = COALESCE(?, labels_json)
             WHERE id = ? AND project_id = ?
            """,
            (title, desc, status, labels_json, task_id, project_id)
        )
        con.commit()
    except sqlite3.IntegrityError as e:
        con.close()
        raise HTTPException(status_code=400, detail=str(e))

    con.close()

    return {
        "id": task_id,
        "title": updates.get("title"),
        "desc": updates.get("desc"),
        "status": updates.get("status"),
        "labels": updates.get("labels", []),
    }


# -------- Notes --------

@app.post("/projects/{project_id}/notes", response_model=dict)
async def add_note(project_id: int, note: dict):
    body = (note.get("desc") or "").strip()
    if not body:
        raise HTTPException(status_code=400, detail="Note body cannot be empty")

    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT id FROM project WHERE id = ?", (project_id,))
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    cur.execute("INSERT INTO note (project_id, body) VALUES (?, ?)", (project_id, body))
    note_id = cur.lastrowid
    con.commit()
    con.close()
    return {"id": note_id, "desc": body}



@app.patch("/projects/{project_id}/notes/{note_id}", response_model=dict)
async def edit_note(project_id: int, note_id: int, updates: dict):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM note WHERE id = ? AND project_id = ?",
        (note_id, project_id)
    )
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Note not found")

    body = updates.get("desc")

    cur.execute(
        """
        UPDATE note
           SET body = COALESCE(?, body)
         WHERE id = ? AND project_id = ?
        """,
        (body, note_id, project_id)
    )
    con.commit()
    con.close()

    return {"id": note_id, "desc": updates.get("desc")}


@app.delete("/projects/{project_id}/notes/{note_id}", response_model=dict)
async def delete_note(project_id: int, note_id: int):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM note WHERE id = ? AND project_id = ?",
        (note_id, project_id)
    )
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Note not found")

    cur.execute(
        "DELETE FROM note WHERE id = ? AND project_id = ?",
        (note_id, project_id)
    )
    con.commit()
    con.close()

    return {"success": True, "deleted_note_id": note_id}

