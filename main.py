from fastapi import FastAPI, Form
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId


app = FastAPI()

# Create a connection to the MongoDB database
client = MongoClient('mongodb://localhost:27017')
db = client['bookstoredb'] 
book = db['book'] #this is our book collection inside the database

# Created a Pydantic model for the book collection
class BookModel(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int
    num_of_sales: int

@app.get("/")
async def root():
    return {"message": "Hello, world!"}

@app.get("/books", response_model=List[BookModel])
# API endpoint: retrieves a list of all books in the store
async def get_books():
    listOfBooks = list(book.find({}))
    return listOfBooks

@app.get("/books/{book_id}")
# API endpoint: retrieves a specific book by ID
async def get_book_by_id(book_id: str):
    result = book.find_one({'_id': ObjectId(book_id)})
    if result is None:
        return {"message": "Book not found"}
    else:
        result['_id'] = str(result['_id'])
        return result

@app.post("/books")
# API endpoint: adds a new book to the store
async def add_book(title: str = Form(...), author: str  = Form(...), description: str  = Form(...), price: float  = Form(...), stock:int  = Form(...), num_of_sales: int = Form(...)):
    book_data = {"title": title, "author": author, "description": description, "price": price, "stock": stock, "num_of_sales":num_of_sales }
    book.insert_one(book_data)
    result = book.find_one(book_data)
    result['_id'] = str(result['_id'])
    return result

@app.put("/books/{book_id}")
# API endpoint: Updates an existing book by ID
async def update_book(book_id, title: str = Form(...), author: str  = Form(...), description: str  = Form(...), price: float  = Form(...), stock:int  = Form(...)):
    newvalues = { "$set": { "title": title, "author": author, "description": description, "price": price, "stock": stock} }
    book.update_one({'_id': ObjectId(book_id)}, newvalues)
    new_book = book.find_one({'_id': ObjectId(book_id)})
    new_book['_id'] = str(new_book['_id'])
    return new_book

@app.delete("/books/{book_id}")
# Deletes a book from the store by ID
async def delete_book(book_id):
    result = book.find_one({'_id': ObjectId(book_id)})
    if not result:
         return {"message": "Book not found"}
    else:
        book.delete_one({'_id': ObjectId(book_id)})
        return {"message": "Deleted book"}
    
@app.get("/search", response_model=List[BookModel])
# searches for book by title, author, and price range
async def search( title: Optional[str] = None, author: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
    query = {}
    if title:
        query["title"] = {"$regex": title, '$options': 'i'}
    if author:
        query["author"] = {"$regex": author, '$options': 'i'}
    price_query = {}
    if min_price:
        price_query["$gte"] = min_price
    if max_price:
        price_query["$lte"] = max_price
    if price_query:
        query["price"] = price_query
    listOfBooks = list(book.find(query))
    return listOfBooks