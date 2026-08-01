import httpx, asyncio

async def test():
    headers = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    base = 'https://127.0.0.1:3333/api'
    async with httpx.AsyncClient(verify=False, timeout=10) as c:
        payload = {
            'name': 'Campaign-Correct',
            'groups': [{'name': 'GroupForUser'}],
            'page': {'name': 'ProperPage'},
            'template': {'name': 'ProperTemplate'},
            'smtp': {'name': 'Test SMTP 2'},
            'url': 'http://localhost:8080',
        }
        r = await c.post(f'{base}/campaigns/', headers=headers, json=payload)
        print(f"Campaign: {r.status_code}")
        print(r.text[:500])
        if r.status_code < 400:
            camp = r.json()
            print(f"Campaign created! ID: {camp.get('id')}")

asyncio.run(test())
