import pytest
import app as vampi_app
from api_views.books import JSON_MIME

def getallbooks(client):
    response = client.get('/books/v1/all')
    assert response.status_code == 200
    assert 'Books' in response.get_json()

def addbook(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    payload = {
        "book_title": "DevSecOps Handbook",
        "secret": "Security is a process, not a product."
    }
    response = client.post('/books/v1/add', json=payload, headers=headers)
    assert response.status_code == 200
    assert b"Book has been added." in response.data

def addbookinvalidjson(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    payload = {"book_title": "Invalid Book"}
    response = client.post('/books/v1/add', json=payload, headers=headers)
    assert response.status_code == 400
    assert b"Please provide a proper JSON body." in response.data

def addbookunauthorized(client):
    payload = {"book_title": "Ghost Book", "secret": "No token"}
    response = client.post('/books/v1/add', json=payload)
    assert response.status_code == 401

def gettitlebola(client, auth_token):
    vampi_app.vuln = True
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/books/v1/bookTitle1', headers=headers)
    assert response.status_code == 200
    assert 'secret' in response.get_json()

def gettitledenied(client, auth_token):
    vampi_app.vuln = False
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/books/v1/bookTitle1', headers=headers)
    assert response.status_code == 404
    assert b"Book not found!" in response.data

def gettitlenotfound(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/books/v1/NonExistingBook', headers=headers)
    assert response.status_code == 404