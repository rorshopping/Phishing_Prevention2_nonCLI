import httpx

h = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f'}
cl = httpx.Client(verify=False, headers=h)
base = 'https://127.0.0.1:3333/api'

for r in ['campaigns', 'groups', 'templates', 'pages', 'smtp']:
    resp = cl.get(f'{base}/{r}/', timeout=10)
    items = resp.json()
    print(f'{r}: {len(items)} items')
    for item in items:
        iid = item['id']
        name = item.get('name', '')
        if r == 'campaigns':
            print(f'  - [{iid}] {name} status={item.get("status")} url={item.get("url")}')
            if item.get('results'):
                for res in item['results']:
                    print(f'      -> {res.get("email")} status={res.get("status")}')
        else:
            print(f'  - [{iid}] {name}')
cl.close()
