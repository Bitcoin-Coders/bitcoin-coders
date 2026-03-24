# Assinaturas no Bitcoin: o elo entre posse e gasto

Toda transação Bitcoin precisa provar que quem está tentando gastar um UTXO **é realmente o dono da chave privada** associada a ele. Essa prova é feita por meio de uma **assinatura digital**, gerada com a chave privada e verificada publicamente com a chave pública.

Ao contrário das senhas ou tokens, as assinaturas digitais não são reutilizáveis. Cada gasto gera uma assinatura única e qualquer alteração mínima na transação faz a assinatura se tornar inválida.

---

### Onde a assinatura aparece na transação

Uma transação Bitcoin é composta por **inputs**, **outputs** e alguns campos auxiliares (versão, locktime, etc). Cada **input** referencia um **output anterior** e precisa provar que tem autorização para gastar aquele valor. Essa prova vem justamente através da **assinatura** e da **chave pública** incluídas no campo `scriptSig` (ou `witness`, nos endereços SegWit).

Um exemplo clássico de transação P2PKH:

```bash
scriptSig:     <assinatura> <chave_publica>
scriptPubKey:  OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

Durante a validação, os dois scripts são **concatenados** e executados como uma única pilha.

Se o `OP_CHECKSIG` confirmar que a assinatura corresponde à chave pública e à transação, o gasto é aceito.

### O ciclo de validação

Podemos visualizar assim:

```bash
UTXO anterior (output bloqueado)
       ↓ scriptPubKey
Nova transação (tentando gastar)
       ↑ scriptSig
```

Quando o nó executa ambos, ele verifica:

1. se a assinatura é válida para o hash da transação,
2. se a chave pública bate com o hash160 esperado no scriptPubKey.

Se tudo estiver correto, o UTXO é desbloqueado e o gasto propagado pela rede.

### **O que é assinado exatamente?**

O Bitcoin não assina toda a transação, ele assina apenas partes dela, conforme um **tipo de assinatura** definido pelo campo **SIGHASH**. Esse byte extra no final da assinatura diz ao nó quais partes foram incluídas no hash antes da assinatura:

| Tipo | O que é assinado | Uso comum |
| --- | --- | --- |
| `SIGHASH_ALL` | Todos os inputs e outputs | padrão |
| `SIGHASH_NONE` | Todos os inputs, nenhum output | transações dinâmicas |
| `SIGHASH_SINGLE` | Input i e output i | transações parciais |
| `ANYONECANPAY` | Apenas o input atual | gastos cooperativos |

A maioria das transações padrão usa `SIGHASH_ALL`, garantindo que **nenhum campo** da transação possa mudar sem invalidar a assinatura.

### Explorando na prática

Vamos analisar uma transação real na *Signet* (P2PKH)*.* Pegue os dados (Hex) de uma transação e decodifique:

```bash
 bitcoin-cli -datadir="." -rpcwallet="demo-p2pkh-legacy" decoderawtransaction 0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd000000006a47304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb012102d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000
```

Saída:

```bash
{
  "txid": "3523ba016a13ba621223ffab879b1042494a0e707c8c61ba2285d6094276c96a",
  "hash": "3523ba016a13ba621223ffab879b1042494a0e707c8c61ba2285d6094276c96a",
  "version": 2,
  "size": 191,
  "vsize": 191,
  "weight": 764,
  "locktime": 0,
  "vin": [
    {
      "txid": "cd769e02a1dac7fa65f59f351cc109511588c99c06c26a84258b5b7d86c8f2fc",
      "vout": 0,
      "scriptSig": {
        "asm": "304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb[ALL] 02d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89",
        "hex": "47304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb012102d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89"
      },
      "sequence": 4294967293
    }
  ],
  "vout": [
    {
      "value": 0.00000600,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 603c773f8f14151e7e75e52d56074cf254359f71 OP_EQUALVERIFY OP_CHECKSIG",
        "desc": "addr(mpHobi2NgwhFpU7qyCgkTJFh9SZo63YFog)#hk0hqnqa",
        "hex": "76a914603c773f8f14151e7e75e52d56074cf254359f7188ac",
        "address": "mpHobi2NgwhFpU7qyCgkTJFh9SZo63YFog",
        "type": "pubkeyhash"
      }
    }
  ]
}
```

O resultado desse exemplo apresenta uma transação **legacy P2PKH** de **191 bytes**, com **1 input** e **1 output**, conforme abaixo:

- **txid**: `3523ba016a13ba621223ffab879b1042494a0e707c8c61ba2285d6094276c96a`
- **input**: referencia o `vout 0` da transação `cd769e02...f2fc`
- **output**: envia `0.00000600 BTC` para o endereço `mpHobi2NgwhFpU7qyCgkTJFh9SZo63YFog`

O campo `scriptSig` contém a **assinatura DER** e a **chave pública**:

```bash
"scriptSig": {
  "asm": "304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb[ALL] 02d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89"
}
```

- O bloco que começa com `3044...fb01` é a **assinatura em formato DER**.
- O último byte `01` indica o tipo **SIGHASH_ALL**.
- O segundo bloco, `02d05926...b4f89`, é a **chave pública compressa (33 bytes)**.

O `scriptPubKey` correspondente no output é um script P2PKH padrão:

```bash
OP_DUP OP_HASH160 603c773f8f14151e7e75e52d56074cf254359f71 OP_EQUALVERIFY OP_CHECKSIG
```

Esse script garante que apenas quem possuir a chave privada correspondente ao hash da chave pública `603c773f...` poderá gastar o valor enviado (o `OP_CHECKSIG` faz isso).

### Assinando manualmente

O Bitcoin Core possui um comando específico para assinar uma transação: `signrawtransactionwithwallet`. O processo de criação e assinatura de uma transação segue três etapas principais:
1. **Criação da transação bruta**, informando o `txid` e `vout` a serem gastos e o endereço de destino:

```bash
bitcoin-cli -datadir="." -rpcwallet="demo-p2pkh-legacy" \
  createrawtransaction '[{"txid":"cd769e02a1dac7fa65f59f351cc109511588c99c06c26a84258b5b7d86c8f2fc","vout":0}]' \
  '{"mpHobi2NgwhFpU7qyCgkTJFh9SZo63YFog":0.00000600}'
0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd0000000000fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000
```

2. **Adição de taxa e troco** (opcional, se o valor do input não for exato):

```bash
bitcoin-cli -datadir="." -rpcwallet="demo-p2pkh-legacy" \
  fundrawtransaction "0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd0000000000fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000" '{"feeRate":0.00000400}'
{
  "hex": "0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd0000000000fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000",
  "fee": 0.00000400,
  "changepos": -1
}
```

Um `Hex` é gerado relativo a transação. Podemos decodificar os dados dessa transação que ainda não foi assinada:

```bash
bitcoin-cli -datadir="." -rpcwallet=demo-p2pkh-legacy decoderawtransaction 0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd0000000000fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000
{
  "txid": "730dad3cdbd30ba86699a775b004ae1138cfeeb009628e6de0871fb6aedd12dd",
  "hash": "730dad3cdbd30ba86699a775b004ae1138cfeeb009628e6de0871fb6aedd12dd",
  "version": 2,
  "size": 85,
  "vsize": 85,
  "weight": 340,
  "locktime": 0,
  "vin": [
    {
      "txid": "cd769e02a1dac7fa65f59f351cc109511588c99c06c26a84258b5b7d86c8f2fc",
      "vout": 0,
      "scriptSig": {
        "asm": "",
        "hex": ""
      },
      "sequence": 4294967293
    }
  ],
  "vout": [
    {
      "value": 0.00000600,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 603c773f8f14151e7e75e52d56074cf254359f71 OP_EQUALVERIFY OP_CHECKSIG",
        "desc": "addr(mpHobi2NgwhFpU7qyCgkTJFh9SZo63YFog)#hk0hqnqa",
        "hex": "76a914603c773f8f14151e7e75e52d56074cf254359f7188ac",
        "address": "mpHobi2NgwhFpU7qyCgkTJFh9SZo63YFog",
        "type": "pubkeyhash"
      }
    }
  ]
}
```

Perceba que o `scriptSig` está vazio, ou seja, essa transação não possui os dados de desbloqueio e se for transmitida assim, não será aceita pela rede.

3. **Assinatura com a carteira**:

Agora vamos assinar a transação:

```bash
bitcoin-cli -datadir="." -rpcwallet="demo-p2pkh-legacy" signrawtransactionwithwallet 0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd0000000000fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000
{
  "hex": "0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd000000006a47304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb012102d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000",
  "complete": true
}
```

O `“complete”: true` já indica que está completa (assinada), mas vamos decodificar o `hex`:

```bash
bitcoin-cli -datadir="." -rpcwallet=demo-p2pkh-legacy decoderawtransaction 0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd000000006a47304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb012102d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000
{
  "txid": "3523ba016a13ba621223ffab879b1042494a0e707c8c61ba2285d6094276c96a",
  "hash": "3523ba016a13ba621223ffab879b1042494a0e707c8c61ba2285d6094276c96a",
  "version": 2,
  "size": 191,
  "vsize": 191,
  "weight": 764,
  "locktime": 0,
  "vin": [
    {
      "txid": "cd769e02a1dac7fa65f59f351cc109511588c99c06c26a84258b5b7d86c8f2fc",
      "vout": 0,
      "scriptSig": {
        "asm": "304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb[ALL] 02d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89",
        "hex": "47304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb012102d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89"
      },
      "sequence": 4294967293
    }
  ],
  "vout": [
    {
      "value": 0.00000600,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 603c773f8f14151e7e75e52d56074cf254359f71 OP_EQUALVERIFY OP_CHECKSIG",
        "desc": "addr(mpHobi2NgwhFpU7qyCgkTJFh9SZo63YFog)#hk0hqnqa",
        "hex": "76a914603c773f8f14151e7e75e52d56074cf254359f7188ac",
        "address": "mpHobi2NgwhFpU7qyCgkTJFh9SZo63YFog",
        "type": "pubkeyhash"
      }
    }
  ]
}
```

Agora o `scriptSig` está preenchido e a transação está pronta para ser transmitida.

```bash
bitcoin-cli -datadir="." -rpcwallet="demo-p2pkh-legacy" sendrawtransaction 0200000001fcf2c8867d5b8b25846ac2069cc988155109c11c359ff565fac7daa1029e76cd000000006a47304402205900c10f73c239b7d731ec704dc11937bff3bcbb56094214c80c5e6d73fe8f70022030756bad8a00a9e1f2b971d6851eabf3cf0689c27b55d3efb8b1941b0d59dafb012102d0592672fe7b5d840f54eb47775eed94104339433377fbb1bc5a2818290b4f89fdffffff0158020000000000001976a914603c773f8f14151e7e75e52d56074cf254359f7188ac00000000
3523ba016a13ba621223ffab879b1042494a0e707c8c61ba2285d6094276c96a
```

### **O elo completo**

O fluxo completo entre **chave privada, assinatura e script** pode ser resumido assim:

```bash
Chave privada → Assinatura DER → Validada com chave pública → Execução do script
```

Durante a verificação, o nó Bitcoin:

1. Recalcula o *hash* da transação de acordo com o `SIGHASH`.
2. Usa a **chave pública** para validar a **assinatura DER**.
3. Confere se o `hash160(pubKey)` corresponde ao valor presente no `scriptPubKey`.

Se todas as verificações forem verdadeiras, o `OP_CHECKSIG` retorna verdadeiro e o gasto é aceito pela rede.

---

As assinaturas digitais são o elo matemático que conecta **posse e gasto** no Bitcoin. Elas garantem que apenas o detentor da chave privada possa movimentar os fundos, sem necessidade de confiança ou autorização externa. Cada assinatura torna-se um selo criptográfico único, impossível de reutilizar ou falsificar.

Compreender o papel das assinaturas dentro das transações é apenas o primeiro passo. Por trás de cada sequência hexadecimal em um `scriptSig` existe uma construção matemática elegante, o algoritmo **ECDSA**, que transforma números aleatórios em provas criptográficas de autenticidade. No próximo artigo, avançaremos para dentro dessa mecânica: como o Bitcoin utiliza a curva elíptica **secp256k1**, como surgem os valores `(r, s)` que compõem a assinatura **DER**, e por que cada byte final (como o **SIGHASH**) determina exatamente o que está sendo protegido. É o momento de abrir a assinatura e ver, bit a bit, como a matemática garante a soberania de cada transação.


por Rafael Santos

