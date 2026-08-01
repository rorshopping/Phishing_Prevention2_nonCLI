import httpx, asyncio, json

async def test():
    headers = {'Authorization': 'Bearer 50e88428b65db1b165d02ffb6c06d15f', 'Content-Type': 'application/json', 'Accept': 'application/json'}
    base = 'https://127.0.0.1:3333/api'
    async with httpx.AsyncClient(verify=False, timeout=10) as c:
        # Create a proper template
        r = await c.post(f'{base}/templates/', headers=headers, json={
            'name': 'ProperTemplate',
            'subject': 'Important: Action Required',
            'html': '<html><body><p>Dear Employee,</p><p>Please <a href="{{.URL}}">click here</a> to review.</p><p>Thank you.</p></body></html>',
            'text': 'Dear Employee, please click here: {{.URL}}',
        })
        print(f"Template create: {r.status_code}")
        tpl = r.json()
        tpl_id = tpl.get('id')
        print(f"Template ID: {tpl_id}")

        # Create group with the user's email
        r = await c.post(f'{base}/groups/', headers=headers, json={
            'name': 'GroupForUser',
            'targets': [{'email': 'rorshopping@gmail.com', 'first_name': 'Richard', 'last_name': 'Or', 'position': 'Developer'}],
        })
        group = r.json()
        gid = group.get('id')
        print(f"Group ID: {gid}")

        # Create proper page
        r = await c.post(f'{base}/pages/', headers=headers, json={
            'name': 'ProperPage',
            'html': '<html><body><h2>Sign in</h2><form><input name="email"/><input name="password" type="password"/><button>Sign In</button></form></body></html>',
            'capture_credentials': True,
            'capture_passwords': True,
        })
        page = r.json()
        pid = page.get('id')
        print(f"Page ID: {pid}")

        # Now create campaign with these
        payload = {
            'name': 'TestCampaign-New',
            'groups': [{'id': gid}],
            'page': {'id': pid},
            'template': {'id': tpl_id},
            'smtp': {'id': 2},
            'url': 'http://localhost:8080',
        }
        print(f"\nPayload: {json.dumps(payload, indent=2)}")
        r = await c.post(f'{base}/campaigns/', headers=headers, json=payload)
        print(f"Campaign: {r.status_code}")
        print(r.text[:500])

        if r.status_code < 400:
            camp = r.json()
            print(f"Campaign created! ID: {camp.get('id')}")

asyncio.run(test())
