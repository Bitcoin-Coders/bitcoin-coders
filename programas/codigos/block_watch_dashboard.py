import os
import time
import json
import threading
from datetime import datetime, timezone

import zmq
import requests
from flask import Flask, jsonify, render_template_string

# =========================
# Config
# =========================
ZMQ_URL = os.getenv("ZMQ_URL","tcp://127.0.0.1:18144")
RPC_URL = os.getenv("RPC_URL","http://127.0.0.1:18113")
RPC_USER = os.getenv("RPC_USER","teste")
RPC_PASS = os.getenv("RPC_PASS","teste")

# =========================
# Estado em memória (último bloco observado)
# =========================
STATE = {
"last_seen_at":None,
"best_height":None,
"block_hash":None,
"block_time":None,
"tx_count":None,
"total_out_sats":None,
"total_fee_sats":None,
"avg_fee_rate_sat_vb":None,
}

# =========================
# Converte LE e BE
# =========================
def decode_hashblock(body: bytes) -> str:
    """
    ZMQ hashblock: em geral vem little-endian. Mas, para evitar pegadinha,
    tentamos as duas formas e escolhemos a que o RPC reconhece.
    """
    h_be = body.hex()
    h_rev = body[::-1].hex()

    # Tenta validar com getblockheader (barato)
    try:
        rpc_call("getblockheader", [h_rev])
        return h_rev
    except Exception:
        pass

    try:
        rpc_call("getblockheader", [h_be])
        return h_be
    except Exception:
        pass

    # Se nenhuma funcionar, devolve a reversa (mais comum) e deixa o erro aparecer no log
    return h_rev


# =========================
# JSON-RPC helper
# =========================
def rpc_call(method, params=None):
    payload = {
        "jsonrpc": "1.0",
        "id": "corecraft",
        "method": method,
        "params": params or []
    }

    r = requests.post(
        RPC_URL,
        auth=(RPC_USER, RPC_PASS),
        json=payload,
        timeout=15
    )
    r.raise_for_status()
    data = r.json()

    if data.get("error"):
        raise RuntimeError(data["error"])

    return data["result"]

# =========================
# Atualiza estatísticas do bloco via RPC
# =========================
def update_block_stats(block_hash: str):
# 1) Pega altura e timestamp (getblockheader é barato)
    header = rpc_call("getblockheader", [block_hash])
    height = header.get("height")
    blk_time = header.get("time")

# 2) Pega estatísticas agregadas (rápido e "real life" p/ dashboards)
# getblockstats existe há bastante tempo e é excelente para esse tipo de painel
    stats = rpc_call("getblockstats", [block_hash])

# Campos comuns:
# - txs: quantidade de tx
# - total_out: valor total de outputs (satoshis)
# - totalfee: taxa total (satoshis) [quando disponível no stats]
# - avgfeerate: taxa média (sat/vB) [quando disponível]
    txs = stats.get("txs")
    total_out = stats.get("total_out")
    total_fee = stats.get("totalfee")
    avgfeerate = stats.get("avgfeerate")

    STATE.update({
    "last_seen_at": datetime.now(timezone.utc).isoformat(),
    "best_height": height,
    "block_hash": block_hash,
    "block_time": (
        datetime.fromtimestamp(blk_time, tz=timezone.utc).isoformat()
        if blk_time else None
    ),
    "tx_count": txs,
    "total_out_sats": total_out,
    "total_fee_sats": total_fee,
    "avg_fee_rate_sat_vb": avgfeerate,
    })


# =========================
# Thread: subscriber ZMQ
# =========================
def zmq_subscriber_loop():
    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.SUB)

    print("[ZMQ] conectando em:", ZMQ_URL)
    sock.connect(ZMQ_URL)

    sock.setsockopt_string(zmq.SUBSCRIBE, "hashblock")
    print("[ZMQ] subscribe: hashblock")

    while True:
        try:
            topic, body, seq = sock.recv_multipart()
            topic = topic.decode("utf-8", errors="replace")
            print("[ZMQ] recebido:", topic, "len(body)=", len(body))

            if topic == "hashblock":
                block_hash = decode_hashblock(body)
                print("[ZMQ] novo bloco:", block_hash)
                update_block_stats(block_hash)

        except Exception as e:
            print("[ZMQ] erro:", repr(e))
            time.sleep(1)



# =========================
# HTTP (Flask): dashboard simples
# =========================
app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <meta http-equiv="refresh" content="5">
  <title>Core Craft — Bloco (ZMQ → RPC)</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 32px; }
    .card { border: 1px solid #ddd; border-radius: 12px; padding: 16px; max-width: 720px; }
    .k { color: #666; font-size: 14px; margin-top: 10px; }
    .v { font-size: 18px; font-weight: 600; }
    code { background: #f4f4f4; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>Core Craft — Evento de Bloco via ZMQ</h1>
  <p>Este painel é atualizado quando chega um <code>hashblock</code> pelo ZMQ e o sistema consulta o bloco via RPC.</p>

  <div class="card">
    <div class="k">Último evento visto</div>
    <div class="v">{{ s.last_seen_at or "—" }}</div>

    <div class="k">Altura</div>
    <div class="v">{{ s.best_height if s.best_height is not none else "—" }}</div>

    <div class="k">Hash</div>
    <div class="v"><code>{{ s.block_hash or "—" }}</code></div>

    <div class="k">Hora do bloco (UTC)</div>
    <div class="v">{{ s.block_time or "—" }}</div>

    <div class="k">Transações</div>
    <div class="v">{{ s.tx_count if s.tx_count is not none else "—" }}</div>

    <div class="k">Total de outputs (sats)</div>
    <div class="v">{{ s.total_out_sats if s.total_out_sats is not none else "—" }}</div>

    <div class="k">Fee total (sats)</div>
    <div class="v">{{ s.total_fee_sats if s.total_fee_sats is not none else "—" }}</div>

    <div class="k">Fee rate médio (sat/vB)</div>
    <div class="v">{{ s.avg_fee_rate_sat_vb if s.avg_fee_rate_sat_vb is not none else "—" }}</div>
  </div>

  <p style="margin-top:16px;">
    API JSON: <a href="/api/last-block">/api/last-block</a>
  </p>
</body>
</html>
"""

@app.get("/")
def index():
    return render_template_string(HTML, s=STATE)

@app.get("/api/last-block")
def api_last_block():
    return jsonify(STATE)

def main():
    t = threading.Thread(target=zmq_subscriber_loop, daemon=True)
    t.start()
    app.run(host="127.0.0.1", port=8080, debug=False)

if __name__ =="__main__":
    main()
