# Como os Scripts se transformam em Endereços no Bitcoin

por Rafael Santos

Toda transação no Bitcoin contém um **script de bloqueio** (*scriptPubKey*): um pequeno programa que define **quem pode gastar** e **em quais condições**. Mas o que chamamos de **endereço** é apenas uma **representação compacta** desse script: um **envelope codificado** que guarda o **hash** da chave pública ou do script, e não o código completo.

O **node não valida endereços**. Ele valida **scripts**, comparando o que foi gravado no *scriptPubKey* (cadeado) com o que o gastador fornece no *scriptSig* ou *witness* (chave).

O endereço é, portanto, **uma forma conveniente e legível** de representar o destino de um script. O que muda entre os formatos *Legacy* e *SegWit* é apenas o **envelope**, enquanto o **miolo** (o hash de 20 ou 32 bytes) continua sendo o mesmo identificador de referência.

---

## 🧱 A. Escolha o “cadeado” — a condição de gasto

Cada tipo de endereço nasce de um tipo diferente de *cadeado*, que define o que será exigido quando os fundos forem gastos:

| Tipo | Regra de gasto | Hash usado |
| --- | --- | --- |
| **P2PKH (legacy)** | Apresente `pubkey` + `assinatura` que valide para `HASH160(pubkey)` | `HASH160(pubkey)` |
| **P2SH (script-hash)** | Apresente um `redeemScript` cujo `HASH160(script)` corresponda + os dados que o satisfazem | `HASH160(script)` |
| **P2WPKH (SegWit v0)** | Witness program `v=0`, com 20 bytes de `HASH160(pubkey)` | `HASH160(pubkey)` |
| **P2WSH (SegWit v0)** | Witness program `v=0`, com 32 bytes de `SHA256(script)` | `SHA256(script)` |

Esse *hash* é o **coração do endereço**, é o que o node usa para saber qual script validar.

---

## 🔩 B. O scriptPubKey — o “cadeado” em código

Depois de escolher o tipo de condição, o Bitcoin grava o programa equivalente no *scriptPubKey* do output.

| Tipo | Estrutura do scriptPubKey | Observação |
| --- | --- | --- |
| **P2PKH** | `OP_DUP OP_HASH160 <20B> OP_EQUALVERIFY OP_CHECKSIG` | o mais comum (endereços “1” ou “m/n”) |
| **P2SH** | `OP_HASH160 <20B> OP_EQUAL` | usado em multisig, scripts compostos |
| **P2WPKH** | `0 <20B>` | formato SegWit simplificado |
| **P2WSH** | `0 <32B>` | usado em scripts complexos SegWit |

🧠 Nesse ponto, o *scriptPubKey* guarda toda a lógica, mas o endereço só vai armazenar o **hash** que está dentro dele.

---

## ✉️ C. “Envelopando” o script em um endereço

Agora vem o empacotamento: o script (ou seu hash) é convertido em um **endereço legível**. Existem apenas **dois sistemas de codificação** usados no Bitcoin atual, o *Base58Check e o Bech32 / Bech32m.* Vamos ver um exemplo de endereço Legacy (Base58) para entender melhor.

### 🟠 Legacy — *Base58Check*

| Tipo | Prefixo | Exemplo (Signet/Testnet) |
| --- | --- | --- |
| **P2PKH** | versão `0x6f` → começa com `m` ou `n` | `mw1v7YAUzMdCpWHjNm6He56SkFc2NabyGx` |
| **P2SH** | versão `0xc4` → começa com `2` | `2MuHsVSqmSpoddRxrDoAbpP6Jya38pDNFid` |

A codificação Base58Check (que remove caracteres ambíguos `0`, `O`, `I`, `l`) inclui:

**prefixo + hash + checksum**.

📦 Exemplo de P2PKH na signet:

```bash
Hash160(pubkey) = aa0420f7f934bce88e817ccaa33f06208f106815
Versão = 6f
Payload = 6faa0420f7f934bce88e817ccaa33f06208f106815
Checksum = 86aa3fbd (SHA256^2)
```

Cada parte representa uma etapa do empacotamento do endereço em **Base58Check**:

- **Hash160(pubkey)** é o núcleo do endereço, o identificador derivado da chave pública, calculado por `RIPEMD160(SHA256(pubkey))`. Esse hash de 20 bytes é o que o *scriptPubKey* realmente usa para vincular os fundos ao dono.
- **Versão (6f)** indica a rede e o tipo de endereço. O valor `0x6f` identifica endereços P2PKH da **testnet/signet** (na mainnet, seria `0x00`).
- **Payload** é a junção desses dois elementos: `versão + hash`. Ele representa os **21 bytes** de dados que serão codificados.
- **Checksum (86aa3fbd)** é um código de verificação calculado como os **4 primeiros bytes** do `SHA256(SHA256(payload))`. Ele garante que qualquer erro de digitação no endereço possa ser detectado pelo node.

Depois disso, o Bitcoin **concatena o payload + checksum**: 

```bash
6faa0420f7f934bce88e817ccaa33f06208f10681586aa3fbd
```

E depois converte o resultado de hexadecimal para **Base58**:

```bash
mw1v7YAUzMdCpWHjNm6He56SkFc2NabyGx
```

💡 Assim, o endereço não contém a chave pública nem o script completo, apenas um resumo criptográfico (o hash) embalado com uma versão e um checksum.

---

## 🔍 D. Interpretação do endereço — decodificando o envelope

Podemos olhar por outro ponto de vista para tentar entender. Quando executamos:

```bash
bitcoin-cli -datadir="." sendtoaddress mqnHAHB3qrdLinFYASUyPnhFUNjEi7BJdv 0.0001
```

o Bitcoin Core primeiro **decodifica o endereço**.

Esse passo não é "mágico", ele apenas **desfaz a codificação Base58Check**, revelando os dados que estavam dentro do envelope.

Vamos ver o que tem dentro:

| Etapa | Descrição | Valor (hex) |
| --- | --- | --- |
| 1️⃣ | **Endereço (Base58Check)** | `mqnHAHB3qrdLinFYASUyPnhFUNjEi7BJdv` |
| 2️⃣ | **Decodifica Base58Check → bytes Hex (25B)** | `6f70973eeb12ae6b7aba4af95fa045251792219ac626959791` |
| 3️⃣ | **Primeiro byte (versão)** | `6f` → prefixo **testnet/signet** para P2PKH |
| 4️⃣ | **Próximos 20 bytes (hash)** | `70973eeb12ae6b7aba4af95fa045251792219ac6` → **HASH160(pubkey)** |
| 5️⃣ | **Últimos 4 bytes (checksum)** | `26959791` → usado só para detecção de erro (não entra no script) |

✅ Assim, o node sabe duas coisas:

- É um endereço **P2PKH (legacy)**, porque o prefixo é `0x6f`;
- O dado essencial é `70973eeb12ae6b7aba4af95fa045251792219ac6` → isso será o `<20B>` usado dentro do **scriptPubKey**.

Podemos usar o comando `validateaddress` para verificar o **scriptPubKey** desse endereço:

```bash
bitcoin-cli -datadir="." validateaddress mqnHAHB3qrdLinFYASUyPnhFUNjEi7BJdv
{
  "isvalid": true,
  "address": "mqnHAHB3qrdLinFYASUyPnhFUNjEi7BJdv",
  "scriptPubKey": "76a91470973eeb12ae6b7aba4af95fa045251792219ac688ac",
  "isscript": false,
  "iswitness": false
}
```

Onde:

- `0x76` → `OP_DUP`
- `0xa9` → `OP_HASH160`
- `0x14` → push de **20 bytes**
- `70973eeb12ae6b7aba4af95fa045251792219ac6` → **HASH160(pubkey)** do destinatário
- `0x88` → `OP_EQUALVERIFY`
- `0xac` → `OP_CHECKSIG`

Confirmando que é o **scriptPubKey** de um endereço **P2PKH:**

```bash
OP_DUP OP_HASH160 <20B> OP_EQUALVERIFY OP_CHECKSIG
```

---

### Na Prática no Bitcoin Core

Vamos ver na prática como essa relação entre endereço e script funciona no Bitcoin Core. Depois que o Bitcoin Core identifica o tipo de endereço e monta o `scriptPubKey`, ele o insere dentro do **output (`vout`)** da transação.

Vamos acompanhar esse caminho completo, usando o exemplo:

```bash
bitcoin-cli -datadir="." -rpcwallet="demo-signet" sendtoaddress mqnHAHB3qrdLinFYASUyPnhFUNjEi7BJdv 0.00001
# 75f5aca348df3655d06a2025c5f03f6914dadb95d6816b49c46168262f05a90f
```

---

### 1️⃣ Verificando a transação gerada

Usamos o comando `getrawtransaction` seguido de `decoderawtransaction` para ver a estrutura:

```bash
bitcoin-cli -datadir="." getrawtransaction 75f5aca348df3655d06a2025c5f03f6914dadb95d6816b49c46168262f05a90f true
```

Saída resumida:

```json
{
  "txid": "75f5aca348df3655d06a2025c5f03f6914dadb95d6816b49c46168262f05a90f",
  ...
  "vin": [
    {
      "txid": "96ab64155223063c1a7eb6f78887ee82b87d014c4e8b7567295548237bc06b6c",
      "vout": 1,
      "scriptSig": {
        "asm": "304402206dbeb0b23281018617d432b6a1c8a722969ae3b54c71fc191545537f6813121e02200ecd4f241831e26d6fbe1c570895894dd0ed0a8146490754608c121252548a13[ALL] 03d6d18224c3648a5a3d74367df185738bf02c82a92b2e7f7c84eb71a59530dda8",
        ...
    }
  ],
  "vout": [
    {
      "value": 0.00008771,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 50665900f9429c524b51edcc09337b1540993a54 OP_EQUALVERIFY OP_CHECKSIG",
        ...
        "address": "mnr4xe9dEoh4Lfvqhu8AkMdBSm88EF1EsM",
        "type": "pubkeyhash"
      }
    },
    {
      "value": 0.00001000,
      "n": 1,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 70973eeb12ae6b7aba4af95fa045251792219ac6 OP_EQUALVERIFY OP_CHECKSIG",
				...
        "address": "mqnHAHB3qrdLinFYASUyPnhFUNjEi7BJdv",
        "type": "pubkeyhash"
      }
    }
  ],
...
}
```

💡 Observe que o **hash de 20 bytes** que estava escondido no endereço (`70973eeb12ae6b7aba4af95fa045251792219ac6`) é o mesmo embutido no `scriptPubKey` do `vout` 1.

---

### 2️⃣ Gastando esse output

Podemos agora fazer uma transação, onde esse `vout` será referenciado por outro `vin`.

Gere um **endereço legacy** (P2PKH) pra receber:

```bash
 bitcoin-cli -datadir="." -rpcwallet="demo-signet" getnewaddress "" legacy
mndXgE9HM8LLi1TRuaCcd52qtWMbHfeuaG
```

**a) Criar a TX bruta (só com o input e um output)**

Vamos enviar **0.00000900 BTC** (900 sats) e subtrair a **taxa do próprio output**. Assim garantimos que **só esse input** será usado.

```bash
bitcoin-cli -datadir="." -rpcwallet="demo-signet" createrawtransaction \
  '[{"txid":"75f5aca348df3655d06a2025c5f03f6914dadb95d6816b49c46168262f05a90f","vout":1}]' \
  '{"mndXgE9HM8LLi1TRuaCcd52qtWMbHfeuaG":0.00000900}'
02000000010fa9052f266861c4496b81d695dbda14693ff0c525206ad05536df48a3acf5750100000000fdffffff0184030000000000001976a9144e073e0dc8a9b26ae890b503d9c600e914c059d888ac00000000
```

**b) Completar Transação**

Use `fundrawtransaction` para completar a transação:

```bash
bitcoin-cli -datadir="." -rpcwallet="demo-signet" fundrawtransaction   02000000010fa9052f266861c4496b81d695dbda14693ff0c525206ad05536df48a3acf5750100000000fdffffff0184030000000000001976a9144e073e0dc8a9b26ae890b503d9c600e914c059d888ac00000000 '{"subtractFeeFromOutputs":[0]}'
{
  "hex": "02000000010fa9052f266861c4496b81d695dbda14693ff0c525206ad05536df48a3acf5750100000000fdffffff0125030000000000001976a9144e073e0dc8a9b26ae890b503d9c600e914c059d888ac00000000",
  "fee": 0.00000195,
  "changepos": -1
}
```

O retorno traz `hex` (a tx ajustada) e `fee`.

**c) Assinar com a carteira**

```bash
bitcoin-cli -datadir="." -rpcwallet="demo-signet" signrawtransactionwithwallet 02000000010fa9052f266861c4496b81d695dbda14693ff0c525206ad05536df48a3acf5750100000000fdffffff0125030000000000001976a9144e073e0dc8a9b26ae890b503d9c600e914c059d888ac00000000
{
  "hex": "02000000010fa9052f266861c4496b81d695dbda14693ff0c525206ad05536df48a3acf575010000006a47304402207e9a79a13fe534bf3c0f319748801ed4c9c3e9c75545f68eaf84d899428abee80220076b60df6fa63dfe8b5411753ef093afa3c3ad6b0918559ae093561b660b61cc012103d6d18224c3648a5a3d74367df185738bf02c82a92b2e7f7c84eb71a59530dda8fdffffff0125030000000000001976a9144e073e0dc8a9b26ae890b503d9c600e914c059d888ac00000000",
  "complete": true
}
```

**d) Enviar Transação**

```bash
bitcoin-cli -datadir="." sendrawtransaction 02000000010fa9052f266861c4496b81d695dbda14693ff0c525206ad05536df48a3acf575010000006a47304402207e9a79a13fe534bf3c0f319748801ed4c9c3e9c75545f68eaf84d899428abee80220076b60df6fa63dfe8b5411753ef093afa3c3ad6b0918559ae093561b660b61cc012103d6d18224c3648a5a3d74367df185738bf02c82a92b2e7f7c84eb71a59530dda8fdffffff0125030000000000001976a9144e073e0dc8a9b26ae890b503d9c600e914c059d888ac00000000
# 245e1628c0c7b53682655236125cb13c011a3ea511d32f62fc25051923f29bb9
```

**e) Ver o `scriptSig` (assinatura + pubkey reais)**

Agora, decodifique a transação que gasta o seu `vout=1`:

```bash
bitcoin-cli -datadir="." getrawtransaction 245e1628c0c7b53682655236125cb13c011a3ea511d32f62fc25051923f29bb9 true
```

Procure em `vin[0].scriptSig.asm`. Você verá algo assim:

```
"scriptSig": {
  "asm": "<DER-assinatura>[SIGHASH_ALL] <pubkey-33-bytes-compressa>",
  ...
}
```

```bash
"scriptSig": {
        "asm": "304402207e9a79a13fe534bf3c0f319748801ed4c9c3e9c75545f68eaf84d899428abee80220076b60df6fa63dfe8b5411753ef093afa3c3ad6b0918559ae093561b660b61cc[ALL] 03d6d18224c3648a5a3d74367df185738bf02c82a92b2e7f7c84eb71a59530dda8"
```

- O **primeiro push** é a **assinatura DER** (termina com um byte de *sighash*, ex.: `...01` para `SIGHASH_ALL`).
- O **segundo push** é a **chave pública** (33 bytes, começa com `02` ou `03`).

**f) Validar que o hash do endereço bate no `scriptPubKey`**

Ainda com o `getrawtransaction`, podemos confirmar que o `vout` que foi pago **tem**:

```json
"scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 4e073e0dc8a9b26ae890b503d9c600e914c059d8 OP_EQUALVERIFY OP_CHECKSIG",
        "desc": "addr(mndXgE9HM8LLi1TRuaCcd52qtWMbHfeuaG)#8gy7drdx",
        "hex": "76a9144e073e0dc8a9b26ae890b503d9c600e914c059d888ac",
        "address": "mndXgE9HM8LLi1TRuaCcd52qtWMbHfeuaG",
        "type": "pubkeyhash"

```

É o mesmo **HASH160(pubkey)** escondido no endereço.

---

Com isso, completamos o caminho que liga o **endereço visível** ao **script real** que o Bitcoin executa.

Quando você envia para um endereço, o que vai para a blockchain é o *scriptPubKey,* o “cadeado” codificado que protege os fundos até que uma chave privada prove sua posse.

Cada tipo de endereço, seja *Legacy*, *SegWit* ou *Taproot,* muda apenas o **envelope** dessa regra, mas o princípio é sempre o mesmo: o node vai exigir que, na hora do gasto, a transação apresente os dados certos (assinatura, chave pública, script) para que a execução retorne **TRUE**.

👉 No próximo artigo, mergulharemos justamente nessa segunda metade da equação: **as assinaturas digitais** que dão vida a essas regras. Veremos como o Bitcoin transforma uma chave privada em prova matemática de autorização, explorando os mecanismos de **ECDSA**, **Schnorr** e os diferentes modos de assinatura (*SIGHASH*), que definem **como** e **até onde** uma transação é validada.
