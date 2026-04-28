import os, threading, time
import requests, zmq
from flask import Flask, request, jsonify, render_template_string

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:58443")
RPC_USER = os.getenv("RPC_USER", "teste")
RPC_PASS = os.getenv("RPC_PASS", "teste")
ZMQ_URL = os.getenv("ZMQ_URL", "tcp://127.0.0.1:58335")

app = Flask(__name__)

STATE = {
    "txid": None,
    "status": "Informe endereço e valor para enviar.",
    "block_hash": None,
    "block_height": None,
    "chain": None,
    "balance": None
}

def rpc(method, params=[]):
    payload = {
        "jsonrpc": "1.0",
        "id": "demo",
        "method": method,
        "params": params
    }

    r = requests.post(RPC_URL, auth=(RPC_USER, RPC_PASS), json=payload)
    data = r.json()

    if data.get("error"):
        raise Exception(data["error"])

    return data["result"]

def decode_hashblock(body: bytes) -> str:
    h1 = body[::-1].hex()
    h2 = body.hex()

    try:
        rpc("getblockheader", [h1])
        return h1
    except:
        pass

    try:
        rpc("getblockheader", [h2])
        return h2
    except:
        pass

    return h1

@app.route("/")
def index():
    return render_template_string("""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Core Craft - Send to Address</title>
  <style>
    body { font-family: system-ui; margin: 40px; max-width: 800px; }
    input { width: 100%; padding: 10px; margin-top: 8px; box-sizing: border-box; }
    button { padding: 10px 18px; margin-top: 14px; cursor: pointer; }
    .card { border: 1px solid #ddd; padding: 16px; border-radius: 12px; margin-top: 20px; }
    code { word-break: break-all; }
    label { font-weight: 600; display: block; margin-top: 12px; }
  </style>
</head>
<body>
  <h1>Enviar BTC pela wallet do node</h1>

  <label>Endereço de destino</label>
  <input id="address" placeholder="Ex: tb1q...">

  <label>Valor em BTC</label>
  <input id="amount" type="number" step="0.00000001" placeholder="Ex: 0.0001">

  <button onclick="sendTx()">Enviar transação</button>

  <div class="card">
    <h3>Status</h3>
    <p id="status">Carregando...</p>
    <p><b>Chain:</b> <span id="chain">-</span></p>
    <p><b>Saldo:</b> <span id="balance">-</span> BTC</p>
    <p><b>TXID:</b> <code id="txid">-</code></p>
    <p><b>Bloco:</b> <code id="block">-</code></p>
    <p><b>Altura:</b> <span id="height">-</span></p>
  </div>

<script>
async function sendTx() {
  const address = document.getElementById("address").value.trim();
  const amount = parseFloat(document.getElementById("amount").value);

  const res = await fetch("/send", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({address, amount})
  });

  const data = await res.json();
  alert(data.message || data.error);
  updateStatus();
}

async function updateStatus() {
  const res = await fetch("/status");
  const data = await res.json();

  document.getElementById("chain").innerText = data.chain || "-";
  document.getElementById("balance").innerText = data.balance ?? "-";
  document.getElementById("status").innerText = data.status;
  document.getElementById("txid").innerText = data.txid || "-";
  document.getElementById("block").innerText = data.block_hash || "-";
  document.getElementById("height").innerText = data.block_height ?? "-";
}

setInterval(updateStatus, 3000);
updateStatus();
</script>
</body>
</html>
""")

@app.route("/send", methods=["POST"])
def send():
    data = request.json
    address = data.get("address", "").strip()
    amount = float(data.get("amount", 0))

    if not address:
        return jsonify({"error": "Endereço não informado."}), 400

    if amount <= 0:
        return jsonify({"error": "Valor inválido."}), 400

    try:
        balance = rpc("getbalance")

        if balance < amount:
            return jsonify({
                "error": f"Saldo insuficiente. Saldo atual: {balance} BTC"
            }), 400

        txid = rpc("sendtoaddress", [address, amount])

        STATE["txid"] = txid
        STATE["status"] = "Transação enviada e aceita na mempool. Aguardando confirmação em bloco..."
        STATE["block_hash"] = None
        STATE["block_height"] = None

        return jsonify({
            "message": "Transação enviada com sucesso.",
            "txid": txid
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/status")
def status():
    try:
        info = rpc("getblockchaininfo")
        STATE["chain"] = info.get("chain")
        STATE["balance"] = rpc("getbalance")
    except:
        pass

    return jsonify(STATE)

def zmq_loop():
    ctx = zmq.Context()
    sock = ctx.socket(zmq.SUB)
    sock.connect(ZMQ_URL)
    sock.setsockopt_string(zmq.SUBSCRIBE, "hashblock")

    print("[ZMQ] aguardando blocos em", ZMQ_URL)

    while True:
        try:
            topic, body, seq = sock.recv_multipart()

            block_hash = decode_hashblock(body)
            print("[ZMQ] novo bloco:", block_hash)

            if not STATE["txid"]:
                continue

            block = rpc("getblock", [block_hash, 2])

            for tx in block["tx"]:
                if tx["txid"] == STATE["txid"]:
                    STATE["status"] = "Transação confirmada em bloco!"
                    STATE["block_hash"] = block_hash
                    STATE["block_height"] = block["height"]
                    print("[OK] tx confirmada:", STATE["txid"])
                    break

        except Exception as e:
            print("[ZMQ erro]", e)
            time.sleep(1)

if __name__ == "__main__":
    threading.Thread(target=zmq_loop, daemon=True).start()
    app.run(host="127.0.0.1", port=8081)
