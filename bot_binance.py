import os, time, hmac, hashlib, requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()
BASE = os.getenv("BINANCE_BASE","https://api.binance.us").rstrip("/")
KEY  = os.getenv("BINANCE_API_KEY","").strip()
SEC  = os.getenv("BINANCE_API_SECRET","").strip()
LIVE = (os.getenv("TRADING_ENABLED","false").lower()=="true")

def _sign(d):
    qs = urlencode(d)
    sig = hmac.new(SEC.encode(), qs.encode(), hashlib.sha256).hexdigest()
    return qs, sig

def price(symbol="BTCUSDT"):
    return float(requests.get(f"{BASE}/api/v3/ticker/price",
                              params={"symbol":symbol}, timeout=10).json()["price"])

def usdt_balance():
    ts=int(time.time()*1000); qs,sig=_sign({"timestamp":ts,"recvWindow":10000})
    r=requests.get(f"{BASE}/api/v3/account?{qs}&signature={sig}",
                   headers={"X-MBX-APIKEY":KEY}, timeout=15).json()
    for b in r.get("balances", []):
        if b["asset"]=="USDT": return float(b["free"])
    return 0.0

def place_limit_buy(symbol, qty, px):
    if not LIVE:
        print(f"[DRY RUN] BUY {symbol} {qty} @ {px}")
        return {"dry_run":True}
    ts=int(time.time()*1000)
    p={"symbol":symbol,"side":"BUY","type":"LIMIT","timeInForce":"GTC",
       "quantity":str(qty),"price":str(px),"timestamp":ts,"recvWindow":10000}
    qs,sig=_sign(p)
    r=requests.post(f"{BASE}/api/v3/order?{qs}&signature={sig}",
                    headers={"X-MBX-APIKEY":KEY}, timeout=15)
    print("Order status:", r.status_code, r.text[:200]); return r.json()

if __name__=="__main__":
    symbol="BTCUSDT"
    while True:
        try:
            p = price(symbol)
            u = usdt_balance()
            print(f"{symbol}={p} | USDT free={u}")
            # demo rule (not a strategy): try a tiny buy when price ends with ".0"
            if str(p).endswith(".0") and u > 25:
                qty = round(20/p, 6)           # ~$20
                px  = round(p*0.999, 2)        # 0.1% under
                place_limit_buy(symbol, qty, px)
        except Exception as e:
            print("Loop error:", e)
        time.sleep(10)
