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

    notes: list[str]
    open: list[dict]         # or better: list[Task]
    in_progress: list[dict]  # or better: list[Task]
    done: list[dict]         # or better: list[Task]


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
    for p in projects:
        if p.id == project_id:
            return p
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


@app.get("/items/{item_id}")
async def read_item(item_id: int, word: str | None = None):
    return {"item_id": item_id, "word": word}
