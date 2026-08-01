import httpx

ak = '50e88428b65db1b165d02ffb6c06d15f'
h = {'Authorization': f'Bearer {ak}', 'Content-Type': 'application/json'}
base = 'https://127.0.0.1:3333/api'
cl = httpx.Client(verify=False, headers=h, follow_redirects=True)

# Create SMTP profile with Gmail
smtp = {
    "name": "Gmail SMTP",
    "interface_type": "SMTP",
    "host": "smtp.gmail.com",
    "port": 587,
    "from_address": "rorshopping@gmail.com",
    "username": "rorshopping@gmail.com",
    "password": "eibr kyda mrls pkst",
    "ignore_cert_errors": False,
}

resp = cl.post(f'{base}/smtp/', json=smtp, timeout=10)
print(f'SMTP create: {resp.status_code}')
if resp.status_code in (200, 201):
    sid = resp.json()['id']
    print(f'SMTP profile ID: {sid}')
else:
    print(f'Error: {resp.text}')

cl.close()
