import re
import jsonschema
import jwt

from config import db, vuln_app
#Import only needed names or import the module and then use its members.
from api_views.json_schemas import register_user_schema, login_user_schema, update_email_schema
from flask import jsonify, Response, request, json
from models.user_model import User
from app import vuln

#Define a constant instead of duplicating this literal "application/json" 27 times.
JSON_MIME = "application/json"

def error_message_helper(msg):
    if isinstance(msg, dict):
        return '{ "status": "fail", "message": "' + msg['error'] + '"}'
    else:
        return '{ "status": "fail", "message": "' + msg + '"}'


def get_all_users():
    resp = token_validator(request.headers.get('Authorization'))
    
    if isinstance(resp, str): 
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)

    current_username = resp['sub']
    user_record = User.query.filter_by(username=current_username).first()

    # RBAC
    if not user_record or not user_record.admin:
        return Response(error_message_helper("Unauthorized! Admin access required to view all users."), 403, mimetype=JSON_MIME)

    list_of_users = []
    users = User.query.all()
    for user in users:
        user_data = {}
        user_data['username'] = user.username
        user_data['email'] = user.email
        user_data['admin'] = user.admin
        list_of_users.append(user_data)

    return Response(json.dumps({"status": "success", "users": list_of_users}), 200, mimetype=JSON_MIME)

def debug():
    resp = token_validator(request.headers.get('Authorization'))
    
    if isinstance(resp, str): 
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)

    current_username = resp['sub']
    req_user = User.query.filter_by(username=current_username).first()
    
    if not req_user or not req_user.admin:
        return Response(error_message_helper("Unauthorized! Top secret debug info is for Admins only."), 403, mimetype=JSON_MIME)

    return_value = jsonify({'users': User.get_all_users_debug()})
    return return_value

def me():
    resp = token_validator(request.headers.get('Authorization'))
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)
    else:
        user = User.query.filter_by(username=resp['sub']).first()
        responseObject = {
            'status': 'success',
            'data': {
                'username': user.username,
                'email': user.email,
                'admin': user.admin
            }
        }
        return Response(json.dumps(responseObject), 200, mimetype=JSON_MIME)
        

def get_by_username(username):
    resp = token_validator(request.headers.get('Authorization'))
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)

    current_user = resp['sub']
    user_record = User.query.filter_by(username=current_user).first()
    is_admin = user_record.admin if user_record else False

    if current_user != username and not is_admin:
        return Response(error_message_helper("Unauthorized! You cannot view other users' data."), 403, mimetype=JSON_MIME)

    if User.get_user(username):
        return Response(str(User.get_user(username)), 200, mimetype=JSON_MIME)
    else:
        return Response(error_message_helper("User not found"), 404, mimetype=JSON_MIME)
    
def register_user():
    request_data = request.get_json()
    user = User.query.filter_by(username=request_data.get('username')).first()
    if not user:
        try:
            jsonschema.validate(request_data, register_user_schema)
            user = User(
                username=request_data['username'], 
                password=request_data['password'],
                email=request_data['email']
            )
            db.session.add(user)
            db.session.commit()

            responseObject = {
                'status': 'success',
                'message': 'Successfully registered. Login to receive an auth token.'
            }

            return Response(json.dumps(responseObject), 200, mimetype=JSON_MIME)
        except jsonschema.exceptions.ValidationError as exc:
            return Response(error_message_helper(exc.message), 400, mimetype=JSON_MIME)
    else:
        return Response(error_message_helper("User already exists. Please Log in."), 200, mimetype=JSON_MIME)

def login_user():
    request_data = request.get_json()

    try:
        # validate the data are in the correct form
        jsonschema.validate(request_data, login_user_schema)
        # fetching user data if the user exists
        user = User.query.filter_by(username=request_data.get('username')).first()
        if user and request_data.get('password') == user.password:
            auth_token = user.encode_auth_token(user.username)
            responseObject = {
                'status': 'success',
                'message': 'Successfully logged in.',
                'auth_token': auth_token
            }
            return Response(json.dumps(responseObject), 200, mimetype=JSON_MIME)
        if vuln:  # Password Enumeration
            if user and request_data.get('password') != user.password:
                return Response(error_message_helper("Password is not correct for the given username."), 200,
                                mimetype=JSON_MIME)
            elif not user:  # User enumeration
                return Response(error_message_helper("Username does not exist"), 200, mimetype=JSON_MIME)
        else:
            if (user and request_data.get('password') != user.password) or (not user):
                return Response(error_message_helper("Username or Password Incorrect!"), 200,
                                mimetype=JSON_MIME)
    except jsonschema.exceptions.ValidationError as exc:
        return Response(error_message_helper(exc.message), 400, mimetype=JSON_MIME)
    #Specify an exception class to catch or reraise the exception
    except Exception:
        return Response(error_message_helper("An error occurred!"), 200, mimetype=JSON_MIME)


def token_validator(auth_header):
    if auth_header:
        try:
            auth_token = auth_header.split(" ")[1]
        #Specify an exception class to catch or reraise the exception
        except (IndexError, AttributeError):
            auth_token = ""
    else:
        auth_token = ""
    if auth_token:
        # if auth_token is valid we get back the username of the user
        return User.decode_auth_token(auth_token)
    else:
        return {'error': 'Invalid token. Please log in again.'}


def update_email(username):
    request_data = request.get_json()
    try:
        jsonschema.validate(request_data, update_email_schema)
    #Specify an exception class to catch or reraise the exception
    except jsonschema.exceptions.ValidationError:
        return Response(error_message_helper("Please provide a proper JSON body."), 400, mimetype=JSON_MIME)
    resp = token_validator(request.headers.get('Authorization'))
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)
    else:
        user = User.query.filter_by(username=resp['sub']).first()
        if vuln:  # Regex DoS
            match = re.search(
                r"^([0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])*@{1}([0-9a-zA-Z][-\w]*[0-9a-zA-Z]\.)+[a-zA-Z]{2,9})$",
                str(request_data.get('email')))
            if match:
                user.email = request_data.get('email')
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'username': user.username,
                        'email': user.email
                    }
                }
                return Response(json.dumps(responseObject), 204, mimetype=JSON_MIME)
            else:
                return Response(error_message_helper("Please Provide a valid email address."), 400,
                                mimetype=JSON_MIME)
        else:
            regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
            if (re.search(regex, request_data.get('email'))):
                user.email = request_data.get('email')
                db.session.commit()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'username': user.username,
                        'email': user.email
                    }
                }
                return Response(json.dumps(responseObject), 204, mimetype=JSON_MIME)
            else:
                return Response(error_message_helper("Please Provide a valid email address."), 400,
                                mimetype=JSON_MIME)


def update_password(username):
    request_data = request.get_json()
    resp = token_validator(request.headers.get('Authorization'))
    
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)
        
    if request_data.get('password'):
        user = User.query.filter_by(username=resp['sub']).first()
        
        if user:
            user.password = request_data.get('password')
            db.session.commit()
            
            responseObject = {
                'status': 'success',
                'Password': 'Updated.'
            }
            return Response(json.dumps(responseObject), 200, mimetype=JSON_MIME)
        else:
            return Response(error_message_helper("User Not Found"), 404, mimetype=JSON_MIME)
    else:
        return Response(error_message_helper("Malformed Data"), 400, mimetype=JSON_MIME)


def delete_user(username):
    resp = token_validator(request.headers.get('Authorization'))
    if "error" in resp:
        return Response(error_message_helper(resp), 401, mimetype=JSON_MIME)
    else:
        user = User.query.filter_by(username=resp['sub']).first()
        if user.admin:
            if bool(User.delete_user(username)):
                responseObject = {
                    'status': 'success',
                    'message': 'User deleted.'
                }
                return Response(json.dumps(responseObject), 200, mimetype=JSON_MIME)
            else:
                return Response(error_message_helper("User not found!"), 404, mimetype=JSON_MIME)
        else:
            return Response(error_message_helper("Only Admins may delete users!"), 401, mimetype=JSON_MIME)
