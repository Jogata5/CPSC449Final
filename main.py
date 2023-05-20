from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from fastapi.templating import Jinja2Templates

from pymongo import MongoClient
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Create a connection to the MongoDB database
client = MongoClient('mongodb://localhost:27017')
db = client['bookstoredb'] 
book = db['book'] #this is our book collection inside the database

# drop existing indexes
book.drop_indexes()

#Create indexes
book.create_index('title', name='title_index')
book.create_index('author', name='author_index')
book.create_index('price', name='price_index')

# Created a Pydantic model for the book collection
class BookModel(BaseModel):
    title: str
    author: str
    description: str
    price: float
    stock: int
    num_of_sales: int

@app.get("/", response_class=HTMLResponse)
async def base(request: Request):
    return templates.TemplateResponse("base.html", {"request" : request})
 

@app.get("/top5", response_class=HTMLResponse)
async def top5(request: Request):
    # Find the total number of books
    total_pipeline = [
        {
            '$group': {
                '_id': None, 
                'count': {'$sum': 1}, #shows how many distinct books we have
                'total': {'$sum': '$stock'} #gives the total book count
            }
        }
    ]
    total = list(book.aggregate(total_pipeline))

    # Find the top 5 bestselling books
    best_book_pipeline = [
        {
            '$group': {
                '_id': {'title': '$title', 'author': '$author'},
                'num_of_sales': {'$sum': '$num_of_sales'}
            }
        },
        {
            '$sort': {'num_of_sales':-1}
        },
        {   
            '$limit': 5
        }
    ]
    bestselling = list(book.aggregate(best_book_pipeline))

    #Find the top 5 authors with the most books in the store
    top_author_pipeline = [
        {
            '$group': {
                '_id': '$author',
                'sum_of_books': {'$sum': '$stock'}
            }
        }, 
        {
            '$sort': {'sum_of_books': -1}
        },
        {   
            '$limit': 5
        }
    ]

    top_authors = list(book.aggregate(top_author_pipeline))

    result =  {
            "Book Count and Total" : total,
            "Best Selling" : bestselling, 
            "Top Authors" : top_authors
            }
    
    return templates.TemplateResponse("top5.html", {"request": request, "result" : result})

@app.get("/add", response_class=HTMLResponse)
async def addBookPage(request: Request):
    return templates.TemplateResponse("add.html", {"request" : request})

@app.get("/delete", response_class=HTMLResponse)
async def deleteBookPage(request: Request):
    return templates.TemplateResponse("delete.html", {"request" : request})

@app.get("/update", response_class=HTMLResponse)
async def updateBookPage(request: Request):
    return templates.TemplateResponse("update.html", {"request" : request})


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
    final_book_data = BookModel(**book_data)
    # valdates the incoming data
    book.insert_one(dict(final_book_data))
    result = book.find_one(dict(final_book_data))
    result['_id'] = str(result['_id'])
    return result

@app.put("/books/{book_id}")
# API endpoint: Updates an existing book by ID
async def update_book(book_id, title: str = Form(...), author: str  = Form(...), description: str  = Form(...), price: float  = Form(...), stock:int  = Form(...), num_of_sales: int = Form(...)):
    newvalues = { "$set": { "title": title, "author": author, "description": description, "price": price, "stock": stock, "num_of_sales":num_of_sales} }
    book.update_one({'_id': ObjectId(book_id)}, newvalues)
    new_book = book.find_one({'_id': ObjectId(book_id)})
    new_book['_id'] = str(new_book['_id'])
    return new_book

@app.delete("/books/{book_id}")
# Deletes a book from the store by ID
async def delete_book(book_id : str):
    result = book.find_one({'_id': ObjectId(book_id)})
    if not result:
         return {"message": "Book not found"}
    else:
        book.delete_one({'_id': ObjectId(book_id)})
        return {"message": "Deleted book"}

@app.get("/test_page", response_class=HTMLResponse)
async def test(request: Request):
    return templates.TemplateResponse("test_page.html", {"request" : request})
    
@app.get("/test", response_class=HTMLResponse)
async def test(book_id, request: Request):
    print(book_id)
    return templates.TemplateResponse("test.html", {"request" : request ,"test" : book.find_one({'_id' : ObjectId(book_id)})  })
      
    
@app.get("/search", response_model=List[BookModel], response_class=HTMLResponse)
# searches for book by title, author, and price range
async def search(request: Request, title: Optional[str] = None, author: Optional[str] = None, min_price: Optional[float] = None, max_price: Optional[float] = None):
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
    return templates.TemplateResponse("search_results.html", {"request" : request, "result" : listOfBooks})
