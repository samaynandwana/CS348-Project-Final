# Database Index Documentation

## Index Overview and Usage

### 1. Clustered Indexes (Primary Keys)

#### books(book_id) 
- Type: Clustered B+ tree, automatically created as PRIMARY KEY
- Usage in Direct book lookups by ID, which is used in Edit book operations. 

#### authors(author_id) 
- Type: Clustered B+ tree, automatically created as PRIMARY KEY
- Usage for direct author lookups in the foreign key relationship, when we select
author when creating a book. 

### 2. Unclustered Indexes

#### idx_books_price: books(price)
- Type: Unclustered B+ tree
- Used in Report features as follows:
  - Price range queries in reports

#### idx_authors_company: authors(company)
- Type: Unclustered B+ tree
- Used in Report features as follows:
  - Report Feature to query by input company

### 3. Hash Indexes

#### idx_books_publish_date_hash: books(publish_date)
- Type: Hash 
- Column: books(publish_date)
- Used in:
  - Date-specific queries for filteirng between the date range
  - Good since dates are generally unique 

## Reasoning for Queries
Overall, the queries are fast and efficient. The hash index is used for the date range queries, which are fast since the dates are generally unique and not likely to be repeated (not neceessarily sequential like an ID). The unclustered indexes are used for the price range queries and the company queries, since these are not unique and are not in sequential order (may be repeated). The clustered indexes are used for the direct lookups by ID, which is used in the Edit book operations. 

