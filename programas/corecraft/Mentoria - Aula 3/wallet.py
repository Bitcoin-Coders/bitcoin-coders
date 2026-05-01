# wallet.py

from rpc import BitcoinRPC

rpc = BitcoinRPC(
    "http://127.0.0.1:58443",
    "teste",
    "teste"
)

def get_utxos():
    return rpc.call("listunspent", [1, 9999999])

def get_new_address():
    return rpc.call("getnewaddress")

def get_balance():
    return rpc.call("getbalance")
