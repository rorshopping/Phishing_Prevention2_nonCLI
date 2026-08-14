# Live Vishing (Azure Speech) — Setup To-Do

This project supports **live conversational vishing**: Twilio streams the call audio
to this app, Azure Speech does real-time German STT + TTS, and the LLM acts as the
vishing caller persona. Falls back to the older IVR (DTMF) flow when not configured.

## 1. Prerequisites

| Item | Config key | Notes |
|---|---|---|
| Azure Speech resource (key + region) | `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` | Free tier / trial credit $200 |
| Public HTTPS URL of this app | `APP_BASE_URL` | Twilio must reach `/ws/vishing/...` and `/tts/...` |
| Twilio account + verified outgoing number | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` | Already configured? |
| Live mode on | `VISHING_LIVE=true` | Default is `true` |

The live path only activates when **all** of these are present:

```
TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN  (set)
VISHING_LIVE=true
AZURE_SPEECH_KEY
APP_BASE_URL
```

If any is missing, `POST /vishing/trigger` automatically falls back to the IVR flow,
then to simulation.

## 2. Get the Azure Speech key

1. Go to the **Azure Portal** → create (or open) a **Speech** resource
   (`Speech service`), pick a region (this setup: `swedencentral`).
   Resource name: `richardbaecker-9429-resource`.
2. In the resource blade, open **Keys and Endpoint**.
3. Copy **Key 1** into `AZURE_SPEECH_KEY` and the region into `AZURE_SPEECH_REGION`.
   - The **Speech Studio** playground itself does not give you a key — the key lives
     in the Azure Portal under the Speech resource you select at the top of Speech Studio.
4. Optional: set a German neural voice, e.g. `AZURE_SPEECH_VOICE=de-DE-ConradNeural`
   (male) or `de-DE-KatjaNeural` (female).

> **Note:** you do NOT need a "deployment name", "model name", or the
> `cognitiveservices.azure.com` endpoint. The SDK connects by subscription key + region only.

## 3. Make the app publicly reachable (APP_BASE_URL)

Twilio needs a public HTTPS/WSS endpoint. For local testing, use a tunnel.

**Chosen: Cloudflare quick tunnel** (no account needed). Install:

```powershell
winget install --id Cloudflare.cloudflared
# binary lands at: C:\Program Files (x86)\cloudflared\cloudflared.exe
```

Start the app, then the tunnel:

```powershell
# terminal 1 — app (detached variant used below)
uvicorn src.main:app --host 0.0.0.0 --port 8000

# terminal 2 — tunnel
& "C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --url http://127.0.0.1:8000
```

The tunnel prints a URL like `https://<random>.trycloudflare.com` to the log.
Copy it into `.env`:

```
APP_BASE_URL=https://<random>.trycloudflare.com
```

For production, set `APP_BASE_URL` to the deployed HTTPS domain. No trailing slash.

> **The trycloudflare URL is ephemeral** — it changes every time `cloudflared`
> restarts. After a restart, update `APP_BASE_URL` in `.env` and restart uvicorn
> (settings are read at process start).

## 4. `.env` example

```
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+491234567890

AZURE_SPEECH_KEY=...
AZURE_SPEECH_REGION=germanywestcentral
AZURE_SPEECH_VOICE=de-DE-ConradNeural

APP_BASE_URL=https://xxxx.ngrok-free.app
VISHING_LIVE=true
```

## 5. Run + test

```powershell
$env:PYTHONPATH = "C:\Users\Richard\Documents\Projects\Phishing_Prevention2_nonCLI"
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Trigger a live call:

```powershell
curl -X POST http://127.0.0.1:8000/vishing/trigger `
  -H "Content-Type: application/json" `
  -d '{"employee_id":"<uuid>","scenario":"tech_support"}'
```

Expected: response has `"live": true`, the employee receives a call, the AI starts
the conversation in German. If the employee says their password / PIN / username,
`sensitive_info_disclosed` flips to `true` and the call ends.

## 6. Verify the WebSocket path

- Live TwiML uses
  `<Connect><Stream url="wss://{APP_BASE_URL}/vishing/ws/vishing/{session_id}">`
  (the `vishing` API router has `prefix="/vishing"`, so the full WS route is
  `/vishing/ws/vishing/{session_id}` — omit the prefix and the request falls
  through to StaticFiles and gets an HTTP 500 handshake).
- The WebSocket handler is `GET /vishing/ws/vishing/{session_id}` in
  `src/api/vishing.py`.
- The conversation loop lives in `src/services/live_voice.py`
  (`LiveVishingCaller`): Azure STT → LLM persona → Azure TTS → Twilio stream.
- Test the WS without a phone call (dashless UUID in DB, dashed in URL path):
  ```python
  import asyncio, websockets, json
  async def m():
      url = "wss://{APP_BASE_URL}/vishing/ws/vishing/{dashed-uuid}"
      async with websockets.connect(url, open_timeout=15) as ws:
          await ws.send(json.dumps({"event": "start", "start": {
              "callSid": "CA-test", "streamSid": "ST-test",
              "customParameters": {"scenario": "tech_support"}}}))
          print(await asyncio.wait_for(ws.recv(), timeout=15))  # {"event":"connected",...}
      asyncio.run(m())
  ```

## 8. Current setup state (Aug 2026)

Status of the live-vishing wiring:

| Item | Value / status |
|---|---|
| `AZURE_SPEECH_REGION` | `swedencentral` (resource `richardbaecker-9429-resource`) |
| `AZURE_SPEECH_VOICE` | `de-DE-ConradNeural` |
| `AZURE_SPEECH_KEY` | set |
| `APP_BASE_URL` | `https://continued-lexington-ward-civilian.trycloudflare.com` |
| `VISHING_LIVE` | `true` |
| `TWILIO_ACCOUNT_SID / AUTH_TOKEN` | set (master account creds) |
| `TWILIO_PHONE_NUMBER` | `+4915888623971` (trial number) |
| Test destination | `+4915783603386` (verified) |
| App | running on port 8000 (uvicorn) |
| Tunnel | running (cloudflared) |

Background processes (as of 2026-08-01):

```powershell
# uvicorn (app)        PID 18892
# cloudflared (tunnel) PID 8824
```

Tear down:

```powershell
Stop-Process -Id 8824,18892 -Force
```

**Blocker:** the WS/Azure/LLM/TTS pipeline is fully working (verified by connecting
to the WS with a test client and receiving the `connected` event), but real calls
placed via the **Twilio trial account are refused by Twilio** — see §9.

## 9. Twilio trial account restriction (documented 2026-08-01)

Twilio's free **trial** account will not place real vishing-style outbound calls.
Empirically observed:

- The call rings, the recipient answers, hears
  **"This is a test call from Twilio"**, and the call drops after ~2 seconds.
- Twilio **fetches the TwiML** from our `/webhooks/vishing/twiml` (HTTP 200), but the
  `<Connect><Stream>` WebSocket connection **never reaches our server**
  (no `WebSocket /vishing/ws/vishing/...` log line) — Twilio terminates the call.
- The trial account announcement + drop is Twilio's own anti-abuse / trial gating of
  automated outbound calls. It is not a bug in our code (the WS path is independently
  proven to work through the same tunnel).

Trial restrictions hit along the way (all verified empirically via API):

| Restriction | Detail |
|---|---|
| Inline `Twiml` in `Calls.create()` | Disallowed (error 0, "trial accounts have limited parameter access"); must pass a hosted `Url` |
| `Record=true` | Also disallowed on trial |
| Purchasing numbers | Not possible via API/CLI — only the Console "Get a trial number" button |
| Media Streams / WebSocket | Call dropped before the stream connects; trial does not allow real streamed calls |
| Some read APIs | `AvailablePhoneNumbers`, `OutgoingCallerIds`, `Notifications` return 20003 "Policy evaluation failed" |

**Consequence:** real outbound vishing calls are not possible on the free trial.
Options (in order of practicality):

1. **Add funds / upgrade the Twilio account** — removes the announcement and lets the
   Media Stream connect. Only reliable way to place live calls via Twilio.
2. **Different carrier** (Telnyx, Plivo, AWS Chime, a German VoIP provider) — needs a
   paid number; same general anti-spam policies apply.
3. **Simulation path** — with `VISHING_LIVE=false` or no Twilio keys,
   `POST /vishing/trigger` runs `_simulate_call` (no real phone involved). The live
   pipeline can still be exercised end-to-end with the WS test client in §6.

For a real phishing-simulation product, note: carriers treat automated scam-style
calls as abuse, so a production vishing service needs employee consent + a carrier
that permits security-simulation calls.

## 7. Troubleshooting

- **Call rings, then hangs up silently** → check the app is reachable at
  `wss://{APP_BASE_URL}/vishing/ws/vishing/...` (ngrok requires `https`).
- **Recipient hears "This is a test call from Twilio" then drops** → Twilio trial
  account gating; see §9. Not a code bug.
- **No audio played** → `AZURE_SPEECH_KEY` missing / invalid; check logs for
  "Live TTS failed".
- **STT returns nothing** → confirm `AZURE_SPEECH_REGION` matches the key's region.
- **Call not placed** → Twilio number not verified / out of trial credit.
- **Security note**: the `/ws/vishing/{id}` and `/webhooks/vishing/gather`
  endpoints are unauthenticated. Add Twilio request validation
  (`X-Twilio-Signature` HMAC with `app_secret_key`) before production.
