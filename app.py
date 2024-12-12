from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from models import db, Book, Author
from schemas import AuthorSchema, BookSchema
from datetime import datetime
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"
db.init_app(app)

def handle_transaction(endpoint_name=None):
    """Decorator to handle database transactions with proper isolation level"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Begin transaction - SQLite only supports this basic transaction mode
                db.session.begin()
                
                result = func(*args, **kwargs)
                db.session.commit()
                return result
            except IntegrityError:
                db.session.rollback()
                flash('Transaction failed: Data was modified by another user. Please try again.', 'error')
                return redirect(url_for('index'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', 'error')
                return redirect(url_for('index'))
        return wrapper
    return decorator

# Book CRUD operations

@app.route('/')
def index():
    books = Book.query.all()
    authors = Author.query.all()
    return render_template('index.html', books=books, authors=authors)

@app.route('/book/create', methods=['GET', 'POST'])
@handle_transaction('create_book')
def create_book():
    if request.method == 'POST':
        try:
            new_book = Book(
                title=request.form['title'],
                genre=request.form['genre'],
                publish_date=datetime.strptime(request.form['publish_date'], '%Y-%m-%d'),
                price=float(request.form['price']),
                author_id=int(request.form['author_id'])
            )
            db.session.add(new_book)
            db.session.commit()
            flash('Book created successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error creating book: {str(e)}', 'error')
            return redirect(url_for('create_book'))
    
    # Get all required data for the form
    authors = Author.query.all()
    genres = db.session.query(Book.genre).distinct().all()
    
    # Modified query to include author information for the table
    books_query = text("""
        SELECT b.book_id, b.title, b.genre, b.publish_date, b.price, 
               a.name as author_name
        FROM books b
        LEFT JOIN authors a ON b.author_id = a.author_id
        ORDER BY b.book_id
    """)
    books = db.session.execute(books_query).fetchall()
    
    return render_template('book_form.html', 
                         authors=authors, 
                         genres=genres,
                         books=books,
                         action="Create")

@app.route('/book/edit/<int:id>', methods=['GET', 'POST'])
@handle_transaction('edit_book')
def edit_book(id):
    book = Book.query.get_or_404(id)
    
    if request.method == 'GET':
        authors = Author.query.all()
        genres = db.session.query(Book.genre).distinct().all()
        
        # Modified query to include author information
        books_query = text("""
            SELECT b.book_id, b.title, b.genre, b.publish_date, b.price, 
                   a.name as author_name, a.author_id
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.author_id
            ORDER BY b.book_id
        """)
        books = db.session.execute(books_query).fetchall()
        
        return render_template('book_form.html', 
                             book=book, 
                             authors=authors, 
                             genres=genres,
                             books=books,
                             action="Edit")
    
    if request.method == 'POST':
        try:
            book.title = request.form['title']
            book.genre = request.form['genre']
            book.publish_date = datetime.strptime(request.form['publish_date'], '%Y-%m-%d')
            book.price = float(request.form['price'])
            book.author_id = int(request.form['author_id'])
            
            db.session.commit()
            flash('Book updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating book: {str(e)}', 'error')
            return redirect(url_for('edit_book', id=id))

@app.route('/book/delete/<int:book_id>', methods=['POST'])
@handle_transaction('delete_book')
def delete_book(book_id):
    try:
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        flash('Book deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting book: {str(e)}', 'error')
    return redirect(url_for('index'))

# Author CRUD operations

@app.route('/author/create', methods=['GET', 'POST'])
def create_author():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age']) if request.form['age'] else None
        company = request.form['company']
        new_author = Author(name=name, age=age, company=company)
        db.session.add(new_author)
        db.session.commit()
        flash('Author created successfully!', 'success')
        return redirect(url_for('index'))
    
    authors = Author.query.all()  # Retrieve all authors for display in table
    return render_template('author_form.html', authors=authors, action="Create")

@app.route('/author/edit/<int:author_id>', methods=['GET', 'POST'])
def edit_author(author_id):
    author = Author.query.get_or_404(author_id)
    if request.method == 'POST':
        author.name = request.form['name']
        author.age = int(request.form['age']) if request.form['age'] else None
        author.company = request.form['company']
        db.session.commit()
        flash('Author updated successfully!', 'success')
        return redirect(url_for('index'))
    
    authors = Author.query.all()  # Retrieve all authors for display in table
    return render_template('author_form.html', author=author, authors=authors, action="Edit")

@app.route('/author/delete/<int:author_id>', methods=['POST'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    flash('Author deleted successfully!', 'success')
    return redirect(url_for('index'))

# Report with Prepared Statement
@app.route('/report', methods=['GET', 'POST'])
def book_report():
    if request.method == 'POST':
        min_price = float(request.form['min_price'])
        max_price = float(request.form['max_price'])
        genre = request.form.get('genre')
        
        query = Book.query.filter(Book.price.between(min_price, max_price))
        
        if genre:
            query = query.filter(Book.genre == genre)
        
        books = query.all()
        
        avg_price = db.session.query(func.avg(Book.price)).filter(Book.price.between(min_price, max_price)).scalar()
        book_count = len(books)
        
        return render_template('report.html', books=books, min_price=min_price, max_price=max_price, genre=genre, avg_price=avg_price, book_count=book_count)
    
    genres = db.session.query(Book.genre).distinct().all()
    genres = [genre[0] for genre in genres if genre[0]]
    return render_template('report_form.html', genres=genres)
# Report by price range
@app.route('/report_by_price', methods=['POST'])
@handle_transaction('report_by_price')
def report_by_price():
    try:
        min_price = float(request.form.get('min_price', 0))
        max_price = float(request.form.get('max_price', float('inf')))
        
        query = text("""
            SELECT b.*, a.name as author_name
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            WHERE b.price BETWEEN :min_price AND :max_price
        """)
        
        books = db.session.execute(query, {
            "min_price": min_price,
            "max_price": max_price
        }).fetchall()

        stats_query = text("""
            SELECT AVG(price) as avg_price,
                   MIN(price) as min_price,
                   MAX(price) as max_price
            FROM books
            WHERE price BETWEEN :min_price AND :max_price
        """)
        
        stats = db.session.execute(stats_query, {
            "min_price": min_price,
            "max_price": max_price
        }).first()

        return render_template('report.html', 
                             books=books,
                             stats=stats,
                             report_type='price')

    except Exception as e:
        print(f"Error in report_by_price: {str(e)}")
        db.session.rollback()
        flash(f'Error generating price report: {str(e)}', 'error')
        return redirect(url_for('book_report'))

@app.route('/report_by_age', methods=['POST'])
@handle_transaction('report_by_age')
def report_by_age():
    try:
        min_age = int(request.form.get('min_age', 0))
        
        query = text("""
            SELECT b.*, a.name as author_name
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            WHERE a.age >= :min_age
        """)
        
        books = db.session.execute(query, {
            "min_age": min_age
        }).fetchall()

        stats_query = text("""
            SELECT AVG(b.price) as avg_price,
                   MIN(b.price) as min_price,
                   MAX(b.price) as max_price
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            WHERE a.age >= :min_age
        """)
        
        stats = db.session.execute(stats_query, {
            "min_age": min_age
        }).first()

        return render_template('report.html', 
                             books=books,
                             stats=stats,
                             report_type='age')

    except Exception as e:
        print(f"Error in report_by_age: {str(e)}")
        db.session.rollback()
        flash(f'Error generating age report: {str(e)}', 'error')
        return redirect(url_for('book_report'))

@app.route('/report_by_company', methods=['POST'])
@handle_transaction('report_by_company')
def report_by_company():
    try:
        company = request.form.get('company', '')
        
        query = text("""
            SELECT b.*, a.name as author_name
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            WHERE a.company LIKE :company
        """)
        
        books = db.session.execute(query, {
            "company": f"%{company}%"
        }).fetchall()

        stats_query = text("""
            SELECT AVG(b.price) as avg_price,
                   MIN(b.price) as min_price,
                   MAX(b.price) as max_price
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            WHERE a.company LIKE :company
        """)
        
        stats = db.session.execute(stats_query, {
            "company": f"%{company}%"
        }).first()

        return render_template('report.html', 
                             books=books,
                             stats=stats,
                             report_type='company')

    except Exception as e:
        print(f"Error in report_by_company: {str(e)}")
        db.session.rollback()
        flash(f'Error generating company report: {str(e)}', 'error')
        return redirect(url_for('book_report'))

@app.route('/report_by_date', methods=['POST'])
@handle_transaction('report_by_date')
def report_by_date():
    try:
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        query = text("""
            SELECT b.*, a.name as author_name
            FROM books b
            JOIN authors a ON b.author_id = a.author_id
            WHERE b.publish_date BETWEEN :start_date AND :end_date
        """)
        
        books = db.session.execute(query, {
            "start_date": start_date,
            "end_date": end_date
        }).fetchall()

        stats_query = text("""
            SELECT COUNT(*) as book_count,
                   AVG(price) as avg_price,
                   MIN(price) as min_price,
                   MAX(price) as max_price
            FROM books
            WHERE publish_date BETWEEN :start_date AND :end_date
        """)
        
        stats = db.session.execute(stats_query, {
            "start_date": start_date,
            "end_date": end_date
        }).first()

        return render_template('report.html', 
                             books=books,
                             stats=stats,
                             report_type='date')

    except Exception as e:
        print(f"Error in report_by_date: {str(e)}")
        db.session.rollback()
        flash(f'Error generating date report: {str(e)}', 'error')
        return redirect(url_for('book_report'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
