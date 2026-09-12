import asyncio, httpx

async def test():
    headers = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    base = 'https://127.0.0.1:3333/api'
    
    async with httpx.AsyncClient(verify=False, timeout=10) as c:
        # Create a page
        r = await c.post(f'{base}/pages/', headers=headers, json={
            'name': 'TestPage-Debug',
            'html': '<html><body><h2>Sign in</h2><form><input name="email"/><input name="password" type="password"/><button>Sign In</button></form></body></html>',
            'capture_credentials': True,
            'capture_passwords': True,
        })
        page = r.json()
        print(f'Page created: id={page.get("id")}')
        print(f'  Response: {page}')

        # Create a template
        r = await c.post(f'{base}/templates/', headers=headers, json={
            'name': 'TestTemplate-Debug',
            'subject': 'Test Subject',
            'html': '<html><body><a href="{{.URL}}">Click here</a></body></html>',
            'text': 'Click here: {{.URL}}',
        })
        tpl = r.json()
        print(f'\nTemplate created: id={tpl.get("id")}')
        print(f'  Response: {tpl}')

        # Create a group
        r = await c.post(f'{base}/groups/', headers=headers, json={
            'name': 'TestGroup-Debug',
            'targets': [{'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}],
        })
        group = r.json()
        print(f'\nGroup created: id={group.get("id")}')

        # Create a campaign
        payload = {
            'name': 'TestCampaign-Debug',
            'groups': [{'id': group.get('id')}],
            'page': {'id': page.get('id')},
            'template': {'id': tpl.get('id')},
            'url': 'http://localhost:8080',
        }
        print(f'\nCampaign payload: {payload}')
        r = await c.post(f'{base}/campaigns/', headers=headers, json=payload)
        print(f'Campaign response: {r.status_code} {r.text[:500]}')

        if r.status_code < 400:
            camp = r.json()
            print(f'Campaign created: id={camp.get("id")}')

asyncio.run(test())
