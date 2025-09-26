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

## Screenshots

*(add your own later — landing page, project detail, board, etc.)*

---

## Tech Stack

- Frontend: [SvelteKit](https://kit.svelte.dev/) + TypeScript + Vite  
- Backend: [FastAPI](https://fastapi.tiangolo.com/) + SQLite  
- Containerization: Docker & Docker Compose  
- Styling: Custom CSS (dark theme, responsive layout)

---

## Getting Started

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- Git

### Installation

1. Clone this repo:
   git clone https://github.com/yourusername/projectboard.git
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

ProjectBoard/  
├── backend/              # FastAPI app  
│   ├── app/  
│   │   ├── main.py       # API routes + DB setup  
│   │   └── mock_data.json  
│   ├── poetry.lock  
│   └── pyproject.toml  
│  
├── frontend/             # SvelteKit app  
│   ├── src/  
│   │   ├── routes/       # +page.svelte files  
│   │   └── lib/          # components  
│   ├── package.json  
│   └── vite.config.ts  
│  
├── docker-compose.yml    # Multi-container setup  
└── README.md  

---

## Accessing on Other Devices

If you want to open ProjectBoard on your phone (same Wi-Fi as PC):

1. Find your PC IP:  
   hostname -I  
   Example: 192.168.178.106

2. Open on phone:  
   http://192.168.178.106:8080

---

## License

MIT — do whatever you want, but attribution is appreciated.

---

## Future Ideas

- User authentication (multi-user support)  
- Drag & drop task reordering  
- Tags/labels with colors  
- Export/import projects  
- Deployment templates (Fly.io, Railway, etc.)

---

## Author

Made by [Your Name]  
Inspired by the need for a simple, self-hosted project tracker.
