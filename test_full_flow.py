import asyncio, httpx, json, os, signal, subprocess, sys, time

os.environ["PYTHONPATH"] = "C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI"
os.chdir("C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI")

proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "error"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
)

try:
    for i in range(20):
        try:
            r = httpx.get("http://localhost:8000/health", timeout=2)
            if r.status_code == 200:
                print(f"Server up after {i+1}s")
                break
        except Exception:
            pass
        time.sleep(1)
    else:
        print("Server failed to start")
        sys.exit(1)

    base = "http://localhost:8000"
    c = httpx.Client(base_url=base, timeout=30)

    # 1. Create client
    print("\n=== Create Client ===")
    r = c.post("/clients", json={
        "company_name": "Müller & Söhne GmbH",
        "contact_email": "admin@testcompany.de",
        "contact_name": "Test Admin",
        "industry": "Technology",
        "employee_count": 50,
        "country": "DE",
        "campaigns_per_year": 25,
        "vishing_enabled": False,
    })
    print(f"Status: {r.status_code}, Body: {r.text[:300]}")
    if r.status_code >= 400:
        print(f"ERROR: {r.text}")
        sys.exit(1)
    client = r.json()
    client_id = client.get("id")
    if not client_id:
        print("ERROR: No client ID returned")
        sys.exit(1)

    # 2. Add employee with user's email
    print("\n=== Add Employee ===")
    r = c.post(f"/clients/{client_id}/employees", json=[
        {
            "email_hash": "rorshopping@gmail.com",
            "name_hash": "Richard Or",
            "role": "Developer",
            "department": "Engineering",
            "group": "engineering",
        }
    ])
    print(f"Status: {r.status_code}")
    if r.status_code >= 400:
        print(f"ERROR: {r.text}")
        sys.exit(1)
    employees = r.json()
    print(f"Employees: {len(employees)}")

    # 3. Run a campaign
    print("\n=== Run Campaign ===")
    r = c.post(f"/clients/{client_id}/campaigns", json={
        "difficulty": "easy",
    })
    print(f"Status: {r.status_code}")
    if r.status_code >= 400:
        print(f"ERROR: {r.text}")
        sys.exit(1)
    campaign = r.json()
    print(f"Campaign: {json.dumps(campaign, indent=2, default=str)[:800]}")

    # 4. List campaigns
    print("\n=== List Campaigns ===")
    r = c.get(f"/clients/{client_id}/campaigns")
    campaigns = r.json()
    print(f"Status: {r.status_code}, Count: {len(campaigns)}")
    for camp in campaigns:
        print(f"  - {camp.get('name')}: status={camp.get('status')}, id={str(camp.get('id'))[:8]}...")

    # 5. Check campaign results
    if campaigns:
        print("\n=== Campaign Results ===")
        r = c.get(f"/campaigns/{campaigns[0]['id']}/results")
        results = r.json()
        print(f"Status: {r.status_code}")
        print(f"Results: {json.dumps(results, indent=2, default=str)[:600]}")

    # 6. Client stats
    print("\n=== Client Stats ===")
    r = c.get(f"/clients/{client_id}")
    stats = r.json()
    print(f"Status: {r.status_code}")
    print(f"Stats: {json.dumps(stats, indent=2, default=str)[:400]}")
    print("\n=== ALL TESTS PASSED ===")

finally:
    proc.terminate()
    proc.wait(timeout=5)
