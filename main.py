from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------- FAKE DATABASE (for now) -----------
DB = []

# ----------- DATA MODEL -----------
class Food(BaseModel):
    dish_name: str
    price: float
    rating: float

# ----------- GET ALL -----------
@app.get("/foods")
def get_foods():
    return DB

# ----------- CREATE -----------
@app.post("/foods")
def add_food(food: Food):
    DB.append(food)
    return {"message": "Food added", "data": food}

# ----------- UPDATE -----------
@app.put("/foods/{index}")
def update_food(index: int, food: Food):
    if index < len(DB):
        DB[index] = food
        return {"message": "Updated", "data": food}
    return {"error": "Not found"}

# ----------- DELETE -----------
@app.delete("/foods/{index}")
def delete_food(index: int):
    if index < len(DB):
        removed = DB.pop(index)
        return {"message": "Deleted", "data": removed}
    return {"error": "Not found"}


@app.post("/login")
def login(user: dict):
    if user["username"] == "admin" and user["password"] == "food123":
        return {"message": "Login successful"}
    return {"error": "Invalid credentials"}
