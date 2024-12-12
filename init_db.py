from app import app, db
from models import Book, Author
from datetime import datetime

def init_db():
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Add sample authors
        author1 = Author(name="John Doe", age=35, company="Tech Books Inc")
        author2 = Author(name="Jane Smith", age=42, company="Education Press")
        db.session.add(author1)
        db.session.add(author2)
        db.session.commit()
        
        # Add sample books
        books = [
            Book(title="Python Programming", genre="Computer Science", 
                 publish_date=datetime(2023, 1, 15), price=45.00, author_id=author1.author_id),
            Book(title="Database Design", genre="Technology", 
                 publish_date=datetime(2023, 6, 20), price=40.00, author_id=author1.author_id),
            Book(title="Learning SQL", genre="Computer Science", 
                 publish_date=datetime(2023, 3, 10), price=35.00, author_id=author2.author_id)
        ]
        
        for book in books:
            db.session.add(book)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized with sample data!") 