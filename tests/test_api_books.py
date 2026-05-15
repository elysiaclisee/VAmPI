import pytest
import config

def test_get_all(client, auth_token):
    hd = {'Authorization': f'Bearer {auth_token}'}
    res = client.get('/books/v1', headers=hd)
    assert res.status_code == 200

def test_add_ok(client, auth_token):
    hd = {'Authorization': f'Bearer {auth_token}'}
    payload = {"book_title": "Unique_DevSecOps", "secret": "Clean_Code"}
    res = client.post('/books/v1', json=payload, headers=hd)
    assert res.status_code == 200

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
