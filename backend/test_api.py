import requests

# Test login
response = requests.post('http://localhost:8000/api/v1/auth/login', json={
    'email': 'setosa@example.com',
    'password': 'password123'
})
print('Login response:', response.status_code)
data = response.json()
print('Token:', data.get('access_token', 'No token'))

# Test data with token
if 'access_token' in data:
    headers = {'Authorization': f"Bearer {data['access_token']}"}
    response = requests.get('http://localhost:8000/api/v1/data/my-data', headers=headers)
    print('Data response:', response.status_code)
    print('Data:', response.json())