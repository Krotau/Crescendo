import requests

def test():
    url = "http://localhost:8000/generate"
    payload = {
        "q": "Hello, how are you?"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    print(response.status_code)
    print(response.json())

print("Running test...")
if __name__ == "__main__":
    test()