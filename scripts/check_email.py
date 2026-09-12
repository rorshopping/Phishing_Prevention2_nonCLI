import httpx

h = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f'}
cl = httpx.Client(verify=False, headers=h, follow_redirects=True)
base = 'https://127.0.0.1:3333/api'

r = cl.get(f'{base}/campaigns/4', timeout=10)
c = r.json()
print('Subject:', c['template']['subject'])
print('HTML preview:')
print(c['template']['html'][:600])
print('...')
print('Text:', c['template']['text'][:300])
cl.close()
