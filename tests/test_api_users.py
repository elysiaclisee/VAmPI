import pytest
import app as vampi_app
from users import JSON_MIME

def duplicateuser(client):
    payload = {"username": "admin", "password": "any", "email": "any@mail.com"}
    response = client.post('/users/v1/register', json=payload)
    assert response.status_code == 200
    assert b"User already exists" in response.data

def wrongpwd(client):
    vampi_app.vuln = True # Kích hoạt nhánh vuln để bao phủ dòng 102
    payload = {"username": "admin", "password": "wrongpassword"}
    response = client.post('/users/v1/login', json=payload)
    assert b"Password is not correct" in response.data

def wrongpwdsecure(client):
    vampi_app.vuln = False # Kích hoạt nhánh an toàn để bao phủ dòng 107
    payload = {"username": "admin", "password": "wrongpassword"}
    response = client.post('/users/v1/login', json=payload)
    assert b"Username or Password Incorrect" in response.data

def getprofile(client, auth_token):
    headers = {'Authorization': f'Bearer {auth_token}'}
    response = client.get('/users/v1/me', headers=headers)
    assert response.status_code == 200
    assert response.get_json()['data']['username'] == 'admin'

def update_pwd_unauth(client, auth_token):
    vampi_app.vuln = True # Test lỗi BOLA tại dòng 197
    headers = {'Authorization': f'Bearer {auth_token}'}
    # Admin cố tình đổi pass của name1 qua tham số username trên URL
    payload = {"password": "newpassword123"}
    response = client.put('/users/v1/update/password/name1', json=payload, headers=headers)
    assert response.status_code == 204