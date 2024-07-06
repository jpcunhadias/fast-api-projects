from fastapi import FastAPI, Query, Path, HTTPException
from pydantic import BaseModel, Field
from starlette import status
from typing import Optional

app = FastAPI()


class Book:
    id: int
    title: str
    author: str
    description: str
    rating: int
    published_year: int

    def __init__(self, id: int, title: str, author: str, description: str, rating: int, published_year: int):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_year = published_year


class BookRequest(BaseModel):
    id: Optional[int] = Field(None, description="ID not needed on creation", title="Book ID")
    title: str = Field(..., title="Book title", min_length=1, max_length=100)
    author: str = Field(..., title="Book author", min_length=1, max_length=100)
    description: str = Field(..., title="Book description", min_length=1, max_length=100)
    rating: int = Field(..., title="Book rating", ge=1, le=5)
    published_year: int = Field(..., title="Book published year", ge=1900, le=2024)

    class Config:
        schema_extra = {
            "example": {
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "description": "The story of the mysteriously wealthy Jay Gatsby and his love for the beautiful Daisy "
                               "Buchanan.",
                "rating": 5,
                "published_year": 1925
            }
        }


books = [
    Book(1, "The Great Gatsby", "F. Scott Fitzgerald",
         "The story of the mysteriously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.", 5, 1925),
    Book(2, "To Kill a Mockingbird", "Harper Lee",
         "The story of young Scout Finch and her father, Atticus, as they face the challenges of racism in the South.",
         4, 1960),
    Book(3, "1984", "George Orwell",
         "The story of Winston Smith, a member of the Outer Party, and his battle against Big Brother and the Thought "
         "Police.",
         5, 1949),
    Book(4, "Pride and Prejudice", "Jane Austen",
         "The story of Elizabeth Bennet and her love for the wealthy Mr. Darcy.", 4, 1813),
    Book(5, "The Catcher in the Rye", "J.D. Salinger",
         "The story of Holden Caulfield and his struggles with growing up and the phoniness of the adult world.", 3,
         1951)
]


@app.get("/books", status_code=status.HTTP_200_OK)
def get_books():
    return books


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
def get_book(book_id: int = Path(..., title="The ID of the book you want to get", gt=0, le=len(books) + 1)):
    for book in books:
        if book.id == book_id:
            return book
    return {"error": "Book not found"}


@app.get("/books/", status_code=status.HTTP_200_OK)
def get_books_by_rating(rating: int = Query(None, title="The rating of the books you want to get", gt=0, le=5)):
    return [book for book in books if book.rating == rating]


@app.get("/books/published/", status_code=status.HTTP_200_OK)
def get_books_by_published_year(
        published_year: int = Query(None, title="The published year of the books you want to get",
                                    gt=1900, le=2024)):
    return [book for book in books if book.published_year == published_year]


@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book_request: BookRequest):
    book = Book(len(books) + 1, book_request.title, book_request.author, book_request.description, book_request.rating,
                book_request.published_year)
    books.append(book)
    return book


def find_book_id(book: Book):
    book.id = 1 if len(books) == 0 else books[-1].id + 1
    return book


@app.put("/books/update_book", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(book: BookRequest):
    book_changed = False
    for i in range(len(books)):
        if books[i].id == book.id:
            books[i] = book
            book_changed = True
    if not book_changed:
        raise HTTPException(status_code=404, detail='Item not found')


@app.delete("/books/delete_book/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(..., title="The ID of the book you want to delete", gt=0, le=len(books) + 1)):
    book_deleted = False
    for i in range(len(books)):
        if books[i].id == book_id:
            del books[i]
            book_deleted = True
    if not book_deleted:
        raise HTTPException(status_code=404, detail='Item not found')
