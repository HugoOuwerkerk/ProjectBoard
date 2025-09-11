from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _normalize_labels(labels):
    """
    Accepts:
      - None
      - ["bug", "ui"]
      - [{"name":"bug"}, {"id": 2, "name":"ui"}]
    Returns a list of dicts: [{"id": 1, "name": "bug"}, ...]
    (ids are local within the task payload)
    """
    if not labels:
        return []
    out = []
    for i, item in enumerate(labels, start=1):
        if isinstance(item, str):
            out.append({"id": i, "name": item})
        elif isinstance(item, dict):
            name = item.get("name") or ""
            out.append({"id": i, "name": name})
        else:
            out.append({"id": i, "name": str(item)})
    return out

class ProjectCreate(BaseModel):
    title: str
    short_description: Optional[str] = None
    description: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None
    status: Literal["idea", "active",  "in_progress", "done"]

class Project(BaseModel):
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


with open("app/mock_data.json", "r", encoding="utf-8") as f:
    raw_projects = json.load(f)

projects = [Project(**p) for p in raw_projects]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/getProjects")
async def getProjects():
    return projects

@app.get("/getProject/{project_id}", response_model=Project)
async def getProject(project_id: int):
    for project in projects:
        if project.id == project_id:
            return project
    raise HTTPException(status_code=404, detail="Project not found")

@app.post("/addProject/", response_model=Project)
async def addProject(project_data: ProjectCreate):
    new_id = len(projects) + 1

    new_project = Project(
        id=new_id,
        title=project_data.title,
        short_description=project_data.short_description,
        description=project_data.description,
        github=project_data.github,
        website=project_data.website,
        status=project_data.status,
        notes=[],
        open=[],
        in_progress=[],
        done=[],
    )

    projects.append(new_project)
    return new_project

@app.patch("/projects/{project_id}", response_model=Project)
async def edit_project(project_id: int, updates: dict):
    pass

@app.post("/projects/{project_id}/tasks", response_model=Project)
async def add_task(project_id: int, task: dict):
    for project in projects:
        if project.id == project_id:
            new_id = max(
                [t["id"] for t in (project.open + project.in_progress + project.done)] or [0]
            ) + 1
            task["id"] = new_id

            task["labels"] = _normalize_labels(task.get("labels"))

            project.open.append(task)
            return project

    raise HTTPException(status_code=404, detail="Project not found")


@app.delete("/projects/{project_id}/tasks/{task_id}", response_model=Project)
async def delete_task(project_id: int, task_id: int):
    for project in projects:
        if project.id == project_id:
            for task_list in [project.open, project.in_progress, project.done]:
                for task in task_list:
                    if task["id"] == task_id:
                        task_list.remove(task)
                        return project
            raise HTTPException(status_code=404, detail="Task not found")

    raise HTTPException(status_code=404, detail="Project not found")

@app.patch("/projects/{project_id}/tasks/{task_id}", response_model=Project)
async def update_task(project_id: int, task_id: int, updates: dict):
    for project in projects:
        if project.id == project_id:
            for task_list in [project.open, project.in_progress, project.done]:
                for task in task_list:
                    if task["id"] == task_id:
                        for key, value in updates.items():
                            if key == "labels":
                                task["labels"] = _normalize_labels(value)
                            elif key in task:
                                task[key] = value
                        return project

            raise HTTPException(status_code=404, detail="Task not found")

    raise HTTPException(status_code=404, detail="Project not found")

