from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import sqlite3
import hashlib
import secrets

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db_connection():
    conn = sqlite3.connect("dishes.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            iso TEXT,
            name TEXT,
            ingredients TEXT,
            method TEXT,
            wiki TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT,
            salt TEXT,
            dietary_requirements TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_dishes (
            user_id INTEGER,
            iso TEXT,
            status TEXT,
            taste_rating INTEGER,
            chef_rating INTEGER,
            PRIMARY KEY (user_id, iso)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM dishes")
    if cursor.fetchone()[0] == 0:
        sample_dishes = [
            ("ITA", "Pizza Margherita", "flour, water, yeast, tomatoes, cheese, basil", "Mix ingredients, bake.", "https://en.wikipedia.org/wiki/Pizza_Margherita"),
            ("GBR", "Fish and chips", "fish, potatoes, batter, oil, salt, vinegar", "Deep fry battered fish and potato chips until golden and crisp.", "https://en.wikipedia.org/wiki/Fish_and_chips"),
            ("FRA", "Pot-au-feu", "beef, carrots, leeks, turnips, potatoes, bouquet garni", "Simmer meat and vegetables slowly in broth until tender.", "https://en.wikipedia.org/wiki/Pot-au-feu"),
            ("ESP", "Tortilla de patatas", "potatoes, eggs, olive oil, onion, salt", "Fry sliced potatoes and onions in oil, mix with beaten eggs, and cook into a thick omelette.", "https://en.wikipedia.org/wiki/Spanish_omelette"),
            ("DEU", "Sauerbraten", "beef, vinegar, water, spices, onions, flour", "Marinate beef in a vinegar mixture for days, then roast and serve with a thick gravy.", "https://en.wikipedia.org/wiki/Sauerbraten"),
            ("IRL", "Irish stew", "lamb, potatoes, onions, parsley, water", "Slow-cook lamb chops with potatoes and onions in a covered pot.", "https://en.wikipedia.org/wiki/Irish_stew"),
            ("NLD", "Stamppot", "potatoes, kale, sausage, butter, milk", "Mash boiled potatoes and kale together, serve with smoked sausage.", "https://en.wikipedia.org/wiki/Stamppot"),
            ("BEL", "Carbonnade flamande", "beef, onions, beer, mustard, bread, butter", "Braize beef slowly in dark Belgian beer with seasoned bread.", "https://en.wikipedia.org/wiki/Carbonnade_flamande"),
            ("PRT", "Bacalhau à Brás", "salt cod, onions, potatoes, eggs, black olives", "Shred desalted cod, sauté with thin potato matchsticks and onions, and bind with beaten eggs.", "https://en.wikipedia.org/wiki/Bacalhau_%C3%A0_Br%C3%A1s"),
            ("CHE", "Fondue", "gruyere, emmental, white wine, garlic, kirsch", "Melt cheeses together with white wine and garlic in a communal pot.", "https://en.wikipedia.org/wiki/Fondue"),
            ("AUT", "Wiener schnitzel", "veal, flour, eggs, breadcrumbs, butter, lemon", "Coat veal cutlet in flour, egg, and breadcrumbs, then fry in butter.", "https://en.wikipedia.org/wiki/Wiener_schnitzel"),
            ("POL", "Bigos", "sauerkraut, cabbage, assorted meats, mushrooms, prunes", "Simmer shredded cabbage and sauerkraut with various meats and spices for hours.", "https://en.wikipedia.org/wiki/Bigos"),
            ("SWE", "Köttbullar", "minced beef, pork, breadcrumbs, milk, onion, cream", "Roll seasoned minced meat into balls, fry, and serve with cream sauce.", "https://en.wikipedia.org/wiki/Meatballs"),
            ("NOR", "Fårikål", "mutton, cabbage, whole black peppercorns, flour, water", "Layer pieces of mutton and cabbage in a pot with peppercorns and simmer until tender.", "https://en.wikipedia.org/wiki/F%C3%A5rik%C3%A5l"),
            ("FIN", "Karelian pasty", "rye flour, water, rice, milk, butter", "Bake thin rye crusts filled with rice porridge.", "https://en.wikipedia.org/wiki/Karelian_pasty"),
            ("DNK", "Stegt flæsk", "pork belly, parsley, potatoes, milk", "Fry pork belly slices until crisp and serve with parsley sauce and potatoes.", "https://en.wikipedia.org/wiki/Stegt_fl%C3%A6sk"),
            ("GRC", "Moussaka", "aubergine, minced lamb, tomatoes, onions, béchamel sauce", "Layer cooked aubergine and spiced minced meat, top with thick béchamel, and bake.", "https://en.wikipedia.org/wiki/Moussaka"),
            ("TUR", "Kuru fasulye", "white beans, onions, tomato paste, meat, oil", "Simmer white beans with onions, tomato paste, and meat until tender.", "https://en.wikipedia.org/wiki/Kuru_fasulye"),
            ("UKR", "Borscht", "beetroot, cabbage, potatoes, carrots, onions, meat", "Simmer beets and vegetables in a meat broth to form a rich, tart soup.", "https://en.wikipedia.org/wiki/Borscht"),
            ("HUN", "Goulash", "beef, onions, paprika, potatoes, vegetables", "Braize cubed beef with copious amounts of paprika and onions into a hearty stew.", "https://en.wikipedia.org/wiki/Goulash"),
            ("USA", "Hamburger", "beef patty, bun, lettuce, tomato, onion, condiments", "Grill a minced beef patty and serve inside a sliced bread roll with toppings.", "https://en.wikipedia.org/wiki/Hamburger"),
            ("CAN", "Poutine", "french fries, cheese curds, brown gravy", "Top hot French fries with fresh cheese curds and drench in hot brown gravy.", "https://en.wikipedia.org/wiki/Poutine"),
            ("MEX", "Tacos", "tortillas, meat, onions, cilantro, lime", "Warm tortillas and fill with seasoned meat, fresh onions, cilantro, and a squeeze of lime.", "https://en.wikipedia.org/wiki/Taco"),
            ("BRA", "Feijoada", "black beans, pork, beef, garlic, onion, bay leaves", "Slow-cook black beans and various cuts of salted pork and beef together in a heavy pot.", "https://en.wikipedia.org/wiki/Feijoada"),
            ("ARG", "Asado", "beef, salt, charcoal, chimichurri", "Grill various cuts of beef over hot coals and serve with chimichurri.", "https://en.wikipedia.org/wiki/Asado"),
            ("COL", "Bandeja paisa", "beans, rice, ground beef, plantain, chorizo, arepa, avocado, egg", "Assemble a platter featuring red beans, rice, minced meat, fried plantains, chorizo, arepa, avocado, and a fried egg.", "https://en.wikipedia.org/wiki/Bandeja_paisa"),
            ("PER", "Ceviche", "fish, lime juice, red onions, chilli peppers, sweet potato", "Cure raw fresh fish chunks in fresh citrus lime juice mixed with sliced onions and chillies.", "https://en.wikipedia.org/wiki/Ceviche"),
            ("CHL", "Empanada", "dough, minced beef, onions, raisins, egg, olives", "Enclose a savory filling of beef, onions, and spices inside dough and bake or fry.", "https://en.wikipedia.org/wiki/Empanada"),
            ("JPN", "Sushi", "rice, vinegar, sugar, salt, seafood, nori", "Season vinegar into cooked rice, shape by hand, and top with fresh seafood and seaweed.", "https://en.wikipedia.org/wiki/Sushi"),
            ("CHN", "Peking duck", "duck, honey, soy sauce, five-spice, pancakes", "Glaze duck, roast until skin is crisp, and serve sliced with thin pancakes and hoisin sauce.", "https://en.wikipedia.org/wiki/Peking_duck"),
            ("IND", "Khichdi", "rice, lentils, ghee, cumin, turmeric, water", "Cook rice and lentils together with spices and ghee until soft and porridge-like.", "https://en.wikipedia.org/wiki/Khichdi"),
            ("PAK", "Biryani", "rice, meat, yogurt, onions, spices", "Layer and steam partially cooked rice with spiced marinated meat.", "https://en.wikipedia.org/wiki/Biryani"),
            ("IDN", "Nasi goreng", "rice, garlic, shallots, tamarind, chilli, egg, chicken", "Stir-fry cooked rice with aromatic spices, sweet soy sauce, and proteins.", "https://en.wikipedia.org/wiki/Nasi_goreng"),
            ("THA", "Pad thai", "rice noodles, eggs, tofu, tamarind, fish sauce, shrimp", "Stir-fry soaked rice noodles with eggs, tofu, and shrimp in a tamarind sauce.", "https://en.wikipedia.org/wiki/Pad_thai"),
            ("VNM", "Pho", "rice noodles, beef broth, herbs, beef slices", "Pour hot aromatic beef broth over fresh rice noodles and raw beef slices.", "https://en.wikipedia.org/wiki/Pho"),
            ("PHL", "Adobo", "pork, chicken, vinegar, soy sauce, garlic, peppercorns", "Marinate and simmer chicken or pork in a mixture of vinegar, soy sauce, garlic, and black peppercorns.", "https://en.wikipedia.org/wiki/Philippine_adobo"),
            ("KOR", "Kimchi", "napa cabbage, radish, scallions, garlic, ginger, chili powder", "Salt and ferment vegetables seasoned with chili powder, garlic, and ginger.", "https://en.wikipedia.org/wiki/Kimchi"),
            ("MYS", "Nasi lemak", "rice, coconut milk, pandan leaves, anchovies, peanuts, egg, sambal", "Cook rice in coconut milk and pandan, serve with anchovies, peanuts, egg, and chili paste.", "https://en.wikipedia.org/wiki/Nasi_lemak"),
            ("SGP", "Chilli crab", "crab, tomato paste, chilli, garlic, eggs", " Stir-fry crab in a semi-thick, sweet and savoury tomato and chilli-based sauce.", "https://en.wikipedia.org/wiki/Chilli_crab"),
            ("AUS", "Meat pie", "minced meat, gravy, pastry", "Enclose diced or minced meat and gravy inside a shortcrust pastry shell.", "https://en.wikipedia.org/wiki/Meat_pie"),
            ("EGY", "Kushari", "rice, macaroni, lentils, tomato sauce, chickpeas, fried onions", "Combine layers of rice, macaroni, and lentils, topped with tomato sauce, chickpeas, and crispy onions.", "https://en.wikipedia.org/wiki/Kushari"),
            ("ZAF", "Bobotie", "minced meat, bread, milk, eggs, dried fruit, curry powder", "Bake spiced minced beef or lamb topped with an egg and milk custard mixture.", "https://en.wikipedia.org/wiki/Bobotie"),
            ("NGA", "Jollof rice", "rice, tomatoes, tomato paste, onions, scotch bonnets, spices", "Cook rice in a heavily seasoned tomato and pepper stew base.", "https://en.wikipedia.org/wiki/Jollof_rice"),
            ("KEN", "Ugali", "maize flour, water", "Boil maize flour and water together into a thick, stiff dough-like consistency.", "https://en.wikipedia.org/wiki/Ugali"),
            ("MAR", "Couscous", "semolina, vegetables, meat, broth", "Steam semolina grains and serve heaped with a stew of meat and vegetables.", "https://en.wikipedia.org/wiki/Couscous"),
            ("SAU", "Kabsa", "rice, meat, tomatoes, onions, mixed spices", "Cook long-grain rice and meat together with an aromatic blend of spices.", "https://en.wikipedia.org/wiki/Kabsa"),
            ("ISR", "Falafel", "chickpeas, herbs, spices, oil", "Shape ground chickpeas and spices into balls and deep-fry until crisp.", "https://en.wikipedia.org/wiki/Falafel"),
            ("IRN", "Ghormeh sabzi", "herbs, kidney beans, lamb, dried limes", "Stew lamb with a heavy mixture of sautéed herbs, kidney beans, and dried limes.", "https://en.wikipedia.org/wiki/Ghormeh_sabzi")
        ]
        cursor.executemany("""
            INSERT INTO dishes (iso, name, ingredients, method, wiki)
            VALUES (?, ?, ?, ?, ?)
        """, sample_dishes)
        conn.commit()
    conn.close()

init_db()

sessions = {}

class UserCreate(BaseModel):
    username: str
    password: str

from typing import Optional
class StatusUpdate(BaseModel):
    iso: str
    status: str
    taste_rating: Optional[int] = None
    chef_rating: Optional[int] = None

class DietaryUpdate(BaseModel):
    dietary_requirements: str

def hash_password(password: str, salt: str):
    return hashlib.sha256((password + salt).encode()).hexdigest()

@app.post("/api/register")
def register(user: UserCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already registered")
    
    salt = secrets.token_hex(16)
    p_hash = hash_password(user.password, salt)
    cursor.execute("INSERT INTO users (username, password_hash, salt, dietary_requirements) VALUES (?, ?, ?, ?)", (user.username, p_hash, salt, ""))
    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (form_data.username,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or user["password_hash"] != hash_password(form_data.password, user["salt"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    token = secrets.token_hex(32)
    sessions[token] = user["id"]
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    user_id = sessions.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user_id

@app.get("/api/dishes")
def get_dishes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dishes;")
        rows = cursor.fetchall()
        conn.close()
        
        dish_database = {}
        for row in rows:
            iso = row["iso"]
            ingredients_list = [i.strip() for i in row["ingredients"].split(",")]
            dish_database[iso] = {
                "name": row["name"],
                "ingredients": ingredients_list,
                "method": row["method"],
                "wiki": row["wiki"]
            }
        return dish_database
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/user-data")
def get_user_data(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username, dietary_requirements FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    
    cursor.execute("SELECT iso, status, taste_rating, chef_rating FROM user_dishes WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    statuses = {row["iso"]: {"status": row["status"], "taste_rating": row["taste_rating"], "chef_rating": row["chef_rating"]} for row in rows}
    
    return {
        "username": user["username"],
        "dietary_requirements": user["dietary_requirements"] or "",
        "statuses": statuses
    }

@app.post("/api/user-dietary")
def update_dietary(data: DietaryUpdate, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET dietary_requirements = ? WHERE id = ?", (data.dietary_requirements, user_id))
    conn.commit()
    conn.close()
    return {"message": "Dietary requirements updated"}

@app.post("/api/user-status")
def update_user_status(data: StatusUpdate, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    if data.status == "none":
        cursor.execute("DELETE FROM user_dishes WHERE user_id = ? AND iso = ?", (user_id, data.iso))
    else:
        cursor.execute("""
            INSERT INTO user_dishes (user_id, iso, status, taste_rating, chef_rating) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id, iso) DO UPDATE SET status = ?, taste_rating = ?, chef_rating = ?
        """, (user_id, data.iso, data.status, data.taste_rating, data.chef_rating, data.status, data.taste_rating, data.chef_rating))
    conn.commit()
    conn.close()
    return {"message": "Status updated"}

app.mount("/", StaticFiles(directory=".", html=True), name="static")