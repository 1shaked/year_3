"""
FastAPI server to serve static files and index.html from the 'static' directory.
"""

from fastapi import FastAPI, Request, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sqlite3
import random
from typing import List, Dict
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Path to the static directory
STATIC_DIR = Path(__file__).parent / "static"
INDEX_FILE = STATIC_DIR / "index.html"

# SQLite database path
DB_PATH = Path(__file__).parent / "questions.db"
from fastapi.responses import FileResponse

if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="assets")# Mount static files if directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(str(INDEX_FILE))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/")
# async def serve_index(request: Request):
#     """
#     Serve the index.html file from the static directory.
#     """
#     if INDEX_FILE.exists():
#         return FileResponse(str(INDEX_FILE))
#     return {"error": "index.html not found"}

@app.get("/api/questions")
def get_random_questions(
    num_questions: int = Query(5, gt=0, le=20),
    topic_id: int = Query(..., description="ID of the topic to filter questions by")
) -> List[Dict]:
    """
    Get a random set of questions and their shuffled options from the database, filtered by topic.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Get all question ids for the given topic
    cursor.execute("SELECT id FROM questions WHERE topic_id = ?", (topic_id,))
    question_ids = [row[0] for row in cursor.fetchall()]
    if len(question_ids) < num_questions:
        num_questions = len(question_ids)
    if not question_ids:
        conn.close()
        return []
    selected_ids = random.sample(question_ids, num_questions)
    questions = []
    for qid in selected_ids:
        cursor.execute("SELECT question FROM questions WHERE id = ?", (qid,))
        question_text = cursor.fetchone()[0]
        cursor.execute("SELECT id, option_text FROM options WHERE question_id = ?", (qid,))
        options = cursor.fetchall()
        # Shuffle options
        random.shuffle(options)
        # Get correct answer option_id
        cursor.execute("SELECT option_id FROM answers WHERE question_id = ?", (qid,))
        correct_option_id = cursor.fetchone()[0]
        # Find the new index of the correct answer after shuffling
        correct_index = next((i for i, (oid, _) in enumerate(options) if oid == correct_option_id), None)
        questions.append({
            "id": qid,
            "question": question_text,
            "options": [opt[1] for opt in options],
            "correct_index": correct_index
        })
    random.shuffle(questions)
    conn.close()
    return questions

@app.get("/api/topics")
def get_topics() -> List[Dict]:
    """
    Get a list of all topics (id and name).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM topics")
    topics = [{"id": row[0], "name": row[1]} for row in cursor.fetchall()]
    conn.close()
    return topics


