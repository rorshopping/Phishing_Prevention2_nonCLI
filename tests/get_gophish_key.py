import requests, json, sys

requests.packages.urllib3.disable_warnings()

admin_pass = sys.argv[1] if len(sys.argv) > 1 else "67a96875edc69828"

# Step 1: Login to get session
r = requests.post("https://127.0.0.1:3333/api/login",
    json={"username": "admin", "password": admin_pass},
    verify=False)
if r.status_code != 200:
    print(f"Login failed: {r.status_code} {r.text}")
    sys.exit(1)

token = r.json().get("token")
print(f"Session token: {token[:20]}...")

# Step 2: Get user info (includes API key)
r = requests.get("https://127.0.0.1:3333/api/users/1",
    headers={"Authorization": f"Bearer {token}"},
    verify=False)
if r.status_code == 200:
    data = r.json()
    api_key = data.get("api_key") if isinstance(data, dict) else data.get("api_key", "")
    print(f"API key: {api_key}")
else:
    print(f"Failed: {r.status_code} {r.text}")
