async function apiGet(path) {
  const r = await fetch(path);
  const data = await r.json();
  if (!data.ok) {
    throw new Error(data?.error?.message + (data?.error?.details ? " | " + data.error.details : ""));
  }
  return data.data;
}

function fmtTime(unix) {
  if (!unix) return "-";
  const d = new Date(unix * 1000);
  return d.toLocaleString();
}

function satToBTC(sats) {
  if (sats === null || sats === undefined) return "-";
  return (sats / 1e8).toFixed(8);
}

function setKV(el, obj) {
  el.innerHTML = "";
  for (const [k, v] of Object.entries(obj)) {
    const box = document.createElement("div");
    box.innerHTML = `<div class="k">${k}</div><div class="v">${v}</div>`;
    el.appendChild(box);
  }
}

function showError(el, msg) {
  el.textContent = msg;
  el.classList.remove("hidden");
}

function hideError(el) {
  el.textContent = "";
  el.classList.add("hidden");
}

// ----------- handlers -----------

async function refreshNode() {
  const nodeEl = document.getElementById("nodeState");
  const mpEl = document.getElementById("mempoolState");
  const errEl = document.getElementById("nodeError");

  hideError(errEl);

  try {
    const data = await apiGet("/api/node");

    setKV(nodeEl, {
      chain: data.chain,
      blocks: data.blocks,
      headers: data.headers,
      difficulty: data.difficulty,
      bestblockhash: data.bestblockhash
    });

    setKV(mpEl, {
      txcount: data.mempool.txcount,
      usage_bytes: data.mempool.usage,
      bytes: data.mempool.bytes,
      maxmempool: data.mempool.maxmempool,
      mempoolminfee: data.mempool.mempoolminfee
    });

  } catch (e) {
    showError(errEl, e.message);
  }
}

async function loadRecent() {
  const n = document.getElementById("recentN").value;
  const tbody = document.querySelector("#recentTable tbody");
  const infoEl = document.getElementById("recentInfo");
  const errEl = document.getElementById("recentError");

  hideError(errEl);
  tbody.innerHTML = "";
  infoEl.textContent = "Carregando...";

  try {
    const data = await apiGet(`/api/blocks/recent?n=${encodeURIComponent(n)}`);
    infoEl.textContent = `Tip: ${data.tip} — mostrando ${data.items.length} blocos`;

    for (const b of data.items) {
      const tr = document.createElement("tr");

      const hashShort = b.hash.slice(0, 16) + "…" + b.hash.slice(-8);

      tr.innerHTML = `
        <td>${b.height}</td>
        <td>${b.txs ?? "-"}</td>
        <td>${b.avgfeerate ?? "-"}</td>
        <td>${b.totalfee !== undefined ? satToBTC(b.totalfee) + " BTC" : "-"}</td>
        <td>${fmtTime(b.time)}</td>
        <td><a class="hash" href="#" data-hash="${b.hash}">${hashShort}</a></td>
      `;

      tbody.appendChild(tr);
    }

    // Clique no hash abre consulta de bloco
    document.querySelectorAll("a.hash").forEach(a => {
      a.addEventListener("click", async (ev) => {
        ev.preventDefault();
        const h = ev.target.getAttribute("data-hash");
        document.getElementById("blockHashInput").value = h;
        await consultBlock();
      });
    });

  } catch (e) {
    infoEl.textContent = "";
    showError(errEl, e.message);
  }
}

async function consultBlock() {
  const input = document.getElementById("blockHashInput");
  const out = document.getElementById("blockResult");
  const errEl = document.getElementById("blockError");

  hideError(errEl);
  out.textContent = "";

  const h = input.value.trim();
  if (!h) return showError(errEl, "Informe um blockhash.");

  try {
    const data = await apiGet(`/api/block/${encodeURIComponent(h)}`);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    showError(errEl, e.message);
  }
}

async function consultTx() {
  const input = document.getElementById("txidInput");
  const out = document.getElementById("txResult");
  const errEl = document.getElementById("txError");

  hideError(errEl);
  out.textContent = "";

  const txid = input.value.trim();
  if (!txid) return showError(errEl, "Informe um txid.");

  try {
    const data = await apiGet(`/api/tx/${encodeURIComponent(txid)}`);
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    showError(errEl, e.message);
  }
}

document.getElementById("btnRefresh").addEventListener("click", refreshNode);
document.getElementById("btnRecent").addEventListener("click", loadRecent);
document.getElementById("btnBlock").addEventListener("click", consultBlock);
document.getElementById("btnTx").addEventListener("click", consultTx);

// Carrega algo ao abrir
refreshNode();
loadRecent();

