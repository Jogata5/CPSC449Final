from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel

app = FastAPI()

# Create a connection to the MongoDB database
client = MongoClient('mongodb://localhost:27017')
db = client['bookstoredb'] 
book = db['book'] #this is our book collection inside the database

# insert a book into the database and our collection
result = book.insert_one({'title': 'The Greate Gatsby'})

# Created a Pydantic model for the book collection
class BookModel(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int

@app.get("/")
async def root():
    return {"message": "Hello, world!"}