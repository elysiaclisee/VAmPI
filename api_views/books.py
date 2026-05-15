import jsonschema
from api_views.users import token_validator, error_message_helper
from config import db
#Import only needed names or import the module and then use its members
from api_views.json_schemas import add_book_schema
from flask import jsonify, Response, request, json
from models.user_model import User
from models.books_model import Book
from config import vuln

#Define a constant instead of duplicating this literal "application/json" 9 times
JSON_MIME = "application/json"

def get_all_books():
    return jsonify({'Books': Book.get_all_books()})

def add_new_book():
    request_data = request.get_json()
    try:
        jsonschema.validate(request_data, add_book_schema)
    # Specify an exception class to catch or reraise the exception
    except jsonschema.ValidationError:
        return Response(error_message_helper("Please provide a proper JSON body."), 400, mimetype=JSON_MIME)
    
    resp = token_validator(request.headers.get('Authorization'))
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)
    
    user = User.query.filter_by(username=resp['sub']).first()
    book = Book.query.filter_by(user=user, book_title=request_data.get('book_title')).first()
    
    if book:
        return Response(error_message_helper("Book Already exists!"), 400, mimetype=JSON_MIME)
    
    newBook = Book(book_title=request_data.get('book_title'), secret_content=request_data.get('secret'),
                   user_id=user.id)
    db.session.add(newBook)
    db.session.commit()
    
    responseObject = {'status': 'success', 'message': 'Book has been added.'}
    return Response(json.dumps(responseObject), 200, mimetype=JSON_MIME)

def get_by_title(book_title):
    resp = token_validator(request.headers.get('Authorization'))
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)
    else:
        if vuln:  # Broken Object Level Authorization
            book = Book.query.filter_by(book_title=str(book_title)).first()
            if book:
                responseObject = {
                    'book_title': book.book_title,
                    'secret': book.secret_content,
                    'owner': book.user.username
                }
                return Response(json.dumps(responseObject), 200, mimetype=JSON_MIME)
            else:
                return Response(error_message_helper("Book not found!"), 404, mimetype=JSON_MIME)
        else:
            user = User.query.filter_by(username=resp['sub']).first()
            book = Book.query.filter_by(user=user, book_title=str(book_title)).first()
            if book:
                responseObject = {
                    'book_title': book.book_title,
                    'secret': book.secret_content,
                    'owner': book.user.username
                }
                return Response(json.dumps(responseObject), 200, mimetype=JSON_MIME)
            else:
                return Response(error_message_helper("Book not found!"), 404, mimetype=JSON_MIME)
