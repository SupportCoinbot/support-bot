# gemini_check.py — public price + signed balances
import os, time, json, base64, hmac, hashlib, requests
from dotenv import load_dotenv

load_dotenv()
BASE   = os.getenv("GEMINI_BASE", "https://api.gemini.com").rstrip("/")
KEY    = os.getenv("GEMINI_API_KEY", "").strip()
SECRET = (os.getenv("GEMINI_API_SECRET", "")).encode()

def g_public_price(symbol="btcusd"):
    r = requests.get(f"{BASE}/v1/pubticker/{symbol}", timeout=10)
    r.raise_for_status()
    return float(r.json()["last"])

def _signed_post(path: str, payload: dict):
    payload["request"] = path
    payload["nonce"]   = str(int(time.time()*1000))
    b64 = base64.b64encode(json.dumps(payload).encode()).decode()
    sig = hmac.new(SECRET, b64.encode(), hashlib.sha384).hexdigest()
    headers = {
        "Content-Type": "text/plain",
        "X-GEMINI-APIKEY": KEY,
        "X-GEMINI-PAYLOAD": b64,
        "X-GEMINI-SIGNATURE": sig,
        "Cache-Control": "no-cache",
    }
    return requests.post(BASE + path, headers=headers, timeout=15)

if __name__ == "__main__":
    print("BASE:", BASE)
    print("Key present?", bool(KEY), "| Secret present?", bool(SECRET))
    # Public price test
    try:
        print("Public BTC/USD:", g_public_price("btcusd"))
    except Exception as e:
        print("Public price error:", e)

    # Signed balances
    r = _signed_post("/v1/balances", {})
    print("Auth /v1/balances status:", r.status_code)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text[:400]}
    if r.ok:
        nz = [a for a in data if float(a.get("available", "0") or 0) > 0 or float(a.get("amount", "0") or 0) > 0]
        print("Nonzero balances:", len(nz))
        for a in nz[:20]:
            print(f"  {a.get('currency')}: available={a.get('available')} total={a.get('amount')}")
    else:
        print("Error:", data)
