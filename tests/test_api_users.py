import pytest
import app as vampi_app
from api_views.users import JSON_MIME

def test_duplicate_user(client):
    payload = {"username": "admin", "password": "any", "email": "any@mail.com"}
    response = client.post('/users/v1/register', json=payload)
    assert response.status_code == 200
    assert b"User already exists" in response.data

def test_wrong_pwd(client):
    vampi_app.vuln = True #cover line 102
    payload = {"username": "admin", "password": "wrongpassword"}
    response = client.post('/users/v1/login', json=payload)
    assert b"Password is not correct" in response.data

def test_wrong_pwd_secure(client):
    vampi_app.vuln = False #cover line 107
    payload = {"username": "admin", "password": "wrongpassword"}
    response = client.post('/users/v1/login', json=payload)
    assert b"Username or Password Incorrect" in response.data

def test_get_me_profile(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/users/v1/_me', headers=headers)
    assert response.status_code == 200
    assert response.get_json()['data']['username'] == 'admin'

def test_update_pwd_bola(client, auth_token):
    vampi_app.vuln = True # line 197
    headers = {'Authorization': f'Bearer {auth_token}'}
    #attempt to change the pwd of name1 through username parameter on URL
    payload = {"password": "newpassword123"}
    response = client.put('/users/v1/password/name1', json=payload, headers=headers)
    assert response.status_code == 204
