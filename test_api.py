import requests
import json

print("Testing API...")
try:
    r = requests.post('http://localhost:5000/api/chat', json={'message': 'test'}, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    data = r.json()
    print(f"\nHas 'error' field: {'error' in data}")
    if 'error' in data:
        print(f"Error value: {data['error']}")
except Exception as e:
    print(f"Exception: {e}")
