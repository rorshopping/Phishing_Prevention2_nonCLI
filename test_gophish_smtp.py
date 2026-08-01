import httpx, asyncio

async def test():
    headers = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    base = 'https://127.0.0.1:3333/api'
    async with httpx.AsyncClient(verify=False, timeout=10) as c:
        # Get SMTP by ID
        r = await c.get(f'{base}/smtp/1', headers=headers)
        print(f"SMTP 1: {r.status_code} {r.text[:500]}")
        
        # Try creating a NEW SMTP profile
        r = await c.post(f'{base}/smtp/', headers=headers, json={
            'name': 'Test SMTP 2',
            'interface_type': 'SMTP',
            'from_address': 'test@phishguard.ai',
            'host': 'localhost',
            'username': '',
            'password': '',
            'port': 25,
            'ignore_cert_errors': True
        })
        print(f"Create SMTP: {r.status_code}")
        if r.status_code < 400:
            smtp2 = r.json()
            smtp2_id = smtp2.get('id')
            print(f"SMTP 2 created: id={smtp2_id}")
            
            # Now try creating a campaign with this SMTP
            payload = {
                'name': 'TestCampaign-Final',
                'groups': [{'id': 8}],
                'page': {'id': 6},
                'template': {'id': 6},
                'smtp': {'id': smtp2_id},
                'url': 'http://localhost:8080',
            }
            r = await c.post(f'{base}/campaigns/', headers=headers, json=payload)
            print(f"Campaign with new SMTP: {r.status_code} {r.text[:500]}")

asyncio.run(test())
