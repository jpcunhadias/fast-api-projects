from fastapi import FastAPI

app = FastAPI()

books = [
    {
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J.K. Rowling",
        "year": 1997,
        "category": "Fantasy"
    },
    {
        "title": "The Hobbit",
        "author": "J.R.R. Tolkien",
        "year": 1937,
        "category": "Fantasy"
    },
    {
        "title": "The Catcher in the Rye",
        "author": "J.D. Salinger",
        "year": 1951,
        "category": "Fiction"
    },
    {
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "year": 1960,
        "category": "Fiction"
    },
    {
        "title": "Pride and Prejudice",
        "author": "Jane Austen",
        "year": 1813,
        "category": "Romance"
    },
    {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "year": 1925,
        "category": "Fiction"
    }
]


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/books")
async def read_books():
    return books


@app.get("/books/by_category/")
async def read_books_by_category_query(category: str):
    return [book for book in books if book["category"].casefold() == category.casefold()]


@app.get("/books/{book_id}")
async def read_book_by_id(book_id: int):
    return books[book_id]


@app.get("/books/by_author/")
async def read_books_by_author_path(author: str):
    return [book for book in books if book["author"].casefold() == author.casefold()]


@app.get("/books/by_author")
async def read_books_by_category_and_author_query(category: str, author: str):
    return [book for book in books if book["category"] == category and book["author"].casefold() == author.casefold()]


@app.post("/books")
async def create_book(book: dict):
    books.append(book)
    return book


@app.put("/books/{book_id}")
async def update_book(book_id: int, book: dict):
    books[book_id] = book
    return book


@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
    book = books[book_id]
    del books[book_id]
    return book
