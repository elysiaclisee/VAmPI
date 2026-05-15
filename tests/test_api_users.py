import config
import pytest
from api_views.users import JSON_MIME

def test_reg_dup(client):
    payload = {"username": "admin", "password": "any", "email": "a@m.com"}
    res = client.post('/users/v1/register', json=payload)
    assert res.status_code == 200
    assert b"User already exists" in res.data

def test_login_vuln(client):
    config.vuln = True
    payload = {"username": "admin", "password": "wrong"}
    res = client.post('/users/v1/login', json=payload)
    assert b"Password is not correct" in res.data

def test_login_safe(client):
    config.vuln = False
    payload = {"username": "admin", "password": "wrong"}
    res = client.post('/users/v1/login', json=payload)
    assert b"Username or Password Incorrect" in res.data

def test_profile(client, auth_token):
    hd = {'Authorization': f'Bearer {auth_token}'}
    res = client.get('/me', headers=hd)
    assert res.status_code == 200

def test_pwd_bola(client, auth_token):
    config.vuln = True
    hd = {'Authorization': f'Bearer {auth_token}'}
    payload = {"password": "new_password"}
    res = client.put('/users/v1/name1/password', json=payload, headers=hd)
    assert res.status_code == 204
