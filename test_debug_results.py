import httpx, json

BASE = 'http://localhost:8000'
camp_id = 'c7cbe705-d4b2-46b6-b7a7-88b15a0a23a8'

r2 = httpx.get(f'{BASE}/campaigns/{camp_id}/results', timeout=10)
print('Status:', r2.status_code)
print('Body:', json.dumps(r2.json(), indent=2, default=str)[:800])
