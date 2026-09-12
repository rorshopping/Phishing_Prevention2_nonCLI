import httpx, json, os

api_key = os.getenv("LLM_API_KEY", "")

r = httpx.get("https://openrouter.ai/api/v1/models", headers={
    "Authorization": f"Bearer {api_key}",
}, timeout=15)
models = r.json().get("data", [])
free = [m for m in models if m.get("id", "").endswith(":free")]
print(f"Total free models: {len(free)}")
for m in sorted(free, key=lambda x: x["id"]):
    print(f"  {m['id']} - {m.get('name','')}")

# Test each one
for m in free[:5]:
    slug = m["id"]
    try:
        r2 = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": slug, "messages": [{"role": "user", "content": "say hello in 3 words"}], "max_tokens": 30},
            timeout=30,
        )
        data = r2.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        reasoning = data.get("choices", [{}])[0].get("message", {}).get("reasoning", "")
        print(f"  --> {slug}: content={repr(content)[:80]} reasoning={repr(reasoning)[:80]}")
    except Exception as e:
        print(f"  --> {slug}: error={e}")
