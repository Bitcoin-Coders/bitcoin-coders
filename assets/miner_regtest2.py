#!/usr/bin/env python3
import hashlib

# =========================
# 1) DADOS DO TEMPLATE
# =========================
PREV_BLOCK_HASH_BE = "6b782674a0aac0ad2af8e283ac1e31dd6b3abf0dffe76a2aba58aed91865c5e5"
CURTIME = 1769378872
BITS_BE = "207fffff"  # ex: "207fffff" (big-endian string)

# target do template (regtest fácil)
TARGET_HEX_BE = "7fffff0000000000000000000000000000000000000000000000000000000000"
TARGET_INT = int(TARGET_HEX_BE, 16)

EXTRA_DIFFICULTY_BITS = 24
CUSTOM_TARGET_INT = TARGET_INT >> EXTRA_DIFFICULTY_BITS

# =========================
# 2) COINBASE (RAW TX HEX)
# =========================
# Isso é a TRANSAÇÃO coinbase (hex completo), não o txid.
# Observação: vários campos neste raw tx (como prevout hash = 0, index = 0xffffffff,
# sequence = 0xffffffff, valores zerados e tamanhos de script fixos) são padrões
# obrigatórios da transação coinbase e não carregam dados “reais” de gasto;
# eles apenas existem para satisfazer o formato da transação Bitcoin.

COINBASE_TX_HEX = (
    "01000000"
    "01"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "ffffffff"
    "03"
    "027F02"  # 02 + Altura (convertida pra Hex + convertida em LE)
    "ffffffff"
    "02"
    "905EBC1300000000"  # coinbasevalue (convertido pra Hex + convertido em LE)
    "16"
    "0014eb340a1673b18844691e596da52f9d2eaabf4d2b" #P2WPKH para endereço do miner
    "0000000000000000"
    "26"    "6a24aa21a9ed98486dd866cdbee618cd3f64dbb8489faa5b9cd7ecd8be2f74f4ac00a733d1a7" #witness_commitment
    "00000000"
)

# witness_commitment: hash que “resume” todos os dados de witness do bloco.
# Depois que o bloco é minerado, qualquer nó pode recalcular esse hash e comparar com o valor na coinbase.
# Se bater:
#   Prova que nenhuma assinatura (witness) foi alterada depois que o bloco foi montado.

# =========================
# 3) TRANSAÇÕES DO BLOCO (RAW TX HEX)
# =========================
# Cole exatamente o transactions[].data do getblocktemplate,
# na ordem em que você quer no bloco (igual ao template).
TX_DATA_HEX_LIST = [
# TX C (data do template)
   "02000000000101071935d912a8467b45e0ad92063b79cdb483eaed46e8cbfccd74cc35d89c6b430000000000fdffffff0480f0fa020000000016001434a98d2cff0499c43ab8c5fd45f55278968056ef80f0fa02000000001600143ac9e5b9bcc8a82fb4edeccb2a62b661e0517f2180f0fa02000000001600144f5edd39f38b92670bce1e9912f2129468bcf12010180f3200000000160014161e43fcaa8f1b525b6f58ae23220e078992947d0247304402207884e17c09cef7cdd42e2e3e8795d58fdb81e28632d6b88ab21c110d4656be0302207e4a410fa23e9b13c12320042427b3aa1b8ffb53a9c234d200af4222ccfc62f5012102d514c24ef0bfdcb7b744c7e3d7010256c517f622c8451be8c7515ccf380955bf00000000",

# TX A
    "0200000000010136eb42cba177e0363390c817265339508870dce9e8e99483ca73af554b296fa20000000000fdffffff0200e1f50500000000160014ff3a8d849398a28014b98a06321d6278cd6768ee0acc480900000000160014a43d8d850701af90129d158635b3bf82df9ebd5a024730440220716fe08b686eec6dba4456797a1f5a8caf947e7b39866920a9df1f117d18f8ad0220372f22ef46b6f1b68fcc37bf746f0a44235b2ff04d12a9e0a74f0cc062610c8c01210367fa46ea3be3f88ec4fd2676fb3dd656ec9bf85471274870b3eee796327f16bd7e020000",
    
# TX B 
    "0200000000010178553be9151a6619c318328b852bf037dd63fb412071553eb1ae5f094c566e3b0100000000fdffffff022c706a03000000001600140da0925f716068904656d59591ba65db5b7b345d804a5d050000000016001424b373f5b61e1f74ae831518b61acbc60d7c83ed0247304402207f4e28e8aac66a53ac0c5004d01d7f5a57c64bcc16257097a47d61dee8b4d28a02201ab1ba622c1395154bf99d7357c0dcde3f2e42fab85df205cfc1aab6241428cf012102dce3b505c0e21c270be1a7f6a8589835bed4f469d5538ef921d1f593f5ef44fa00000000",

# TX D

"02000000000102f80e546515a0ee165e325c827ba0a0f45b7751125c3bffdec57633450fc0ebc80200000000fdfffffffc786fcd796ce42f8c3cfd12d5ad5b9ed9d64f82df0854ce9a0732bf04e555c60000000000fdffffff0280f0fa020000000016001415c116605e09e8973d6fe9698886dad0fd1037cb7082760000000000160014b9c6060a2dbaaced41f0a5908fdee1425b07eafc0247304402204dc252e1329316b0e699da9318baea736eadac406fe9c7da208e4b997b2c392002203bb633daecadb2fd2fddcd2d8e38928e4122938ba738525470d10af9344918570121021c9b554ff399f13be50a5451d50afbf7c9b88979bf74b41b94cf1ae399f0813d024730440220439dcb80bfbd0b5799e49517ba44ae1cedbec560af504021cb399f261e99a09d022004bd906510cff007f9b5cdda63997c47a27e5dfef253cfd82d4199cbe344589f012102660f483289c5c86baed3a6629c91127bc60a81d04a62fe41075dfdca6d0f696a7e020000"

]

# TXIDS NONCOINBASE
TXIDS_NONCOINBASE_BE = [    
   "37086e834875eeb6cc63bf0c5fb8924270be70389ee64e9127a4ab25a9e9e1a2",
  "3b6e564c095faeb13e55712041fb63dd37f02b858b3218c319661a15e93b5578",
  "33cf1862321e17b62c49f99e8d9bbca8f6a48bcbbea3487dbbd3803bfd93666a",
"45ca82769ec92b2c029c95389939d26f976e6670cb2e007227efba1f59b559a4",
]

# =========================
# Funções auxiliares
# =========================
# Double SHA-256: hash padrão usado em txids e Merkle tree no Bitcoin
def sha256d(b: bytes) -> bytes:
    return hashlib.sha256(hashlib.sha256(b).digest()).digest()

# Converte um inteiro em 4 bytes little-endian (uint32)
def u32_le(n: int) -> bytes:
    return n.to_bytes(4, "little", signed=False)

# Converte uma string hex big-endian em bytes little-endian
def hex_be_to_le_bytes(hex_be: str) -> bytes:
    return bytes.fromhex(hex_be)[::-1]

# Converte o campo bits (target compactado) de BE para LE em bytes
def bits_be_to_le_bytes(bits_be: str) -> bytes:
    return bytes.fromhex(bits_be)[::-1]

# Codifica um inteiro no formato varint do Bitcoin
def varint(n: int) -> bytes:
    if n < 0xfd:
        return bytes([n])
    if n <= 0xffff:
        return b"\xfd" + n.to_bytes(2, "little")
    if n <= 0xffffffff:
        return b"\xfe" + n.to_bytes(4, "little")
    return b"\xff" + n.to_bytes(8, "little")

# Calcula o txid a partir do raw tx (double SHA-256 e reverse para BE)
def txid_from_rawtx_hex(rawtx_hex: str) -> str:
    tx = bytes.fromhex(rawtx_hex)
    h = sha256d(tx)          # bytes LE
    return h[::-1].hex()     # BE string

# Calcula a Merkle root a partir de uma lista de txids (em BE)
def merkle_root_from_txids_be(txids_be: list[str]) -> bytes:
    layer = [hex_be_to_le_bytes(t) for t in txids_be]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        layer = [sha256d(layer[i] + layer[i+1]) for i in range(0, len(layer), 2)]
    return layer[0]  # LE

# Monta os campos fixos do header do bloco (sem nonce)
def build_header_base(prev_block_be: str, merkle_root_le: bytes, curtime: int, bits_be: str) -> bytes:
    version_le = u32_le(0x20000000)
    prev_block_le = hex_be_to_le_bytes(prev_block_be)
    time_le = u32_le(curtime)
    bits_le = bits_be_to_le_bytes(bits_be)
    return version_le + prev_block_le + merkle_root_le + time_le + bits_le

# =========================
# main
# =========================
def main():
    # 1) Calcula txid real da coinbase (a partir do raw tx)
    coinbase_txid_be = txid_from_rawtx_hex(COINBASE_TX_HEX)

    # 2) Lista final de txids (coinbase + txs do template)
    txids_in_block_be = [coinbase_txid_be] + TXIDS_NONCOINBASE_BE

    # 3) Merkle root (LE no header)
    merkle_root_le = merkle_root_from_txids_be(txids_in_block_be)
    merkle_root_be = merkle_root_le[::-1].hex()

    header_base = build_header_base(PREV_BLOCK_HASH_BE, merkle_root_le, CURTIME, BITS_BE)

    print("=== Fase 1: bloco candidato ===")
    print("coinbase txid:", coinbase_txid_be)
    print("txcount:", len(txids_in_block_be))
    print("merkle_root (BE):", merkle_root_be)
    print("target (custom):", hex(CUSTOM_TARGET_INT)[2:].rjust(64, "0"))
    print()

    # 4) Minera: tenta nonces
    for nonce in range(0, 2**32):
        header = header_base + u32_le(nonce)
        h = sha256d(header)
        hash_be = h[::-1].hex()

        if nonce % 200000 == 0 and nonce > 0:
            print(f"tentativas: {nonce:,} | hash: {hash_be[:16]}...")

        if int(hash_be, 16) < CUSTOM_TARGET_INT:
            print("\n✅ Nonce encontrado!")
            print("nonce:", nonce)
            print("hash (BE):", hash_be)
            print("header (hex):", header.hex())

            # 5) Monta bloco completo: header + varint(txcount) + txs (raw)
            block = bytearray()
            block += header
            block += varint(1 + len(TX_DATA_HEX_LIST))  # coinbase + outras txs
            block += bytes.fromhex(COINBASE_TX_HEX)
            for txhex in TX_DATA_HEX_LIST:
                block += bytes.fromhex(txhex)

            block_hex = block.hex()
            print("\n=== Bloco completo (hex) ===")
            print(block_hex)

            print("\nPara submeter:")
            print(f'bitcoin-cli -datadir="." submitblock "{block_hex}"')
            return

    print("⚠ Nenhum nonce encontrado.")

if __name__ == "__main__":
    main()

