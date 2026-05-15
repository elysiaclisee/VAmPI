import pytest
import config

def test_get_all(client, auth_token):
    hd = {'Authorization': f'Bearer {auth_token}'}
    res = client.get('/books/v1', headers=hd)
    assert res.status_code == 200

def test_add_ok(client, auth_token):
    hd = {'Authorization': f'Bearer {auth_token}'}
    payload = {"book_title": "New_Title", "secret": "Secret_Data"}
    res = client.post('/books/v1', json=payload, headers=hd)
    assert res.status_code == 200

def test_add_bad(client, auth_token):
    hd = {'Authorization': f'Bearer {auth_token}'}
    res = client.post('/books/v1', json={"book_title": "Fail"}, headers=hd)
    assert res.status_code == 400

def test_add_401(client):
    res = client.post('/books/v1', json={"book_title": "Ghost"})
    assert res.status_code == 401

def test_get_bola(client, auth_token):
    config.vuln = True
    hd = {'Authorization': f'Bearer {auth_token}'}
    res = client.get('/books/v1/bookTitle1', headers=hd)
    assert res.status_code == 200

def test_get_secure(client, auth_token):
    config.vuln = False
    hd = {'Authorization': f'Bearer {auth_token}'}
    res = client.get('/books/v1/bookTitle1', headers=hd)
    assert res.status_code == 404
