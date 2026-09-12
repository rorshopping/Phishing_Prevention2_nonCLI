import httpx

ak = '50e88428b65db1b165d02ffb6c06d15f'
h = {'Authorization': f'Bearer {ak}', 'Content-Type': 'application/json'}
base = 'https://127.0.0.1:3333/api'

for resource in ['campaigns', 'groups', 'templates', 'pages', 'smtp']:
    r = httpx.get(f'{base}/{resource}/', headers=h, verify=False, timeout=10)
    for item in r.json():
        rid = item['id']
        try:
            if resource == 'campaigns' and item.get('status') != 'completed':
                httpx.put(f'{base}/campaigns/{rid}/complete', headers=h, verify=False, timeout=10)
            dr = httpx.delete(f'{base}/{resource}/{rid}/', headers=h, verify=False, timeout=10)
            print(f'DEL {resource}/{rid}: {dr.status_code}')
        except Exception as e:
            print(f'ERR {resource}/{rid}: {e}')

print('Done')
