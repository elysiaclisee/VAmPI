import pytest
import config

def test_get_all_books(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/books/v1/all', headers=headers)
    assert response.status_code == 200
    assert 'Books' in response.get_json()

def test_add_new_book_success(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    payload = {"book_title": "New Title", "secret": "Secret Content"}
    response = client.post('/books/v1/books', json=payload, headers=headers)
    assert response.status_code == 200
    assert b"Book has been added." in response.data

def test_add_new_book_invalid(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    payload = {"book_title": "Invalid"}
    response = client.post('/books/v1/books', json=payload, headers=headers)
    assert response.status_code == 400
    assert b"proper JSON body" in response.data

def test_add_new_book_unauthorized(client):
    payload = {"book_title": "Ghost", "secret": "None"}
    response = client.post('/books/v1/books', json=payload)
    assert response.status_code == 401

def test_get_by_title_bola(client, auth_token):
    config.vuln = True 
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/books/v1/book/bookTitle1', headers=headers)
    assert response.status_code == 200

def test_get_by_title_secure_access_denied(client, auth_token):
    config.vuln = False 
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/books/v1/book/bookTitle1', headers=headers)
    assert response.status_code == 404
    assert b"Book not found!" in response.data
