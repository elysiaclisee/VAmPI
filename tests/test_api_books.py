import pytest
import config

def test_get_all(client, auth_token):
    hd = {'Authorization': f'Bearer {auth_token}'}
    res = client.get('/books/v1', headers=hd)
    assert res.status_code == 200

def test_add_ok(client, auth_token):
    hd = {'Authorization': f'Bearer {auth_token}'}
    payload = {"book_title": "Unique_Title_Final", "secret": "No_Comment"}
    res = client.post('/books/v1', json=payload, headers=hd)
    assert res.status_code == 200

def test_get_bola(client, auth_token):
    config.vuln = True
    hd = {'Authorization': f'Bearer {auth_token}'}
    res = client.get('/books/v1/bookTitle1', headers=hd)
    assert res.status_code == 200

def test_get_secure(client):
    config.vuln = False
    login_res = client.post('/users/v1/login', json={"username": "admin", "password": "pass1"})
    token = login_res.get_json()['auth_token']
    hd = {'Authorization': f'Bearer {token}'}
    res = client.get('/books/v1/bookTitle1', headers=hd)
    assert res.status_code == 404
