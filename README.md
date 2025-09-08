# Svelte + FastAPI Template

A minimal full-stack starter template with a **SvelteKit 5 frontend** and a **FastAPI backend**.  
No `.env` files needed — the frontend just fetches directly from the backend.

---

## Project Structure

```
svelte-fastapi-template/
├── backend/             # FastAPI backend
│   ├── app/
│   │   └── main.py      
│   ├── poetry.lock
│   └── pyproject.toml
├── frontend/            # SvelteKit frontend
│   ├── src/
│   │   └── routes/+page.svelte
│   ├── package.json
└── README.md
```

---

## Backend (FastAPI)

### Install dependencies
```bash
cd backend
poetry install
```

### Run the backend
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

### API endpoints
- `GET /` → returns:
  ```json
  { "Hello": "World" }
  ```
- `GET /items/{item_id}?word=hello` → returns:
  ```json
  {
    "item_id": 42,
    "word": "hello"
  }
  ```

## Frontend (SvelteKit 5)

### Install dependencies
```bash
cd frontend
npm install
```

### Run the frontend
```bash
npm run dev
```

Frontend runs at:  
[http://127.0.0.1:5173]


---

## Development Notes

- Backend CORS is configured to allow requests from the Svelte dev server (`localhost:5173`).
- No `.env` is used — the API URL is written directly in the frontend.
