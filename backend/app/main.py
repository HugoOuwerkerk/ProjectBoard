from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal
import sqlite3
import json
import os
import base64
import hashlib
import secrets
from datetime import datetime, timedelta
import re


# DB
def get_conn():
    db_path = os.getenv("DB_PATH", "projects.db")
    con = sqlite3.connect(db_path)
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
        status            TEXT NOT NULL CHECK(status IN ('idea','active','paused','done')),
        user_id           INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
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
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS session (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        expires_at TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
    )
    """)
    con.commit()
    ensure_default_user(con)
    ensure_project_user_column(con)
    con.close()


SESSION_COOKIE = "pb_session"
SESSION_DURATION = timedelta(days=7)


def ensure_default_user(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM user")
    (count,) = cur.fetchone() or (0,)
    if count:
        return

    username = os.getenv("DEFAULT_ADMIN_USER")
    password = os.getenv("DEFAULT_ADMIN_PASSWORD")
    password_hash = hash_password(password)
    cur.execute(
        "INSERT INTO user (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    con.commit()


def ensure_project_user_column(con: sqlite3.Connection) -> None:
    cur = con.cursor()
    cur.execute("PRAGMA table_info(project)")
    columns = {row[1] for row in cur.fetchall()}
    if "user_id" in columns:
        return

    cur.execute("ALTER TABLE project ADD COLUMN user_id INTEGER")
    cur.execute("UPDATE project SET user_id = 1 WHERE user_id IS NULL")
    con.commit()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    payload = salt + derived
    return base64.urlsafe_b64encode(payload).decode()


def verify_password(password: str, encoded: str) -> bool:
    try:
        payload = base64.urlsafe_b64decode(encoded.encode())
    except (ValueError, TypeError):
        return False

    salt, stored = payload[:16], payload[16:]
    try:
        derived = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    except ValueError:
        return False
    return secrets.compare_digest(stored, derived)


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def upsert_session(con: sqlite3.Connection, user_id: int) -> tuple[str, datetime]:
    token = new_session_token()
    now = datetime.utcnow()
    expires = now + SESSION_DURATION
    cur = con.cursor()
    cur.execute(
        "INSERT INTO session (token, user_id, expires_at, created_at) VALUES (?, ?, ?, ?)",
        (token, user_id, expires.isoformat(), now.isoformat()),
    )
    con.commit()
    return token, expires


def get_user_by_session(token: str | None) -> dict | None:
    if not token:
        return None

    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute(
            """
            SELECT user.id, user.username, session.expires_at
            FROM session
            JOIN user ON user.id = session.user_id
            WHERE session.token = ?
            """,
            (token,),
        )
        row = cur.fetchone()
        if not row:
            return None
        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at < datetime.utcnow():
            cur.execute("DELETE FROM session WHERE token = ?", (token,))
            con.commit()
            return None
        return {"id": row["id"], "username": row["username"]}
    finally:
        con.close()


def require_user(request: Request) -> dict:
    user = get_user_by_session(request.cookies.get(SESSION_COOKIE))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


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
    # user_id intentionally hidden from API responses


class UserModel(BaseModel):
    id: int
    username: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user: UserModel


class SignupRequest(BaseModel):
    username: str
    password: str


PASSWORD_SPECIALS = set("!@#$%^&*()-_=+[]{}|;:'\",.<>/?`~")


def validate_password_policy(password: str) -> list[str]:
    errors: list[str] = []

    if len(password) < 10:
        errors.append("Password must be at least 10 characters long")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least one digit")

    if not any(char in PASSWORD_SPECIALS for char in password):
        errors.append("Password must contain at least one special character")

    return errors


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
async def get_projects(user: dict = Depends(require_user)):
    con = get_conn()
    cur = con.cursor()
    cur.execute("SELECT * FROM project WHERE user_id = ? ORDER BY id ASC", (user["id"],))
    rows = cur.fetchall()
    con.close()
    return build_projects(rows)



@app.get("/getProject/{project_id}", response_model=ProjectModel)
async def get_project(project_id: int, user: dict = Depends(require_user)):
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT * FROM project WHERE id = ? AND user_id = ?",
            (project_id, user["id"]),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Project not found")
        return build_projects([row])[0]
    finally:
        con.close()



@app.post("/addProject/", response_model=ProjectModel)
async def add_project(
    project_data: ProjectCreate,
    user: dict = Depends(require_user),
):
    con = get_conn()
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO project (title, short_description, description, github, website, status, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_data.title,
            project_data.short_description,
            project_data.description,
            project_data.github,
            project_data.website,
            project_data.status,
            user["id"],
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


@app.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, response: Response):
    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute(
            "SELECT id, password_hash FROM user WHERE username = ?",
            (data.username,),
        )
        row = cur.fetchone()
        if not row or not verify_password(data.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token, expires = upsert_session(con, row["id"])
        response.set_cookie(
            SESSION_COOKIE,
            token,
            httponly=True,
            max_age=int(SESSION_DURATION.total_seconds()),
            expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            samesite="lax",
            secure=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
            path="/",
        )
        return {"user": {"id": row["id"], "username": data.username}}
    finally:
        con.close()


@app.post("/signup", response_model=LoginResponse)
async def signup(data: SignupRequest, response: Response):
    username = data.username.strip()
    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long")

    password_errors = validate_password_policy(data.password)
    if password_errors:
        raise HTTPException(status_code=400, detail=password_errors)

    con = get_conn()
    try:
        cur = con.cursor()
        cur.execute("SELECT 1 FROM user WHERE username = ?", (username,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="Username already taken")

        password_hash = hash_password(data.password)
        try:
            cur.execute(
                "INSERT INTO user (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Username already taken")

        user_id = cur.lastrowid
        con.commit()

        token, expires = upsert_session(con, user_id)
        response.set_cookie(
            SESSION_COOKIE,
            token,
            httponly=True,
            max_age=int(SESSION_DURATION.total_seconds()),
            expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            samesite="lax",
            secure=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
            path="/",
        )

        return {"user": {"id": user_id, "username": username}}
    finally:
        con.close()


@app.post("/logout")
async def logout(request: Request, response: Response):
    token = request.cookies.get(SESSION_COOKIE)
    if token:
        con = get_conn()
        try:
            cur = con.cursor()
            cur.execute("DELETE FROM session WHERE token = ?", (token,))
            con.commit()
        finally:
            con.close()

    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}


@app.get("/me", response_model=UserModel)
async def get_me(user: dict = Depends(require_user)):
    return user

@app.patch("/projects/{project_id}", response_model=ProjectModel)
async def edit_project(
    project_id: int,
    updates: dict,
    user: dict = Depends(require_user),
):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM project WHERE id = ? AND user_id = ?",
        (project_id, user["id"]),
    )
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
    return await get_project(project_id, user)


# -------- Tasks --------
@app.post("/projects/{project_id}/tasks", response_model=dict)
async def add_task(project_id: int, task: dict, user: dict = Depends(require_user)):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM project WHERE id = ? AND user_id = ?",
        (project_id, user["id"]),
    )
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
async def delete_task(
    project_id: int,
    task_id: int,
    user: dict = Depends(require_user),
):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM project WHERE id = ? AND user_id = ?",
        (project_id, user["id"]),
    )
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
async def update_task(
    project_id: int,
    task_id: int,
    updates: dict,
    user: dict = Depends(require_user),
):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM project WHERE id = ? AND user_id = ?",
        (project_id, user["id"]),
    )
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    cur.execute(
        "SELECT 1 FROM task WHERE id = ? AND project_id = ?",
        (task_id, project_id)
    )
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
        
        cur.execute(
            "SELECT id, title, desc, status, labels_json FROM task WHERE id = ? AND project_id = ?",
            (task_id, project_id)
        )
        row = cur.fetchone()
        if not row:
            con.close()
            raise HTTPException(status_code=500, detail="Row missing after update")

    except sqlite3.IntegrityError as e:
        con.close()
        raise HTTPException(status_code=400, detail=str(e))

    con.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "desc": row["desc"],
        "status": row["status"],
        "labels": json.loads(row["labels_json"] or "[]"),
    }


@app.delete("/projects/{project_id}", response_model=dict)
async def delete_project(project_id: int, user: dict = Depends(require_user)):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM project WHERE id = ? AND user_id = ?",
        (project_id, user["id"]),
    )
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    cur.execute("DELETE FROM project WHERE id = ?", (project_id,))
    con.commit()
    con.close()

    return {"success": True, "deleted_project_id": project_id}

# -------- Notes --------

@app.post("/projects/{project_id}/notes", response_model=dict)
async def add_note(
    project_id: int,
    note: dict,
    user: dict = Depends(require_user),
):
    body = (note.get("desc") or "").strip()
    if not body:
        raise HTTPException(status_code=400, detail="Note body cannot be empty")

    con = get_conn()
    cur = con.cursor()
    cur.execute(
        "SELECT id FROM project WHERE id = ? AND user_id = ?",
        (project_id, user["id"]),
    )
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

    cur.execute("INSERT INTO note (project_id, body) VALUES (?, ?)", (project_id, body))
    note_id = cur.lastrowid
    con.commit()
    con.close()
    return {"id": note_id, "desc": body}



@app.patch("/projects/{project_id}/notes/{note_id}", response_model=dict)
async def edit_note(
    project_id: int,
    note_id: int,
    updates: dict,
    user: dict = Depends(require_user),
):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM project WHERE id = ? AND user_id = ?",
        (project_id, user["id"]),
    )
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

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
async def delete_note(
    project_id: int,
    note_id: int,
    user: dict = Depends(require_user),
):
    con = get_conn()
    cur = con.cursor()

    cur.execute(
        "SELECT id FROM project WHERE id = ? AND user_id = ?",
        (project_id, user["id"]),
    )
    if not cur.fetchone():
        con.close()
        raise HTTPException(status_code=404, detail="Project not found")

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
