# schemas.py
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
from models import Book, Author
from models import db

class AuthorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Author
        include_relationships = True
        load_instance = True
        sqla_session = db.session  # Manually set the SQLAlchemy session

class BookSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        include_relationships = True
        load_instance = True
        sqla_session = db.session  # Manually set the SQLAlchemy session

    author = fields.Nested(AuthorSchema)
