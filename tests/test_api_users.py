import config
import pytest
from api_views.users import JSON_MIME

def test_duplicate_user(client):
    payload = {"username": "admin", "password": "any", "email": "any@mail.com"}
    response = client.post('/users/v1/register', json=payload)
    assert response.status_code == 200
    assert b"User already exists" in response.data

def test_wrong_pwd(client):
    config.vuln = True 
    payload = {"username": "admin", "password": "wrong"}
    response = client.post('/users/v1/login', json=payload)
    assert b"Password is not correct" in response.data

def test_wrong_pwd_secure(client):
    config.vuln = False
    payload = {"username": "admin", "password": "wrong"}
    res = client.post('/users/v1/login', json=payload)
    assert b"Username or Password Incorrect" in res.data

def test_get_me_profile(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/me', headers=headers)
    assert response.status_code == 200

def test_update_pwd_bola(client, auth_token):
    config.vuln = True 
    headers = {'Authorization': f'Bearer {auth_token}'}
    payload = {"password": "newpassword123"}
    response = client.put('/users/v1/name1/password', json=payload, headers=headers)
    assert response.status_code == 204
