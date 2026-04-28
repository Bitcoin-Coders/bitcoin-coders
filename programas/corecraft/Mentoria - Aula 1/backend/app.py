import os
from flask import Flask, jsonify, request, send_from_directory
from rpc import BitcoinRPC, BitcoinRPCError

app = Flask(__name__)
rpc = BitcoinRPC()

# ---------- utilitários ----------

def ok(data):
    return jsonify({"ok": True, "data": data})

def fail(message, details=None, code=400):
    payload = {"ok": False, "error": {"message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return jsonify(payload), code


# ---------- endpoints API ----------

@app.get("/api/node")
def api_node():
    """
    Node snapshot:
    - getblockchaininfo (chain, blocks, headers, difficulty, bestblockhash)
    - getmempoolinfo (size, bytes, usage)
    - getnetworkinfo (subversion, connections)
    """
    try:
        bc = rpc.call("getblockchaininfo")
        mp = rpc.call("getmempoolinfo")
        nw = rpc.call("getnetworkinfo")

        data = {
            "chain": bc.get("chain"),
            "blocks": bc.get("blocks"),
            "headers": bc.get("headers"),
            "difficulty": bc.get("difficulty"),
            "bestblockhash": bc.get("bestblockhash"),
            "mempool": {
                "txcount": mp.get("size"),
                "bytes": mp.get("bytes"),
                "usage": mp.get("usage"),
                "maxmempool": mp.get("maxmempool"),
                "mempoolminfee": mp.get("mempoolminfee"),
            },
            "network": {
                "subversion": nw.get("subversion"),
                "connections": nw.get("connections"),
                "version": nw.get("version"),
            }
        }
        return ok(data)
    except BitcoinRPCError as e:
        return fail("Falha ao consultar estado do node via RPC.", details=str(e), code=502)


@app.get("/api/blocks/recent")
def api_blocks_recent():
    """
    Lista N blocos recentes com estatísticas simples.
    Usa:
      - getblockcount
      - getblockhash(height)
      - getblockheader(hash)  (leve)
      - getblockstats(hash)   (stats úteis)
    """
    n = int(request.args.get("n", 10))
    n = max(1, min(n, 25))  # limite didático

    try:
        tip = rpc.call("getblockcount")
        blocks = []
        for h in range(tip, max(tip - n, -1), -1):
            bh = rpc.call("getblockhash", [h])
            header = rpc.call("getblockheader", [bh])
            stats = rpc.call("getblockstats", [bh])

            blocks.append({
                "height": h,
                "hash": bh,
                "time": header.get("time"),
                "mediantime": header.get("mediantime"),
                "txs": stats.get("txs"),
                "totalfee": stats.get("totalfee"),
                "avgfee": stats.get("avgfee"),
                "feerate_percentiles": stats.get("feerate_percentiles"),
                "avgfeerate": stats.get("avgfeerate"),
                "avg_tx_size": stats.get("avgtxsize"),
                "total_size": stats.get("total_size"),
            })

        return ok({"tip": tip, "items": blocks})
    except BitcoinRPCError as e:
        return fail("Falha ao consultar blocos recentes via RPC.", details=str(e), code=502)


@app.get("/api/block/<blockhash>")
def api_block(blockhash):
    """
    Resumo de um bloco por hash.
    Usa getblock(hash, verbosity=1) para evitar payload gigante.
    """
    try:
        blk = rpc.call("getblock", [blockhash, 1])

        data = {
            "hash": blk.get("hash"),
            "height": blk.get("height"),
            "confirmations": blk.get("confirmations"),
            "time": blk.get("time"),
            "nTx": blk.get("nTx"),
            "size": blk.get("size"),
            "weight": blk.get("weight"),
            "version": blk.get("version"),
            "previousblockhash": blk.get("previousblockhash"),
            "nextblockhash": blk.get("nextblockhash"),
            "tx": blk.get("tx")[:20],  # mostra só 20 txids por segurança/UX
        }
        return ok(data)
    except BitcoinRPCError as e:
        return fail("Falha ao consultar bloco.", details=str(e), code=502)


@app.get("/api/tx/<txid>")
def api_tx(txid):
    """
    Consulta uma transação por txid.

    Importante (conceito de integração real):
    - getrawtransaction (verbose=1) só funciona se:
      a) tx estiver na mempool OU
      b) tx estiver na wallet OU
      c) node foi iniciado com txindex=1 (indexação completa)
    """
    try:
        tx = rpc.call("getrawtransaction", [txid, True])
        data = {
            "txid": tx.get("txid"),
            "hash": tx.get("hash"),
            "version": tx.get("version"),
            "size": tx.get("size"),
            "vsize": tx.get("vsize"),
            "weight": tx.get("weight"),
            "locktime": tx.get("locktime"),
            "vin": tx.get("vin"),
            "vout": tx.get("vout"),
            "confirmations": tx.get("confirmations"),  # pode não existir
            "blockhash": tx.get("blockhash"),
            "time": tx.get("time"),
            "blocktime": tx.get("blocktime"),
        }
        return ok(data)
    except BitcoinRPCError as e:
        return fail(
            "Falha ao consultar tx. Dica: isso exige txindex=1, ou a tx precisa estar na mempool/wallet.",
            details=str(e),
            code=502
        )


# ---------- servir frontend (opcional) ----------
# Vamos servir o frontend por Flask para facilitar (um único comando pra rodar tudo).
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.get("/app.js")
def frontend_js():
    return send_from_directory(FRONTEND_DIR, "app.js")

@app.get("/styles.css")
def frontend_css():
    return send_from_directory(FRONTEND_DIR, "styles.css")


if __name__ == "__main__":
    # Dica: debug=True só em ambiente local
    app.run(host="127.0.0.1", port=8080, debug=True)

