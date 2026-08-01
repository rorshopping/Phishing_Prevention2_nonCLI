import httpx

ak = '50e88428b65db1b165d02ffb6c06d15f'
h = {'Authorization': f'Bearer {ak}', 'Content-Type': 'application/json'}
base = 'https://127.0.0.1:3333/api'
cl = httpx.Client(verify=False, headers=h, follow_redirects=True)

for resource in ['campaigns', 'groups', 'templates', 'pages', 'smtp']:
    r = cl.get(f'{base}/{resource}/', timeout=10)
    items = r.json()
    for item in items:
        rid = item['id']
        try:
            if resource == 'campaigns':
                cl.put(f'{base}/campaigns/{rid}/complete', timeout=10)
            dr = cl.delete(f'{base}/{resource}/{rid}/', timeout=10)
            print(f'DEL {resource}/{rid}: {dr.status_code}')
        except Exception as e:
            print(f'ERR {resource}/{rid}: {e}')

print('Gophish cleaned')
cl.close()
