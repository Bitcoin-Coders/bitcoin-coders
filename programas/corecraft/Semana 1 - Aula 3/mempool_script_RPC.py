import time
import requests
from requests.auth import HTTPBasicAuth

RPC_URL = "http://127.0.0.1:58443"
AUTH = HTTPBasicAuth("teste", "teste")

def rpc(method, params=[]):
    payload = {
        "jsonrpc": "1.0",
        "id": "corecraft",
        "method": method,
        "params": params
    }
    r = requests.post(RPC_URL, json=payload, auth=AUTH)
    return r.json()["result"]

while True:
    info = rpc("getmempoolinfo")
    print(
        f"txs={info['size']} | "
        f"bytes={info['bytes']} | "
        f"total_fee={info['total_fee']}"
    )
    time.sleep(10)

