from app import app, db
from sqlalchemy import text

def create_indexes():
    with app.app_context():
        try:
            # Clustered indexes are already on book_id and author_id (PRIMARY KEYS)
            
            # Most important unclustered indexes
            
            # Index for price range queries (frequently used in reports)
            db.session.execute(text('''
                CREATE INDEX IF NOT EXISTS idx_books_price 
                ON books(price);
            '''))
            
            # Composite index for genre and price (commonly used together in reports)
            db.session.execute(text('''
                CREATE INDEX IF NOT EXISTS idx_books_genre_price 
                ON books(genre, price);
            '''))
            
            # Index for company-based queries in reports
            db.session.execute(text('''
                CREATE INDEX IF NOT EXISTS idx_authors_company 
                ON authors(company);
            '''))

            # Add hash index for publish_date
            # Note: SQLite doesn't directly support HASH indexes, but we can create a function-based index
            db.session.execute(text('''
                CREATE INDEX IF NOT EXISTS idx_books_publish_date_hash 
                ON books(abs(julianday(publish_date)));
            '''))

            db.session.commit()
            print("Indexes created successfully!")
            
            # Verify indexes
            print("\nVerifying indexes...")
            indexes = db.session.execute(text('''
                SELECT name, tbl_name 
                FROM sqlite_master 
                WHERE type = 'index';
            ''')).fetchall()
            
            print("\nExisting indexes:")
            for index in indexes:
                print(f"Index: {index.name}, Table: {index.tbl_name}")

        except Exception as e:
            print(f"Error creating indexes: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    create_indexes() 