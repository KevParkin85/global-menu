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
def get_ingredients():
    return {
        "meat_poultry": [
            "Chicken", "Beef", "Pork", "Lamb", "Turkey", "Duck", "Bacon", "Sausage", 
            "Ham", "Venison", "Veal", "Goat", "Prosciutto", "Chorizo", "Pepperoni", 
            "Salami", "Pancetta", "Quail", "Rabbit", "Bison", "Liver", "Kidney"
        ],
        "fish_seafood": [
            "Salmon", "Cod", "Shrimp", "Tuna", "Crab", "Lobster", "Sardines", "Mackerel", 
            "Trout", "Scallops", "Mussels", "Squid", "Octopus", "Anchovies", "Clams", 
            "Oysters", "Haddock", "Halibut", "Sea Bass", "Snapper", "Crayfish", "Herring"
        ],
        "vegetables_legumes": [
            "Tomato", "Onion", "Garlic", "Spinach", "Potato", "Carrot", "Broccoli", 
            "Bell Pepper", "Zucchini", "Mushrooms", "Chickpeas", "Lentils", "Black Beans", 
            "Kidney Beans", "Green Peas", "Cabbage", "Cauliflower", "Cucumber", "Lettuce", 
            "Celery", "Sweet Potato", "Eggplant", "Asparagus", "Artichoke", "Kale", 
            "Pumpkin", "Butternut Squash", "Beetroot", "Radish", "Leek", "Scallion", 
            "Bok Choy", "Edamame", "Cannellini Beans", "Pinto Beans", "Split Peas"
        ],
        "pantry_grains_dairy": [
            "Rice", "Flour", "Milk", "Cheese", "Butter", "Pasta", "Bread", "Oats", 
            "Cheddar", "Mozzarella", "Yogurt", "Heavy Cream", "Eggs", "Quinoa", "Couscous", 
            "Parmesan", "Feta", "Ricotta", "Gouda", "Brie", "Paneer", "Halloumi", 
            "Sour Cream", "Cream Cheese", "Tortillas", "Noodles", "Polenta", "Bulgur", 
            "Barley", "Olive Oil", "Vegetable Oil", "Coconut Milk", "Honey", "Maple Syrup", 
            "Sugar", "Baking Powder", "Yeast", "Soy Sauce", "Vinegar", "Tomato Paste"
        ],
        "sauces_herbs_spices": [
            "Soy Sauce", "Olive Oil", "Basil", "Cumin", "Black Pepper", "Sea Salt", 
            "Oregano", "Thyme", "Paprika", "Chili Powder", "Ginger", "Rice Vinegar", 
            "Fish Sauce", "Sesame Oil", "Rosermary", "Sage", "Dill", "Coriander", 
            "Cayenne Pepper", "Turmeric", "Cinnamon", "Nutmeg", "Cloves", "Cardamom", 
            "Star Anise", "Curry Powder", "Garam Masala", "Hot Sauce", "Worcestershire Sauce", 
            "Dijon Mustard", "Whole Grain Mustard", "Mayonnaise", "Ketchup", "Sriracha", 
            "Hoisin Sauce", "Oyster Sauce", "Tahin", "Miso Paste", "Gochujang"
        ]
    }

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