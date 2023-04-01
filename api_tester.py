import requests

# Register a new user
register_data = {
    "uname": "testuser",
    "mail": "testuser@example.com",
    "passw": "testpassword",
}

headers = {'Content-Type': 'application/json'}

response = requests.post("http://127.0.0.1:5000/api/register", json=register_data, headers=headers)
print("Register:", response.json())

# Login the user
login_data = {
    "uname": "testuser",
    "passw": "testpassword",
}

response = requests.post("http://127.0.0.1:5000/api/login", json=login_data, headers=headers)
print("Login:", response.json())

# Get the session cookie for the logged-in user
session_cookie = response.cookies

# Access the index as an authenticated user
response = requests.get("http://127.0.0.1:5000/api/index", cookies=session_cookie)
print("Index (authenticated):", response.json())

# Access the user's profile
response = requests.get("http://127.0.0.1:5000/api/profile", cookies=session_cookie)
print("Profile:", response.json())

# Access the user loader
response = requests.get("http://127.0.0.1:5000/api/user_loader", cookies=session_cookie)
print("User Loader:", response.json())

# Logout the user
response = requests.post("http://127.0.0.1:5000/api/logout", cookies=session_cookie)
print("Logout:", response.json())

# Access the index as a guest (unauthenticated user)
response = requests.get("http://127.0.0.1:5000/api/index")
print("Index (unauthenticated):", response.json())
