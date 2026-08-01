import httpx, asyncio

async def clean():
    headers = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    base = 'https://127.0.0.1:3333/api'
    async with httpx.AsyncClient(verify=False, timeout=10) as c:
        for resource in ['campaigns', 'pages', 'templates', 'groups']:
            r = await c.get(f'{base}/{resource}/', headers=headers)
            for item in r.json():
                print(f'Deleting {resource[:-1]} {item.get("id")} {item.get("name")}')
                await c.delete(f'{base}/{resource}/{item.get("id")}', headers=headers)
        print('Done cleaning')

asyncio.run(clean())
