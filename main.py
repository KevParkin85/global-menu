import sqlite3
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS so your frontend can talk to the backend smoothly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def init_db():
    conn = sqlite3.connect('dishes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            country TEXT NOT NULL,
            rating INTEGER,
            difficulty INTEGER,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Dish(BaseModel):
    name: str
    country: str
    rating: int = None
    difficulty: int = None
    notes: str = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the Global Menu API!"}

@app.get("/dishes")
def get_dishes():
    conn = sqlite3.connect('dishes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dishes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/dishes")
def add_dish(dish: Dish):
    conn = sqlite3.connect('dishes.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dishes (name, country, rating, difficulty, notes) VALUES (?, ?, ?, ?, ?)",
        (dish.name, dish.country, dish.rating, dish.difficulty, dish.notes)
    )
    conn.commit()
    conn.close()
    return {"message": "Dish added successfully!"}

@app.get("/dishes/top10")
def get_top_10_dishes():
    conn = sqlite3.connect('dishes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name, country, AVG(rating) as avg_rating, AVG(difficulty) as avg_difficulty 
        FROM dishes 
        WHERE rating IS NOT NULL 
        GROUP BY name, country 
        ORDER BY avg_rating DESC 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/countries/{country_name}/stats")
def get_country_stats(country_name: str):
    conn = sqlite3.connect('dishes.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT AVG(rating), AVG(difficulty), COUNT(*) 
        FROM dishes 
        WHERE LOWER(country) = LOWER(?)
    """, (country_name,))
    row = cursor.fetchone()
    conn.close()
    
    if not row or row[2] == 0:
        return {"avg_rating": 0, "avg_difficulty": 0, "total_dishes": 0}
        
    return {
        "avg_rating": round(row[0], 1) if row[0] else 0,
        "avg_difficulty": round(row[1], 1) if row[1] else 0,
        "total_dishes": row[2]
    }