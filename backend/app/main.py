from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

voorbeeld = {
    "id" :  "1",
    "titel" :  "test-titel",
    "description" : "test-description",
    "open" : [],
    "in progress": [],
    "done":  []
}

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/getItems")
async def get_items():
    return voorbeeld


@app.get("/items/{item_id}")
async def read_item(item_id: int, word: str | None = None):
    return {"item_id": item_id, "word": word}
