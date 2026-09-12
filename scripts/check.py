import httpx, time

# Check Gophish
h = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f'}
cl = httpx.Client(verify=False, headers=h, follow_redirects=True)
base = 'https://127.0.0.1:3333/api'

r = cl.get(f'{base}/campaigns/', timeout=10)
for c in r.json():
    print(f'Campaign [{c["id"]}]: {c["name"]}')
    print(f'  Status: {c["status"]}')
    print(f'  SMTP: {c.get("smtp", {}).get("name")} -> {c.get("smtp", {}).get("host")}')
    print(f'  URL: {c.get("url")}')
    if c.get('results'):
        for res in c['results']:
            print(f'  Target: {res["email"]} -> status={res["status"]}')
            if res.get('send_date'):
                print(f'  Send date: {res["send_date"]}')
            if res.get('error'):
                print(f'  Error: {res["error"]}')
    if c.get('timeline'):
        for t in c['timeline']:
            print(f'  [{t["time"][:19]}] {t["message"]} {t.get("details","")[:100]}')

cl.close()
