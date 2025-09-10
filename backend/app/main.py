from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Example data with task objects (title, desc, labels)
projects = [
    {
        "id": "1",
        "title": "ProjectBoard",
        "short_description": "Personal project hub",
        "description": "Personal project hub with notes and a kanban board.",
        "status": "done",
        "github": "https://github.com/HugoOuwerkerk/ProjectBoard",
        "website": "http://localhost:5173/",
        "notes": ["Add Markdown support", "Consider export feature"],
        "open": [
            {"title": "Fix filter dropdown", "desc": "Dropdown flickers on blur in Chrome.", "labels": ["bug", "ui"]},
            {"title": "Add project form", "desc": "Modal with name + short description.", "labels": ["feature"]}
        ],
        "in_progress": [
            {"title": "Responsive layout", "desc": "Tweak grid gaps < 680px.", "labels": ["ui", "polish"]}
        ],
        "done": [
            {"title": "Landing page design", "desc": "Dark hero + showcase board.", "labels": ["design"]}
        ]
    },
    {
        "id": "2",
        "title": "Journeo",
        "short_description": "Trip planner",
        "description": "Trip planner with budget & preferences.",
        "status": "paused",
        "github": "https://github.com/HugoOuwerkerk/journeo",
        "website": "https://journeo.example.com",
        "notes": ["Integrate routing API"],
        "open": [
            {"title": "Budget slider", "desc": "Range component with currency suffix.", "labels": ["feature", "ui"]},
            {"title": "Date picker", "desc": "Disable past dates; support ranges.", "labels": ["feature"]}
        ],
        "in_progress": [],
        "done": [
            {"title": "Frontend skeleton", "desc": "Routes + base layout created.", "labels": ["setup"]}
        ]
    },
    {
        "id": "3",
        "title": "AutoShortsBot",
        "short_description": "Reddit → Shorts bot",
        "description": "Bot that converts Reddit content into YouTube Shorts.",
        "status": "active",
        "github": "https://github.com/HugoOuwerkerk/auto-shorts-bot",
        "website": None,
        "notes": ["Check TikTok upload API"],
        "open": [
            {"title": "Add watermark", "desc": "Bottom-right, 60% opacity.", "labels": ["feature", "branding"]},
            {"title": "Custom voice", "desc": "TTS voice with SSML support.", "labels": ["research"]}
        ],
        "in_progress": [
            {"title": "Subtitle rendering", "desc": "SRT -> burned-in subs with outline.", "labels": ["video", "ffmpeg"]}
        ],
        "done": []
    },
    {
        "id": "4",
        "title": "Personal CV Website",
        "short_description": "Portfolio site",
        "description": "Portfolio site that showcases all my projects.",
        "status": "active",
        "github": "https://github.com/HugoOuwerkerk/personal-site",
        "website": "https://hugo.dev",
        "notes": ["Add dark mode toggle"],
        "open": [],
        "in_progress": [
            {"title": "Project grid layout", "desc": "Auto-fit cards with equal heights.", "labels": ["ui"]}
        ],
        "done": [
            {"title": "Hero section", "desc": "Intro copy + CTA.", "labels": ["content"]},
            {"title": "Contact form", "desc": "Serverless form handler wired.", "labels": ["feature"]}
        ]
    }
]

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/getProjects")
async def getProjects():
    return projects

@app.get("/getProject/{project_id}")
async def getProject(project_id: str):
    for p in projects:
        if p["id"] == project_id:
            return p
    raise HTTPException(status_code=404, detail="Project not found")

@app.post("/addProject")
async def addProject():
    pass


@app.get("/items/{item_id}")
async def read_item(item_id: int, word: str | None = None):
    return {"item_id": item_id, "word": word}
