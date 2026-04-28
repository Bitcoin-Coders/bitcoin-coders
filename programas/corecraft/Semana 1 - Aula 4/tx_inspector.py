import os
import requests
from bitcoin.core import CTransaction, b2lx

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:58443")
RPC_USER = os.getenv("RPC_USER", "teste")
RPC_PASS = os.getenv("RPC_PASS", "teste")


def rpc_call(method, params=None):
    payload = {
        "jsonrpc": "1.0",
        "id": "corecraft",
        "method": method,
        "params": params or []
    }
    r = requests.post(RPC_URL, auth=(RPC_USER, RPC_PASS), json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("error"):
        raise RuntimeError(data["error"])
    return data["result"]


def summarize_tx(raw_hex: str):
    # Parse da transação a partir do hex
    tx = CTransaction.deserialize(bytes.fromhex(raw_hex))

    # TXID
    txid = b2lx(tx.GetTxid())

    vin_count = len(tx.vin)
    vout_count = len(tx.vout)
    total_out_sats = sum(int(v.nValue) for v in tx.vout)

    # Tamanho em bytes da serialização (didático)
    size_bytes = len(tx.serialize())

    return {
        "txid": txid,
        "vin": vin_count,
        "vout": vout_count,
        "total_out_sats": total_out_sats,
        "size_bytes": size_bytes,
    }


def main():
    best_hash = rpc_call("getbestblockhash")
    block = rpc_call("getblock", [best_hash, 2])  # verbosity=2 inclui hex das txs

    print("Bloco:", best_hash)
    print("Altura:", block["height"])
    print("Txs:", len(block["tx"]))
    print("----")

    for i, txinfo in enumerate(block["tx"][:10]):
        s = summarize_tx(txinfo["hex"])

        print(
            f"[{i}] {s['txid']} "
            f"vin={s['vin']} "
            f"vout={s['vout']} "
            f"total_out={s['total_out_sats']} sats "
            f"size={s['size_bytes']}B"
        )


if __name__ == "__main__":
    main()

