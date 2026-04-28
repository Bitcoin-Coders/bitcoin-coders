import os
import json
import base64
from pathlib import Path
import requests

class BitcoinRPCError(Exception):
    pass

class BitcoinRPC:
    """
    Cliente JSON-RPC minimalista.
    - Usa RPC_USER/RPC_PASS se existir
    - Senão tenta cookie auth (ideal local)
    """

    def __init__(self):
        self.host = os.getenv("RPC_HOST", "127.0.0.1")
        self.port = int(os.getenv("RPC_PORT", "18113"))
        self.wallet = os.getenv("RPC_WALLET", "").strip()  # opcional, ex: "minha_wallet"
        self.network = os.getenv("BTC_NETWORK", "main").strip()  # main, testnet, regtest, signet

        self.user = os.getenv("RPC_USER")
        self.password = os.getenv("RPC_PASS")

        if not (self.user and self.password):
            self.user, self.password = self._read_cookie()

        self._session = requests.Session()
        self._url = self._build_url()

    def _build_url(self) -> str:
        # Wallet endpoint é /wallet/<name> (opcional)
        if self.wallet:
            return f"http://{self.host}:{self.port}/wallet/{self.wallet}"
        return f"http://{self.host}:{self.port}/"

    def _read_cookie(self):
        # Descobre caminho padrão do cookie por rede
        # main: ~/.bitcoin/.cookie
        # testnet: ~/.bitcoin/testnet3/.cookie
        # regtest: ~/.bitcoin/regtest/.cookie
        # signet: ~/.bitcoin/signet/.cookie
        base = Path(os.getenv("BTC_DATADIR", str(Path.home() / ".bitcoin")))
        net = self.network.lower()

        if net == "main":
            cookie_path = base / ".cookie"
        elif net == "testnet":
            cookie_path = base / "testnet3" / ".cookie"
        elif net == "regtest":
            cookie_path = base / "regtest" / ".cookie"
        elif net == "signet":
            cookie_path = base / "signet" / ".cookie"
        else:
            cookie_path = base / ".cookie"

        if not cookie_path.exists():
            raise BitcoinRPCError(
                f"Não achei cookie RPC em {cookie_path}. "
                "Defina RPC_USER/RPC_PASS ou ajuste BTC_NETWORK/BTC_DATADIR."
            )

        content = cookie_path.read_text().strip()
        # formato: user:password
        if ":" not in content:
            raise BitcoinRPCError(f"Cookie inválido em {cookie_path}")
        u, p = content.split(":", 1)
        return u, p

    def call(self, method: str, params=None):
        if params is None:
            params = []

        payload = {
            "jsonrpc": "1.0",
            "id": "corecraft-aula1",
            "method": method,
            "params": params
        }

        auth_str = f"{self.user}:{self.password}".encode("utf-8")
        auth_header = base64.b64encode(auth_str).decode("utf-8")

        try:
            r = self._session.post(
                self._url,
                data=json.dumps(payload),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {auth_header}",
                },
                timeout=10,
            )
        except requests.RequestException as e:
            raise BitcoinRPCError(f"Falha de rede ao chamar RPC: {e}")

        if r.status_code != 200:
            raise BitcoinRPCError(f"RPC HTTP {r.status_code}: {r.text[:200]}")

        data = r.json()
        if data.get("error"):
            raise BitcoinRPCError(data["error"])

        return data["result"]

