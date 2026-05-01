# rpc.py

import requests
import json

class BitcoinRPC:
    def __init__(self, url, user, password):
        self.url = url
        self.auth = (user, password)

    def call(self, method, params=[]):
        payload = {
            "jsonrpc": "1.0",
            "id": "corecraft",
            "method": method,
            "params": params
        }

        response = requests.post(
            self.url,
            auth=self.auth,
            data=json.dumps(payload)
        )

        result = response.json()
        if result.get("error"):
            raise Exception(result["error"])

        return result["result"]
