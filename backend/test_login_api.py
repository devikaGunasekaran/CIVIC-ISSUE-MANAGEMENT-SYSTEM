import requests

url = "http://127.0.0.1:8000/auth/token"
data = {
    "username": "admin",
    "password": "password"
}

try:
    response = requests.post(url, data=data, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
except Exception as e:
    print(f"Error: {e}")
