import httpx, asyncio

async def test():
    headers = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    base = 'https://127.0.0.1:3333/api'
    async with httpx.AsyncClient(verify=False, timeout=10) as c:
        r = await c.get(f'{base}/templates/', headers=headers)
        templates = r.json()
        for t in templates:
            html = t.get('html', '') or ''
            print(f"Template {t.get('id')}: name={t.get('name')}, html_len={len(html)}, subject={t.get('subject')}")

        # Try creating a campaign with the SMTP profile too
        smtp_r = await c.get(f'{base}/smtp/', headers=headers)
        smtps = smtp_r.json()
        for s in smtps:
            print(f"SMTP {s.get('id')}: name={s.get('name')}, host={s.get('host')}")

        # Get template by ID
        r = await c.get(f'{base}/templates/6', headers=headers)
        print(f"\nTemplate 6 by ID: {r.status_code}")
        print(f"  {r.text[:300]}")

        # Try with name-based references
        payload_name = {
            'name': 'TestCampaign-ByName',
            'groups': [{'id': 8}],
            'page': {'name': 'TestPage-Debug'},
            'template': {'name': 'TestTemplate-Debug'},
            'smtp': {'id': smtps[0].get('id')},
            'url': 'http://localhost:8080',
        }
        r = await c.post(f'{base}/campaigns/', headers=headers, json=payload_name)
        print(f"\nByName campaign: {r.status_code}")
        print(r.text[:500])

        # Try with both id and name
        payload_both = {
            'name': 'TestCampaign-Both',
            'groups': [{'id': 8}],
            'page': {'id': 6, 'name': 'TestPage-Debug'},
            'template': {'id': 6, 'name': 'TestTemplate-Debug'},
            'smtp': {'id': smtps[0].get('id')},
            'url': 'http://localhost:8080',
        }
        r = await c.post(f'{base}/campaigns/', headers=headers, json=payload_both)
        print(f"\nBoth campaign: {r.status_code}")
        print(r.text[:500])

asyncio.run(test())


asyncio.run(test())
