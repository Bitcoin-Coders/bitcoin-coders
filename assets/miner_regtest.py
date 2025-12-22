#!/usr/bin/env python3
import binascii
import hashlib

COINBASE_TX_HEX = (
    "01000000"
    "01"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "ffffffff"
    "03"
    "02e406" #02+altura do bloco em LE
    "ffffffff"
    "02"
    "BE40250000000000" #coinbasevalue em LE
    "16"
    "00140fee9cc0499b2e61ed64c3fdfbee4c88ffd12874" #scriptPubKey end receb da coinbase
    "0000000000000000"
    "26"
    "6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9"
    "00000000"
)

# Header
VERSION_LE      = "00000020"
PREV_BLOCK_LE = "E9682DF87231E48D6EE06429B1D750F1CB320F55E19290F4FF950BA1F0270000"
MERKLE_ROOT_LE = "9F3D9E477CFA03273545035AB5B576782EC3C17FE8E1263DCCB0688B2DC6CCBC"
TIME_LE = "FC438668"
BITS_LE         = "ffff7f20"

# Target da rede (do getblocktemplate)
TARGET_HEX = "7fffff0000000000000000000000000000000000000000000000000000000000"
TARGET_INT = int(TARGET_HEX, 16)

# Opcional: deixar mais difícil só para fins didáticos
EXTRA_DIFFICULTY_BITS = 16  # 2^16 ≈ 65 mil vezes mais difícil
CUSTOM_TARGET_INT = TARGET_INT >> EXTRA_DIFFICULTY_BITS

HEADER_BASE_NO_NONCE = VERSION_LE + PREV_BLOCK_LE + MERKLE_ROOT_LE + TIME_LE + BITS_LE


def sha256d(hex_str: str) -> bytes:
    data = binascii.unhexlify(hex_str)
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def main():
    print("Header base (sem nonce):")
    print(HEADER_BASE_NO_NONCE)
    print("\nTarget da rede:")
    print(TARGET_HEX)
    print("Target customizado:", hex(CUSTOM_TARGET_INT)[2:].rjust(64, "0"))
    print()

    for nonce in range(0, 2**32):
        nonce_le = format(nonce, "08x")
        header_hex = HEADER_BASE_NO_NONCE + nonce_le

        h = sha256d(header_hex)
        hash_be_hex = h[::-1].hex()
        print("Tentando: ")
        print("Nonce (decimal):", nonce)
        print("Hash do bloco (big-endian):", hash_be_hex)
        if int(hash_be_hex, 16) < CUSTOM_TARGET_INT:
            print("✅ Nonce encontrado!")
            print("Nonce (decimal):", nonce)
            print("Nonce (hex LE):", nonce_le)
            print("Hash do bloco (big-endian):", hash_be_hex)

            block_hex = header_hex + "01" + COINBASE_TX_HEX
            print("\nBloco completo (hex) para submitblock:")
            print(block_hex)
            return

    print("⚠ Nenhum nonce encontrado no intervalo 0..2^32-1.")


if __name__ == "__main__":
    main()
