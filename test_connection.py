import os
from pathlib import Path
from dotenv import load_dotenv
import requests

# Load .env from the same folder as this script (bullet-proof)
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

for k in ["BINANCE_API_KEY","BINANCE_API_SECRET","COINBASE_API_KEY","COINBASE_API_SECRET"]:
    v = os.getenv(k)
    print(k, "OK" if v else "MISSING", (v[:6] + "…") if v else "")
print("Binance public time:", requests.get("https://api.binance.com/api/v3/time", timeout=10).json())
print("Coinbase public time:", requests.get("https://api.coinbase.com/v2/time", timeout=10).json())
