import httpx, json

BASE = 'http://localhost:8000'

c = httpx.post(f'{BASE}/clients', json={
    'company_name': 'Bayerische Industrie AG',
    'contact_email': 'admin@testcompany.de',
    'contact_name': 'Test Admin',
    'industry': 'Technology',
    'employee_count': 50,
    'country': 'DE',
    'campaigns_per_year': 25,
    'vishing_enabled': True
}, timeout=10)
assert c.status_code == 201, f'Create client failed: {c.status_code} {c.text}'
cj = c.json()
cid = cj['id']
print(f'1. CLIENT: {cj["company_name"]} ({cid})')

emp = httpx.post(f'{BASE}/clients/{cid}/employees', json=[{
    'email': 'rorshopping@gmail.com',
    'name': 'Richard Or',
    'role': 'Developer',
    'department': 'Engineering',
    'group': 'engineering'
}], timeout=10)
assert emp.status_code == 201, f'Import failed: {emp.status_code} {emp.text}'
eid = emp.json()[0]['id']
print(f'2. EMPLOYEE: rorshopping@gmail.com ({eid})')

print('3. Triggering campaign...')
camp = httpx.post(f'{BASE}/clients/{cid}/campaigns', json={'difficulty': 'medium'}, timeout=120)
print(f'   Status: {camp.status_code}')
print(f'   Response: {json.dumps(camp.json(), indent=2, default=str)[:800]}')
