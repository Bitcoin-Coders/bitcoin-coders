# Mineração na prática: minerando blocos na regtest com bitcoin-cli

No artigo anterior, vimos **como um bloco Bitcoin é estruturado**, o que é o header de 80 bytes, como funciona o campo `bits` e como a Prova de Trabalho exige que o hash do header seja menor que um alvo (`target`) definido pela rede.

Agora vamos dar o passo que faltava:

> pegar um node Bitcoin Core em regtest e realmente minerar um bloco “na mão”:
> 
> - vamos consultar o estado da blockchain,
> - construir a transação coinbase manualmente,
> - montar o header com os campos corretos,
> - rodar um minerador em Python que testa nonces até achar um hash válido,
> - e finalmente enviar o bloco pronto para o node com `submitblock`.

---

### Mineração em regtest: fechando o ciclo com o bitcoin-cli

Antes de mergulharmos no processo manual de mineração, vale lembrar que o Bitcoin Core já oferece um **atalho extremamente simples para minerar blocos na regtest**. Basta executar:

```bash
bitcoin-cli -datadir="." generatetoaddress 1 <endereço>
```

Esse comando:

- cria automaticamente a coinbase,
- monta o bloco seguindo as regras de consenso,
- encontra um nonce válido instantaneamente (já que a dificuldade é mínima),
- e adiciona o bloco à blockchain local.

Com isso, em ambientes de teste, você consegue:

- confirmar transações,
- avançar o tempo da chain,
- destravar UTXOs de coinbase após 100 blocos,
- simular cenários rapidamente.

**Porém…** esse método *esconde* praticamente todo o processo de mineração real.

Nós não vemos:

- como a coinbase é construída,
- como o Merkle root é calculado,
- como o header é montado,
- como o hash é comparado ao `target`,
- nem como um minerador realmente tenta bilhões de nonces.

A ideia nesse artigo é fazer o oposto. Vamos entender a fundo a mineração e reconstruir **manualmente** cada passo desse processo. Assim, vamos:

1. Verificar o **estado atual da blockchain**
2. Obter um **template de bloco** com `getblocktemplate`
3. Construir a **transação coinbase** manualmente
4. Montar o **header do bloco**
5. Rodar um script Python que faz o papel de **minerador**
6. Enviar o bloco com `submitblock` e ver a blockchain avançar

Nos nossos exemplos vamos assumir o ambiente do `datadir` configurado em `regtest`:

```bash
bitcoind -datadir="."  # regtest configurado nesse datadir
```

---

### Passo 1 — Verificando o estado atual da blockchain

Antes de minerar, precisamos saber **onde a cadeia está**:

```bash
bitcoin-cli -datadir="." getblockchaininfo
```

Saída (situação *antes* de minerar o novo bloco):

```bash
{
  "chain": "regtest",
  "blocks": 1546,
  "headers": 1546,
  "bestblockhash": "000002d42512f36787b9f4adb960502f0fa3e1f527d053f82234986ec59b830d",
  "bits": "207fffff",
  "target": "7fffff0000000000000000000000000000000000000000000000000000000000",
  "difficulty": 4.656542373906925e-10,
  "time": 1765375693,
  "mediantime": 1765374950,
  "verificationprogress": 1,
  "initialblockdownload": false,
  "chainwork": "0000000000000000000000000000000000000000000000000000000000000c16",
  "size_on_disk": 478357,
  "pruned": false,
  "warnings": [
  ]
}
```

Informações importantes aqui:

- `blocks`: altura atual (1546)
- `bestblockhash`: hash do último bloco
- `bits` e `target`: dificuldade da rede regtest (mínima, `0x207fffff`)
- `chainwork`: trabalho acumulado até aqui

É com base nesse estado que vamos construir o próximo bloco, de altura **1547**.

---

### Passo 2 — Obtendo o template do próximo bloco

Agora pedimos ao node um **esqueleto de bloco** com `getblocktemplate`. É isso que um minerador real faz:

```bash
bitcoin-cli -datadir="." getblocktemplate '{"rules": ["segwit"]}'
```

Saída:

```bash
{
  "capabilities": [
    "proposal"
  ],
  "version": 536870912,
  "rules": [
    "csv",
    "!segwit",
    "testdummy",
    "taproot"
  ],
  "vbavailable": {
  },
  "vbrequired": 0,
  "previousblockhash": "000002d42512f36787b9f4adb960502f0fa3e1f527d053f82234986ec59b830d",
  "transactions": [
  ],
  "coinbaseaux": {
  },
  "coinbasevalue": 4882812,
  "longpollid": "000002d42512f36787b9f4adb960502f0fa3e1f527d053f82234986ec59b830d102",
  "target": "7fffff0000000000000000000000000000000000000000000000000000000000",
  "mintime": 1765374951,
  "mutable": [
    "time",
    "transactions",
    "prevblock"
  ],
  "noncerange": "00000000ffffffff",
  "sigoplimit": 80000,
  "sizelimit": 4000000,
  "weightlimit": 4000000,
  "curtime": 1765822776,
  "bits": "207fffff",
  "height": 1547,
  "default_witness_commitment": "6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9"
}
```

Pontos-chave:

- `height = 1547` — altura do bloco que vamos minerar
- `previousblockhash` — hash do bloco 1546, que o novo bloco vai referenciar
- `coinbasevalue = 4882812` satoshis — recompensa + taxas disponíveis
- `bits` e `target` — dificuldade que o header precisa cumprir
- `curtime` — timestamp sugerido
- `default_witness_commitment` — script de `OP_RETURN` que precisamos colocar na coinbase para blocos com SegWit

Esse template **não é um bloco pronto**, mas sim a lista de ingredientes que o minerador usa para montar:

- a **coinbase**,
- o **Merkle root**,
- e finalmente o **header** que será hasheado até satisfazer o alvo de Prova de Trabalho.

---

### Passo 3 — Construindo a transação coinbase

A coinbase é a primeira transação do bloco, que:

- não consome UTXOs anteriores,
- cria os novos satoshis da recompensa,
- coleta as taxas (se houver),
- e carrega algumas informações importantes (altura do bloco, witness commitment, etc.).

Vamos pagar a recompensa para o endereço:

```
bcrt1q7e4uc7mz8rhl0e2g25a3jcguydxale9yrnl4cz
```

Podemos confirmar o scriptPubKey dele:

```bash
bitcoin-cli -datadir="." getaddressinfo "bcrt1q7e4uc7mz8rhl0e2g25a3jcguydxale9yrnl4cz"
```

Trecho relevante da saída:

```bash
{
  "scriptPubKey": "0014f66bcc7b6238eff7e548553b19611c234ddfe4a4",
  "iswitness": true,
  "witness_version": 0,
  "witness_program": "f66bcc7b6238eff7e548553b19611c234ddfe4a4",...
}
```

### ScriptSig com a altura (BIP34)

A altura do bloco é 1547.

- 1547 decimal = `0x060B`
- Em little-endian: `0b 06`

O scriptSig do input coinbase leva a altura codificada assim:

```
02 0b 06
```

onde:

- `0x02` = “vou empurrar 2 bytes”
- `0b 06` = altura 1547 em little-endian

### Montagem da coinbase em hex (bloco 1547)

A coinbase usada para esse bloco fica:

```
01000000                                                          # version
01                                                                # vin_count
0000000000000000000000000000000000000000000000000000000000000000  # prev_txid (coinbase)
ffffffff                                                          # vout (coinbase)
03                                                                # scriptSig length
020b06                                                            # scriptSig: altura 1547 (BIP34)
ffffffff                                                          # sequence
02                                                                # vout_count = 2
7c814a0000000000                                                  # value = 4 882 812 sat
16                                                                # pkScript length = 22 bytes
0014f66bcc7b6238eff7e548553b19611c234ddfe4a4                      # P2WPKH para o endereço bcrt1q7e4...
0000000000000000                                                  # value = 0 (output do commitment)
26                                                                # pkScript length = 38 bytes
6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9  # default_witness_commitment
00000000                                                          # locktime
```

Coinbase completa em uma linha (para usar em comandos):

```
01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff03020b06ffffffff027c814a0000000000160014f66bcc7b6238eff7e548553b19611c234ddfe4a40000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf900000000
```

Podemos pedir para o node decodificar essa transação e conferir:

```bash
bitcoin-cli -datadir="." decoderawtransaction "0100000001..."
```

Saída:

```bash
{
  "txid": "1ed002fc5dadd422db257ec5f6f7ead9045e1ac2d0bae1298ed4d2e2c40ed177",
  "hash": "1ed002fc5dadd422db257ec5f6f7ead9045e1ac2d0bae1298ed4d2e2c40ed177",
  "version": 1,
  "size": 132,
  "vsize": 132,
  "weight": 528,
  "locktime": 0,
  "vin": [
    {
      "coinbase": "020b06",
      "sequence": 4294967295
    }
  ],
  "vout": [
    {
      "value": 0.04882812,
      "n": 0,
      "scriptPubKey": {
        "asm": "0 f66bcc7b6238eff7e548553b19611c234ddfe4a4",
        "desc": "addr(bcrt1q7e4uc7mz8rhl0e2g25a3jcguydxale9yrnl4cz)#xps6m4ne",
        "hex": "0014f66bcc7b6238eff7e548553b19611c234ddfe4a4",
        "address": "bcrt1q7e4uc7mz8rhl0e2g25a3jcguydxale9yrnl4cz",
        "type": "witness_v0_keyhash"
      }
    },
    {
      "value": 0.00000000,
      "n": 1,
      "scriptPubKey": {
        "asm": "OP_RETURN aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9",
        "desc": "raw(6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9)#cav96mf3",
        "hex": "6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9",
        "type": "nulldata"
      }
    }
  ]
}
```

Ou seja:

- a coinbase está correta,
- paga a recompensa para o endereço desejado,
- carrega o `default_witness_commitment`.

O `txid` (big-endian) dessa coinbase é:

```
1ed002fc5dadd422db257ec5f6f7ead9045e1ac2d0bae1298ed4d2e2c40ed177
```

Como ela é a única transação do bloco, esse será o **Merkle root**.

---

### Passo 4 — Montando o header do bloco

Agora vamos montar o header de 80 bytes que o minerador vai hashear.

### Campos em little-endian

Do `getblocktemplate`:

- `version = 536870912 = 0x20000000`
    
    → little-endian: `00000020`
    
- `previousblockhash` (big-endian):
    
    `000002d42512f36787b9f4adb960502f0fa3e1f527d053f82234986ec59b830d`
    
    Em little-endian (invertendo os bytes):
    
    ```
    0d839bc56e983422f853d027f5e1a30f2f5060b9adf4b98767f31225d4020000
    ```
    
- `merkleroot` (big-endian = `txid` da coinbase):
    
    `1ed002fc5dadd422db257ec5f6f7ead9045e1ac2d0bae1298ed4d2e2c40ed177`
    
    Em little-endian:
    
    ```
    77d10ec4e2d2d48e29e1bad0c21a5e04d9eaf7f6c57e25db22d4ad5dfc02d01e
    ```
    
- `curtime = 1765822776`
    
    → hex = `0x69403af8`
    
    → little-endian: `f83a4069`
    
- `bits = 0x207fffff`
    
    → little-endian: `ffff7f20`
    
- `nonce` começa em `00000000` e será preenchido pelo minerador.

### Header base (sem nonce) e header final

Header **sem nonce** (76 bytes):

```
00000020
0d839bc56e983422f853d027f5e1a30f2f5060b9adf4b98767f31225d4020000
77d10ec4e2d2d48e29e1bad0c21a5e04d9eaf7f6c57e25db22d4ad5dfc02d01e
f83a4069
ffff7f20
```

Em uma linha:

```
000000200d839bc56e983422f853d027f5e1a30f2f5060b9adf4b98767f31225d402000077d10ec4e2d2d48e29e1bad0c21a5e04d9eaf7f6c57e25db22d4ad5dfc02d01ef83a4069ffff7f20
```

O script Python vai concatenar o nonce (em little-endian) no final e testar:

```
HEADER_FINAL = HEADER_BASE_NO_NONCE + NONCE_LE
```

Exemplo com nonce inicial `00000000`:

```
000000200d839bc56e983422f853d027f5e1a30f2f5060b9adf4b98767f31225d402000077d10ec4e2d2d48e29e1bad0c21a5e04d9eaf7f6c57e25db22d4ad5dfc02d01ef83a4069ffff7f2000000000
```

---

### Passo 5 — Minerador em Python (`miner_regtest.py`)

Agora vamos juntar tudo isso num script simples que:

1. define o `HEADER_BASE_NO_NONCE`
2. define a coinbase (`COINBASE_TX_HEX`)
3. escolhe um `target_custom` (opcionalmente mais difícil que o da rede, já que em regtest seria imediato)
4. faz brute-force do nonce até achar um hash abaixo do alvo

```python
#!/usr/bin/env python3
import binascii
import hashlib

COINBASE_TX_HEX = (
    "01000000"
    "01"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "ffffffff"
    "03"
    "020b06"
    "ffffffff"
    "02"
    "7c814a0000000000"
    "16"
    "0014f66bcc7b6238eff7e548553b19611c234ddfe4a4"
    "0000000000000000"
    "26"
    "6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48beb"
    "d836974e8cf9"
    "00000000"
)

VERSION_LE      = "00000020"
PREV_BLOCK_LE = "0d839bc56e983422f853d027f5e1a30f2f5060b9adf4b98767f31225d4020000"
MERKLE_ROOT_LE = "77d10ec4e2d2d48e29e1bad0c21a5e04d9eaf7f6c57e25db22d4ad5dfc02d01e"
TIME_LE = "f83a4069"
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
```

Rodando:

```bash
python3 miner_regtest.py
```

Você verá algo como:

```
✅ Nonce encontrado!
Nonce (decimal): 88461
Nonce (hex LE): 0001598d
Hash do bloco (big-endian): 000001f77a35e6eff98d1a6e4d912e3bc95eb7b8a11a545566481a9905ab216e
COINBASE_TX_HEX (primeiros 20 chars): 01000000010000000000

Bloco completo (hex) para submitblock:
000000200d839bc56e983422f853d027f5e1a30f2f5060b9adf4b98767f31225d402000077d10ec4e2d2d48e29e1bad0c21a5e04d9eaf7f6c57e25db22d4ad5dfc02d01ef83a4069ffff7f200001598d0101000000010000000000000000000000000000000000000000000000000000000000000000ffffffff03020b06ffffffff027c814a0000000000160014f66bcc7b6238eff7e548553b19611c234ddfe4a40000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf900000000
```

Esse `bloco_hex` é o que vamos enviar pro node.

---

### Passo 6 — Enviando o bloco com `submitblock` (antes e depois)

Com o bloco pronto, enviamos para o node:

```bash
bitcoin-cli -datadir="." submitblock "000000200d839bc56e983422f853d027f5e1a30f2f5060b9adf4b98767f31225d402000077d10ec4e2d2d48e29e1bad0c21a5e04d9eaf7f6c57e25db22d4ad5dfc02d01ef83a4069ffff7f200001598d0101000000010000000000000000000000000000000000000000000000000000000000000000ffffffff03020b06ffffffff027c814a0000000000160014f66bcc7b6238eff7e548553b19611c234ddfe4a40000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf900000000"
```

Se o bloco for aceito, o comando não imprime nada (volta direto pro prompt).

Agora vale repetir o `getblockchaininfo` para ver o efeito:

```bash
bitcoin-cli -datadir="." getblockchaininfo
```

Situação *depois* de minerar:

```bash
{
  "chain": "regtest",
  "blocks": 1547,
  "headers": 1547,
  "bestblockhash": "000001f77a35e6eff98d1a6e4d912e3bc95eb7b8a11a545566481a9905ab216e",
  "bits": "207fffff",
  "target": "7fffff0000000000000000000000000000000000000000000000000000000000",
  "difficulty": 4.656542373906925e-10,
  "time": 1765817080,
  "mediantime": 1765374951,
  "verificationprogress": 1,
  "initialblockdownload": false,
  "chainwork": "0000000000000000000000000000000000000000000000000000000000000c18",
  "size_on_disk": 478655,
  "pruned": false,
  "warnings": [
  ]
}
```

Comparando com o antes:

- `blocks` subiu de **1546 → 1547**
- `bestblockhash` agora é exatamente o hash que o script encontrou
- `chainwork` aumentou (mais um bloco de trabalho adicionado)

Pronto: você acabou de minerar um bloco na regtest **construindo tudo à mão**: coinbase, Merkle root, header, nonce, bloco completo e submissão.

---

Com isso, fechamos o ciclo completo da mineração no nível mais “baixo” possível usando um node Bitcoin Core em regtest: partimos do estado atual da blockchain, extraímos um `getblocktemplate`, construímos a coinbase com altura (BIP34) e witness commitment, derivamos o Merkle root, montamos o header de 80 bytes e fizemos o trabalho de PoW na prática testando nonces até encontrar um hash abaixo do alvo. No próximo artigo, saímos do “bloco em si” e entramos no que faz o Bitcoin ser uma rede: **P2P Bitcoin: como nodes conversam,** handshake, propagação de inventário, anúncio de transações e blocos. Em seguida, conectamos isso ao coração do node: **Chainstate, validação e políticas**, entendendo como o Bitcoin Core decide o que entra (e o que não entra) no mempool e na cadeia válida, e por que “consenso” e “política” são coisas diferentes.

Escrito por:  

Rafael Santos
