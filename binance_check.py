import os, time, hmac, hashlib, json
from pathlib import Path
from urllib.parse import urlencode
import requests
from dotenv import load_dotenv

# Load .env from the same folder
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

BASE = os.getenv("BINANCE_BASE", "https://api.binance.us").rstrip("/")
KEY  = (os.getenv("BINANCE_API_KEY") or "").strip()
SEC  = (os.getenv("BINANCE_API_SECRET") or "").strip()

print("Using BASE:", BASE)
print("Key present?:", bool(KEY), "| Secret present?:", bool(SEC))

# Public sanity check
t_resp = requests.get(f"{BASE}/api/v3/time", timeout=10)
print("Public /time:", t_resp.status_code, t_resp.text[:120])
server_time = t_resp.json().get("serverTime")

# ---- signed /account request ----
params = {"timestamp": server_time, "recvWindow": 10000}
qs = urlencode(params)
sig = hmac.new(SEC.encode(), qs.encode(), hashlib.sha256).hexdigest()
headers = {"X-MBX-APIKEY": KEY}

r = requests.get(
    f"{BASE}/api/v3/account?{qs}&signature={sig}",
    headers=headers,
    timeout=15,
)

print("Auth /account status:", r.status_code)

# Pretty output: show only non-zero balances or the error body
if r.ok:
    data = r.json()
    nz = [b for b in data.get("balances", []) if float(b["free"]) or float(b["locked"])]
    print(f"Nonzero balances: {len(nz)}")
    for b in nz[:25]:
        print(f"  {b['asset']}: free={b['free']} locked={b['locked']}")
else:
    try:
        print("Error body:", json.dumps(r.json(), indent=2)[:800])
    except Exception:
        print("Error body (raw):", r.text[:800])
