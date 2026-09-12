import httpx

BASE = 'http://localhost:8000'
cid = '832e8316-8708-4135-8a1e-76c2c045c83a'

r = httpx.get(f'{BASE}/clients/{cid}/campaigns', timeout=10)
print('Campaign list:', r.status_code)
if r.status_code == 200:
    for c in r.json():
        print(f'  {c["id"]}: {c["name"]} status={c["status"]} sent={c["sent_count"]}')

# Get campaign results
camp_id = 'c7cbe705-d4b2-46b6-b7a7-88b15a0a23a8'
r2 = httpx.get(f'{BASE}/campaigns/{camp_id}/results', timeout=10)
print(f'\nResults: {r2.status_code}')
if r2.status_code == 200:
    for res in r2.json():
        print(f'  {res["employee_email"]}: opened={res["email_opened"]} clicked={res["link_clicked"]}')
