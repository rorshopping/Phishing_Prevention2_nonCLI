import secrets
import sqlite3
import sys

db_path = r"C:\Users\Richard\Documents\Projects\Phishing_Prevention2_nonCLI\gophish\gophish.db"

# Accept API key from CLI arg, or generate random one
if len(sys.argv) > 1:
    api_key = sys.argv[1]
    print(f"Using provided API key: {api_key}")
else:
    api_key = secrets.token_hex(32)
    print(f"Generated new API key: {api_key}")

# Update the database (api_key column stores the raw key, hash column is for password)
db = sqlite3.connect(db_path)
db.execute("UPDATE users SET api_key = ? WHERE id = 1", (api_key,))
db.commit()
db.close()
print("API key updated in gophish.db")

# Verify the API key works
import httpx
base = "https://127.0.0.1:3333"
client = httpx.Client(verify=False)
r = client.get(f"{base}/api/users/", headers={"Authorization": api_key})
print(f"Test with new API key: {r.status_code}")
try:
    print(r.json())
except:
    print(r.text[:500])
