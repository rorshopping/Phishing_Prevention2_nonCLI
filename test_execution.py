import asyncio, httpx, json, sys

async def test():
    # Test Gophish connectivity
    gophish_url = "https://127.0.0.1:3333/api"
    api_key = "50e88428b65db1b165d02ffb6c06d15f"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(verify=False, timeout=10) as c:
        # List existing groups
        r = await c.get(f"{gophish_url}/groups/", headers=headers)
        print(f"GET /groups/: {r.status_code}")
        if r.status_code < 400:
            groups = r.json()
            print(f"  Groups count: {len(groups)}")
            for g in groups:
                print(f"  - id={g.get('id')} name={g.get('name')} targets={len(g.get('targets', []))}")

        # List templates
        r = await c.get(f"{gophish_url}/templates/", headers=headers)
        print(f"GET /templates/: {r.status_code}")
        if r.status_code < 400:
            templates = r.json()
            print(f"  Templates count: {len(templates)}")

        # List pages
        r = await c.get(f"{gophish_url}/pages/", headers=headers)
        print(f"GET /pages/: {r.status_code}")
        if r.status_code < 400:
            pages = r.json()
            print(f"  Pages count: {len(pages)}")

        # List SMTP profiles
        r = await c.get(f"{gophish_url}/smtp/", headers=headers)
        print(f"GET /smtp/: {r.status_code}")
        if r.status_code < 400:
            smtp = r.json()
            print(f"  SMTP profiles count: {len(smtp)}")
            for s in smtp:
                print(f"  - id={s.get('id')} name={s.get('name')} host={s.get('host')}")

        # List campaigns
        r = await c.get(f"{gophish_url}/campaigns/", headers=headers)
        print(f"GET /campaigns/: {r.status_code}")
        if r.status_code < 400:
            camps = r.json()
            print(f"  Campaigns count: {len(camps)}")

        # Try creating a simple group
        print("\n--- Creating test group ---")
        r = await c.post(f"{gophish_url}/groups/", headers=headers, json={
            "name": "TestGroup-Simple",
            "targets": [{"email": "test@example.com", "first_name": "Test", "last_name": "User"}]
        })
        print(f"Create group: {r.status_code}")
        print(f"Response: {r.text[:500]}")
        if r.status_code < 400:
            group = r.json()
            print(f"Group created with id={group.get('id')}")

        # Check if Gophish is accessible at all
        r = await c.get(f"{gophish_url}/", headers=headers)
        print(f"\nGET /: {r.status_code}")
        if r.status_code < 400:
            print(f"Response: {r.text[:500]}")

asyncio.run(test())
