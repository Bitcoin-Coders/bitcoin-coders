import os
import time
import threading
from dataclasses import dataclass, asdict
from collections import deque

import zmq
import requests
from flask import Flask, jsonify, send_from_directory

# ----------------------------
# Config (env vars)
# ----------------------------
BITCOIN_RPC_URL = os.getenv("BITCOIN_RPC_URL", "http://127.0.0.1:58443")
BITCOIN_RPC_USER = os.getenv("BITCOIN_RPC_USER", "teste")
BITCOIN_RPC_PASS = os.getenv("BITCOIN_RPC_PASS", "teste")

ZMQ_HASHBLOCK = os.getenv("ZMQ_HASHBLOCK", "tcp://127.0.0.1:58335")
ZMQ_HASHTX = os.getenv("ZMQ_HASHTX", "tcp://127.0.0.1:58332")

MAX_BLOCK_EVENTS = int(os.getenv("MAX_BLOCK_EVENTS", "25"))
MAX_TX_EVENTS = int(os.getenv("MAX_TX_EVENTS", "60"))

# ----------------------------
# Estado derivado em RAM
# ----------------------------
@dataclass
class Event:
    topic: str
    value: str
    ts: float

class InMemoryState:
    def __init__(self):
        self.lock = threading.Lock()
        self.blocks = deque(maxlen=MAX_BLOCK_EVENTS)
        self.txs = deque(maxlen=MAX_TX_EVENTS)
        self.count_blocks = 0
        self.count_txs = 0
        self.last_zmq_ts = None
        self.last_seen_blockhash = None
        self.last_seen_block_ts = None

STATE = InMemoryState()

# ----------------------------
# RPC helper
# ----------------------------
_rpc_id = 0
def rpc_call(method: str, params=None):
    global _rpc_id
    _rpc_id += 1
    payload = {
        "jsonrpc": "1.0",
        "id": _rpc_id,
        "method": method,
        "params": params or []
    }
    r = requests.post(
        BITCOIN_RPC_URL,
        auth=(BITCOIN_RPC_USER, BITCOIN_RPC_PASS),
        json=payload,
        timeout=6
    )
    r.raise_for_status()
    j = r.json()
    if j.get("error"):
        raise RuntimeError(j["error"])
    return j["result"]

# ----------------------------
# ZMQ  (threads)
# ----------------------------
def _zmq_subscribe(topic: str, endpoint: str):
    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.SUB)
    sock.connect(endpoint)
    sock.setsockopt(zmq.SUBSCRIBE, topic.encode("utf-8"))

    while True:
        try:
            frames = sock.recv_multipart()
            # frames tipicamente: [topic, body, sequence]
            topic_b = frames[0]
            body = frames[1]

            topic_s = topic_b.decode("utf-8", errors="replace")
            value_hex = body.hex()
            now = time.time()

            ev = Event(topic=topic_s, value=value_hex, ts=now)

            with STATE.lock:
                STATE.last_zmq_ts = now

                if topic_s == "hashblock":
                    STATE.blocks.appendleft(ev)
                    STATE.count_blocks += 1
                    STATE.last_seen_blockhash = value_hex
                    STATE.last_seen_block_ts = now
                elif topic_s == "hashtx":
                    STATE.txs.appendleft(ev)
                    STATE.count_txs += 1

        except Exception:
            # Mantém resiliente para mentoria (em prod: logging de verdade)
            time.sleep(0.2)

def start_zmq_threads():
    t1 = threading.Thread(target=_zmq_subscribe, args=("hashblock", ZMQ_HASHBLOCK), daemon=True)
    t2 = threading.Thread(target=_zmq_subscribe, args=("hashtx", ZMQ_HASHTX), daemon=True)
    t1.start()
    t2.start()

# ----------------------------
# Flask (serve frontend e API)
# ----------------------------
app = Flask(__name__, static_folder="../frontend", static_url_path="")

@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/styles.css")
def styles():
    return send_from_directory(app.static_folder, "styles.css")

@app.get("/app.js")
def js():
    return send_from_directory(app.static_folder, "app.js")

@app.get("/api/health")
def health():
    rpc_ok = False
    rpc_err = None
    try:
        rpc_call("getblockchaininfo")
        rpc_ok = True
    except Exception as e:
        rpc_err = str(e)

    with STATE.lock:
        last_zmq_ts = STATE.last_zmq_ts

    now = time.time()
    zmq_age_s = None if last_zmq_ts is None else round(now - last_zmq_ts, 3)

    return jsonify({
        "ok": True,
        "rpc_ok": rpc_ok,
        "rpc_error": rpc_err,
        "zmq_last_event_age_s": zmq_age_s,
        "server_time": now
    })

@app.get("/api/state")
def state():
    # Foto via RPC
    rpc_error = None
    bestblockhash = None
    chaininfo = None
    mempoolinfo = None

    try:
        bestblockhash = rpc_call("getbestblockhash")
        chaininfo = rpc_call("getblockchaininfo")
        mempoolinfo = rpc_call("getmempoolinfo")
    except Exception as e:
        rpc_error = str(e)

    # Fluxo via ZMQ
    with STATE.lock:
        blocks = [asdict(ev) for ev in list(STATE.blocks)]
        txs = [asdict(ev) for ev in list(STATE.txs)]
        count_blocks = STATE.count_blocks
        count_txs = STATE.count_txs
        last_seen_blockhash = STATE.last_seen_blockhash
        last_seen_block_ts = STATE.last_seen_block_ts

    divergence = None
    if bestblockhash and last_seen_blockhash:
        divergence = (bestblockhash != last_seen_blockhash)

    return jsonify({
        "rpc": {
            "bestblockhash": bestblockhash,
            "height": chaininfo.get("blocks") if chaininfo else None,
            "chain": chaininfo.get("chain") if chaininfo else None,
            "mempool_size": mempoolinfo.get("size") if mempoolinfo else None,
            "error": rpc_error
        },
        "zmq": {
            "last_seen_blockhash": last_seen_blockhash,
            "last_seen_block_ts": last_seen_block_ts,
            "counters": {
                "block_events": count_blocks,
                "tx_events": count_txs
            },
            "blocks": blocks,
            "txs": txs
        },
        "analysis": {
            "bestblock_vs_last_seen_diverged": divergence,
            "note": "Divergência pode ser latência, reorg, out-of-order, ou timing do polling."
        },
        "server_time": time.time()
    })

def main():
    start_zmq_threads()
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)

if __name__ == "__main__":
    main()

