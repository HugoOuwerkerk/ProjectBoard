# 🚀 ProjectBoard

A personal project hub built with **SvelteKit 5 (frontend)** and **FastAPI (backend)**.  
Manage your projects, notes, and tasks in a clean **kanban-style board** with a modern dark UI.

---

## ✨ Features
- 📂 Project list with title, description & status badge *(active, paused, done)*
- 📑 Project detail pages with notes, GitHub & website links
- 🗂️ Kanban per project *(Open, In Progress, Done)*
- 🌙 Dark, modern UI
- 🔗 Decoupled frontend & backend

---

## 📂 Project Structure
    ProjectBoard/
    ├── backend/                  
    │   ├── main.py               # API endpoints + example data
    │   └── (poetry files)        # pyproject.toml, poetry.lock
    ├── frontend/                 
    │   ├── src/
    │   │   └── routes/
    │   │       ├── +page.svelte              # Landing page (all projects)
    │   │       └── project/[id]/+page.svelte # Project detail page
    │   └── package.json
    └── README.md

---

## ⚙️ Backend (FastAPI)

**Install:**
    cd backend
    poetry install

**Run:**
    poetry run uvicorn main:app --reload --port 8000

CORS is enabled for:
- http://localhost:5173
- http://127.0.0.1:5173

**Endpoints:**
- GET /getProjects → list all projects  
- GET /getProject/{id} → get a single project by ID  
- POST /addProject → placeholder for future create  

**Example project object (JSON):**
    {
      "id": "1",
      "title": "ProjectBoard",
      "short_description": "Personal project hub",
      "description": "Hub with notes and a kanban board.",
      "status": "active",
      "github": "https://github.com/HugoOuwerkerk/ProjectBoard",
      "website": "http://localhost:5173/",
      "notes": ["Add Markdown support"],
      "open": [{ "title": "Fix filter dropdown", "desc": "Bug in Chrome", "labels": ["bug"] }],
      "in_progress": [],
      "done": []
    }

---

## 🎨 Frontend (SvelteKit 5)

**Install:**
    cd frontend
    npm install

**Run:**
    npm run dev

Local dev URL:  
👉 http://127.0.0.1:5173

---

## 🛠️ Development Notes
- Frontend fetches the backend directly (**no .env needed** in dev)
- CORS is preconfigured in the backend for the Svelte dev server
- Tasks support **title**, **description**, and **labels**

---

## 🗺️ Roadmap
- [ ] Create new projects from the UI (wire POST /addProject)
- [ ] Inline edit tasks on the kanban board
- [ ] Persist data in a database (SQLite/Postgres) instead of an in-memory list
- [ ] Authentication / multi-user support

---
