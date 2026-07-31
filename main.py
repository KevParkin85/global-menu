import sqlite3
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Simple store for active session user
current_session = {"username": "User", "dietary_requirements": ""}

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

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/token")
@app.post("/api/login")
async def login(request: Request):
    form_data = await request.form()
    username = form_data.get("username")
    
    if not username:
        try:
            body = await request.json()
            username = body.get("username")
        except:
            username = "User"

    if username:
        current_session["username"] = username

    return {
        "access_token": "mock_token", 
        "token_type": "bearer", 
        "username": current_session["username"],
        "user": current_session["username"]
    }

@app.get("/api/user-data")
def get_user_data():
    return {
        "username": current_session["username"],
        "user": current_session["username"],
        "dietary_requirements": current_session["dietary_requirements"]
    }

@app.get("/dishes")
@app.get("/api/dishes")
def get_dishes():
    conn = sqlite3.connect('dishes.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dishes")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/ingredients")
@app.get("/api/ingredients")
@app.get("/api/get-ingredients")
def get_ingredients():
    return [
        # Meat & Poultry
        {"category": "meat_poultry", "name": "Chicken"},
        {"category": "meat_poultry", "name": "Beef"},
        {"category": "meat_poultry", "name": "Pork"},
        {"category": "meat_poultry", "name": "Lamb"},
        {"category": "meat_poultry", "name": "Turkey"},
        {"category": "meat_poultry", "name": "Duck"},
        {"category": "meat_poultry", "name": "Bacon"},
        {"category": "meat_poultry", "name": "Sausage"},
        {"category": "meat_poultry", "name": "Ham"},
        {"category": "meat_poultry", "name": "Venison"},
        {"category": "meat_poultry", "name": "Chorizo"},
        {"category": "meat_poultry", "name": "Pepperoni"},
        
        # Fish & Seafood
        {"category": "fish_seafood", "name": "Salmon"},
        {"category": "fish_seafood", "name": "Cod"},
        {"category": "fish_seafood", "name": "Shrimp"},
        {"category": "fish_seafood", "name": "Tuna"},
        {"category": "fish_seafood", "name": "Crab"},
        {"category": "fish_seafood", "name": "Lobster"},
        {"category": "fish_seafood", "name": "Sardines"},
        {"category": "fish_seafood", "name": "Mackerel"},
        {"category": "fish_seafood", "name": "Scallops"},
        {"category": "fish_seafood", "name": "Mussels"},
        {"category": "fish_seafood", "name": "Squid"},
        {"category": "fish_seafood", "name": "Octopus"},
        
        # Vegetables & Legumes
        {"category": "vegetables_legumes", "name": "Tomato"},
        {"category": "vegetables_legumes", "name": "Onion"},
        {"category": "vegetables_legumes", "name": "Garlic"},
        {"category": "vegetables_legumes", "name": "Spinach"},
        {"category": "vegetables_legumes", "name": "Potato"},
        {"category": "vegetables_legumes", "name": "Carrot"},
        {"category": "vegetables_legumes", "name": "Broccoli"},
        {"category": "vegetables_legumes", "name": "Bell Pepper"},
        {"category": "vegetables_legumes", "name": "Zucchini"},
        {"category": "vegetables_legumes", "name": "Mushrooms"},
        {"category": "vegetables_legumes", "name": "Chickpeas"},
        {"category": "vegetables_legumes", "name": "Lentils"},
        {"category": "vegetables_legumes", "name": "Black Beans"},
        {"category": "vegetables_legumes", "name": "Kidney Beans"},
        {"category": "vegetables_legumes", "name": "Green Peas"},
        {"category": "vegetables_legumes", "name": "Cabbage"},
        
        # Pantry, Grains & Dairy
        {"category": "pantry_grains_dairy", "name": "Rice"},
        {"category": "pantry_grains_dairy", "name": "Flour"},
        {"category": "pantry_grains_dairy", "name": "Milk"},
        {"category": "pantry_grains_dairy", "name": "Cheese"},
        {"category": "pantry_grains_dairy", "name": "Butter"},
        {"category": "pantry_grains_dairy", "name": "Pasta"},
        {"category": "pantry_grains_dairy", "name": "Bread"},
        {"category": "pantry_grains_dairy", "name": "Oats"},
        {"category": "pantry_grains_dairy", "name": "Cheddar"},
        {"category": "pantry_grains_dairy", "name": "Mozzarella"},
        {"category": "pantry_grains_dairy", "name": "Yogurt"},
        {"category": "pantry_grains_dairy", "name": "Eggs"},
        {"category": "pantry_grains_dairy", "name": "Quinoa"},
        {"category": "pantry_grains_dairy", "name": "Couscous"},
        {"category": "pantry_grains_dairy", "name": "Parmesan"},
        
        # Sauces, Herbs & Spices
        {"category": "sauces_herbs_spices", "name": "Soy Sauce"},
        {"category": "sauces_herbs_spices", "name": "Olive Oil"},
        {"category": "sauces_herbs_spices", "name": "Basil"},
        {"category": "sauces_herbs_spices", "name": "Cumin"},
        {"category": "sauces_herbs_spices", "name": "Black Pepper"},
        {"category": "sauces_herbs_spices", "name": "Sea Salt"},
        {"category": "sauces_herbs_spices", "name": "Oregano"},
        {"category": "sauces_herbs_spices", "name": "Thyme"},
        {"category": "sauces_herbs_spices", "name": "Paprika"},
        {"category": "sauces_herbs_spices", "name": "Chili Powder"},
        {"category": "sauces_herbs_spices", "name": "Ginger"},
        {"category": "sauces_herbs_spices", "name": "Fish Sauce"},
        {"category": "sauces_herbs_spices", "name": "Sesame Oil"},
        {"category": "sauces_herbs_spices", "name": "Curry Powder"},
        {"category": "sauces_herbs_spices", "name": "Sriracha"}
    ]

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