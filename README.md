# ProjectBoard

A minimal self-hosted project manager to organize projects, tasks, and notes in one place.  
Built with SvelteKit (frontend) and FastAPI (backend), running in Docker.

---

## Features

- Create and manage projects with title, description, status, GitHub/website links
- Add and edit tasks in a simple kanban board (Open / In Progress / Done)
- Add notes to each project for quick ideas or documentation
- Simple search & filter on the landing page
- Clean, dark UI with responsive design
- Fully self-hosted with Docker Compose

---

## Tech Stack

- Frontend: [SvelteKit](https://kit.svelte.dev/) + TypeScript + Vite  
- Backend: [FastAPI](https://fastapi.tiangolo.com/) + SQLite  
- Containerization: Docker & Docker Compose  
- Styling: Custom CSS (dark theme, responsive layout)

---

## Getting Started

### Installation

1. Clone this repo:
   git clone https://github.com/HugoOuwerkerk/ProjectBoard.git
   cd projectboard

2. Build and start the containers:
   docker compose up -d

3. Open in browser:
   http://localhost:8080

---

## Development

### Frontend
cd frontend  
npm install  
npm run dev  
Runs on http://localhost:5173

### Backend
cd backend  
poetry install  
poetry run uvicorn app.main:app --reload  
Runs on http://localhost:8000

---

## API Endpoints (Backend)

- GET /getProjects → List all projects  
- GET /getProject/{id} → Get project by ID  
- POST /addProject/ → Add a new project  
- PATCH /projects/{id} → Update a project  
- DELETE /projects/{id} → Delete a project  

- POST /projects/{id}/tasks → Add a task  
- PATCH /projects/{id}/tasks/{taskId} → Update a task  
- DELETE /projects/{id}/tasks/{taskId} → Delete a task  

- POST /projects/{id}/notes → Add a note  
- PATCH /projects/{id}/notes/{noteId} → Update a note  
- DELETE /projects/{id}/notes/{noteId} → Delete a note  

---

## Project Structure

ProjectBoard
├── backend
│   ├── app
│   │   └── main.py
│   ├── Dockerfile
│   ├── poetry.lock
│   ├── projects.db
│   └── pyproject.toml
├── docker-compose.yml
├── frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── package-lock.json
│   ├── src
│   │   ├── app.d.ts
│   │   ├── app.html
│   │   ├── lib
│   │   │   ├── assets
│   │   │   │   ├── favicon.png
│   │   │   │   └── logo.png
│   │   │   ├── components
│   │   │   │   └── Modal.svelte
│   │   │   ├── index.ts
│   │   │   └── style.css
│   │   └── routes
│   │       ├── +layout.svelte
│   │       ├── +page.svelte
│   │       └── project
│   │           └── [id]
│   │               ├── +layout.svelte
│   │               └── +page.svelte
│   ├── static
│   │   └── robots.txt
│   ├── svelte.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── package.json
├── package-lock.json
└── README.md

---

## License

MIT — do whatever you want, but attribution is appreciated.

---

## Future Ideas

- User authentication (multi-user support)  
- Tags/labels with colors  
- Export/import projects  
---

## Author

Made by Hugo Ouwerkerk
Inspired by the need for a simple, self-hosted project tracker.
