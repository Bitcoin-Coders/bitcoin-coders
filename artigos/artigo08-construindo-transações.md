# Construindo Transações no Bitcoin Core

por Rafael Santos

No artigo anterior exploramos a anatomia de uma transação no Bitcoin, entendendo como os inputs e outputs se conectam ao modelo UTXO e como o Bitcoin Core pode lidar com diferentes níveis de automação, desde a criação totalmente automática até a montagem bruta de um hex. Essa visão foi essencial para compreender a lógica interna do protocolo e perceber como cada parte da transação tem um papel fundamental na validação pela rede.

Agora, daremos um passo além: o objetivo deste artigo é **aprender a criar transações de diferentes tipos e cenários**, colocando em prática a construção manual com o Bitcoin Core. Vamos começar com exemplos simples e explorar situações reais, como o envio para múltiplos destinatários (batching), a criação de transações com troco, a consolidação de UTXOs e o controle manual das taxas. 

Para dominar a criação de transações no Bitcoin Core, é importante ir além do caso mais simples e experimentar diferentes cenários que refletem situações reais de uso. Cada um deles pode nos ensinar algo específico sobre como o protocolo funciona e como podemos ter maior controle sobre nossos UTXOs e taxas.

Utilizaremos nesse artigo a rede `regtest`, nao esqueça de configurar o arquivo `bitcoin.conf`. Você pode usar a `signet` também, apenas vai ter que esperar os sBTC entrarem depois de solicitar no faucet.

---

## Transação simples e o papel do troco

Esse é o exemplo mais básico: gastar um único UTXO para enviar fundos a apenas um destinatário. Mas mesmo na “transação simples”, temos nuances importantes a considerar. Caso não tenha nenhum UTXO, crie um endereço para sua carteira e minere 101 blocos (pra tornar gastável):

```bash
bitcoin-cli -datadir="." getnewaddress
# bcrt1q7nt3cskcna7pshru94t2s6tgfpxqymlkp0eh6p
```

```bash
bitcoin-cli -datadir="." generatetoaddress 101 bcrt1q7nt3cskcna7pshru94t2s6tgfpxqymlkp0eh6p
```

- Agora, em primeiro lugar, listamos os UTXOs disponíveis na carteira:

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "c3fef1a9764c57262ef70c2f11eb5bf548cbbcaeb7d900a77ae9ac25cb3954de",
    "vout": 0,
    "address": "bcrt1q7nt3cskcna7pshru94t2s6tgfpxqymlkp0eh6p",
    "label": "",
    "scriptPubKey": "0014f4d71c42d89f7c185c7c2d56a86968484c026ff6",
    "amount": 50.00000000,
    "confirmations": 101,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/0]024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba7)#ah5fng3d",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  }
]
```

Neste caso, temos um UTXO com 50 BTCs para gastar. Vamos ver alguns cenários.

**1️⃣ Enviar parte do valor, deixando o Core criar troco**

Aqui vamos supor que queremos mandar **0.5 BTC** e deixar o Core calcular taxa e gerar endereço de troco.

**a. Criar o hex bruto sem taxa nem troco**

```bash
bitcoin-cli -datadir="." createrawtransaction   '[{"txid":"c3fef1a9764c57262ef70c2f11eb5bf548cbbcaeb7d900a77ae9ac25cb3954de","vout":0}]'   '{"bcrt1qkqp9xzkre29gl7kl7d3s264nstysw7fqjj5pqf":0.5}'
0200000001de5439cb25ace97aa700d9b7aebccb48f55beb112f0cf72e26574c76a9f1fec30000000000fdffffff0180f0fa0200000000160014b002530ac3ca8a8ffadff363056ab382c907792000000000

```

**b. Completar com taxa e troco automático**

Esse Hex gerado acima é utilizado no comando fundrawtransaction, que completa a transação com a taxa e o troco.

```bash
bitcoin-cli -datadir="." fundrawtransaction "0200000001de5439cb25ace97aa700d9b7aebccb48f55beb112f0cf72e26574c76a9f1fec30000000000fdffffff0180f0fa0200000000160014b002530ac3ca8a8ffadff363056ab382c907792000000000"  '{"feeRate":0.00001000}'
{
  "hex": "0200000001de5439cb25ace97aa700d9b7aebccb48f55beb112f0cf72e26574c76a9f1fec30000000000fdffffff0280f0fa0200000000160014b002530ac3ca8a8ffadff363056ab382c9077920f3000b2701000000160014fcde2eebcd45d4e852907d8de7051e5a9e9a472700000000",
  "fee": 0.00000141,
  "changepos": 1
}
```

Um novo valor Hex é gerado, agora representado a transação completa.

**c. Assinar e enviar**

```bash
bitcoin-cli -datadir="." signrawtransactionwithwallet "0200000001de5439cb25ace97aa700d9b7aebccb48f55beb112f0cf72e26574c76a9f1fec30000000000fdffffff0280f0fa0200000000160014b002530ac3ca8a8ffadff363056ab382c9077920f3000b2701000000160014fcde2eebcd45d4e852907d8de7051e5a9e9a472700000000"
{
  "hex": "02000000000101de5439cb25ace97aa700d9b7aebccb48f55beb112f0cf72e26574c76a9f1fec30000000000fdffffff0280f0fa0200000000160014b002530ac3ca8a8ffadff363056ab382c9077920f3000b2701000000160014fcde2eebcd45d4e852907d8de7051e5a9e9a4727024730440220139015403f1787b993f84616a737c4a51ac93976cae845e1bc3949a8245a21c702200fa867025026dd8a624896265bf9c44130d87c49845a4251f3917e79a042f87b0121024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba700000000",
  "complete": true
}
```

O `signrawtransactionwithwallet` assina a transação e o `sendrawtransaction` envia para a rede.

```bash
bitcoin-cli -datadir="." sendrawtransaction "02000000000101de5439cb25ace97aa700d9b7aebccb48f55beb112f0cf72e26574c76a9f1fec30000000000fdffffff0280f0fa0200000000160014b002530ac3ca8a8ffadff363056ab382c9077920f3000b2701000000160014fcde2eebcd45d4e852907d8de7051e5a9e9a4727024730440220139015403f1787b993f84616a737c4a51ac93976cae845e1bc3949a8245a21c702200fa867025026dd8a624896265bf9c44130d87c49845a4251f3917e79a042f87b0121024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba700000000"
1417f599358ea49a63dd253a3b3701ce0fa28cdf006522e4a3c50c48fce12e8e

```

Logo após, mineramos mais um bloco para confirmar a transação enviada.

```bash
bitcoin-cli -datadir="." generatetoaddress 1 bcrt1q9w437k3luux5crekejss56r8cysxhr4ypuha22
```

Então podemos observar nosso UTXO mais uma vez.

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "b260fe7dd4eac4dca8b70d58e8cff68fb3f5753a61dc0856e658bbe731736c90",
    "vout": 0,
    "address": "bcrt1q7nt3cskcna7pshru94t2s6tgfpxqymlkp0eh6p",
    "label": "",
    "scriptPubKey": "0014f4d71c42d89f7c185c7c2d56a86968484c026ff6",
    "amount": 50.00000000,
    "confirmations": 101,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/0]024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba7)#ah5fng3d",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
    "txid": "1417f599358ea49a63dd253a3b3701ce0fa28cdf006522e4a3c50c48fce12e8e",
    "vout": 0,
    "address": "bcrt1qkqp9xzkre29gl7kl7d3s264nstysw7fqjj5pqf",
    "label": "",
    "scriptPubKey": "0014b002530ac3ca8a8ffadff363056ab382c9077920",
    "amount": 0.50000000,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/1]0238caef26a2025d89d4230bcc7e2d1dbdcc8ce51ce1c07cd4509a76495bba07d9)#8q3llhqf",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
    "txid": "1417f599358ea49a63dd253a3b3701ce0fa28cdf006522e4a3c50c48fce12e8e",
    "vout": 1,
    "address": "bcrt1qln0za67dgh2ws55s0kx7wpg7t20f53e8envezx",
    "scriptPubKey": "0014fcde2eebcd45d4e852907d8de7051e5a9e9a4727",
    "amount": 49.49999859,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/1/0]03f032737bcfe1ccb7cf642458916102c22386727a2e3be2f36cdc4cb6ab37c3b9)#nyyqzwmx",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/1/*)#jtyys78l"
    ],
    "safe": true
  }
]

```

Perceba que temos 3 UTXO, o primeiro é referente a recompensa dessa nova mineração que acabamos de fazer, então podemos ignorar aqui. O segundo UTXO é referente ao endereço pra qual mandamos a transação. Já o terceiro, é o endereço de troco gerado na transação, e possui `49.49999859 BTC` (50 dos BTC originais - 0,5 enviados - taxa).

**2️⃣ Gastar todo o valor, subtraindo a taxa automaticamente**

Neste caso, queremos **enviar todo o saldo do UTXO para um único endereço**, sem gerar endereço de troco.

O Bitcoin Core permite que a própria taxa seja **descontada do valor de envio**, de forma que o output final já considere a taxa de mineração.

**a. Criar endereço de destino**

```bash
bitcoin-cli -datadir="." getnewaddress
#bcrt1qkyrgk8wkau455lytvggyp5wwtds2rr2m0f5kfg
```

**b. Enviar todo o saldo, subtraindo a taxa**
Podemos usar o comando `sendtoaddress` com o parâmetro `subtractfeefromamount=true` para enviar todo saldo de um UTXO:

```bash
bitcoin-cli -datadir="." sendtoaddress \
  bcrt1qkyrgk8wkau455lytvggyp5wwtds2rr2m0f5kfg \
  49.49999859 \
  "" "" \
  true
#828ec7cedc36f9517bd44a8e2a813be906698125c7c80b9a71a3202f2c09438c
```

- O valor de **49.49999859 BTC** corresponde ao **UTXO de troco** que recebemos no cenário anterior.
- O último argumento `true` faz com que a taxa de mineração seja descontada desse valor, evitando que o Core crie um endereço de troco.

A saída do comando já retorna o `txid` da nova transação.

**d. Confirmar em bloco**
Em seguida podemos minerar novamente para confirmar em um bloco.

```bash
bitcoin-cli -datadir="." generatetoaddress 1 bcrt1q9w437k3luux5crekejss56r8cysxhr4ypuha22
```

**e. Checar UTXO resultante**

Por fim, podemos conferir com o `listunspent`:

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "828ec7cedc36f9517bd44a8e2a813be906698125c7c80b9a71a3202f2c09438c",
    "vout": 0,
    "address": "bcrt1qkyrgk8wkau455lytvggyp5wwtds2rr2m0f5kfg",
    "label": "",
    "scriptPubKey": "0014b1068b1dd6ef2b4a7c8b621040d1ce5b60a18d5b",
    "amount": 49.49998759,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/3]02759296d087fc8a6746c5949ccf44fb8c1ec84fd2898f0b3d636a1fb861f279e8)#grjvnzy9",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
...
```

Note que agora temos um novo UTXO/txid com `49.49998759` BTC (49.49999859 BTC do UTXO Original - 0,000011 BTC da taxa).

**3️⃣ Gastar todo o valor ajustando a taxa manualmente**

Neste caso, queremos enviar **todo o saldo de um UTXO** para um único endereço **sem gerar troco**, mas **definindo nós mesmos a taxa** em vez de deixar o Core subtrair automaticamente.

A lógica é simples: **valor do output = valor do input – taxa desejada**.

Assim, a diferença entre entrada e saída é exatamente a taxa, e nenhum endereço de troco é necessário.

**a. Preparar o endereço de destino**

```bash
bitcoin-cli -datadir="." getnewaddress
# bcrt1qnpsadfag5mupmjyq3j8ksrr7rzxz6uawmpfuyk
```

**b. Calcular o valor de envio**

Suponha que o UTXO disponível seja de `49.49998759` **BTC** (UTXO do cenário 2) e queremos pagar uma taxa de `0.0001` **BTC**:

```bash
VALOR -> 49.49998759 - 0.0001
# 49.49988759
```

**c. Criar a transação bruta com valor já descontado**

```bash
bitcoin-cli -datadir="." createrawtransaction '[{"txid":"828ec7cedc36f9517bd44a8e2a813be906698125c7c80b9a71a3202f2c09438c","vout":0}]' '{"bcrt1qnpsadfag5mupmjyq3j8ksrr7rzxz6uawmpfuyk":49.49988759}'
# 02000000018c43092c2f20a3719a0bc8c725816906e93b812a8e4ad47b51f936dccec78e820000000000fdffffff0197d50a27010000001600149861d6a7a8a6f81dc8808c8f680c7e188c2d73ae00000000
```

O comando retorna um **hex bruto** que já não terá espaço para troco.

**d. Assinar**

```bash
bitcoin-cli -datadir="." signrawtransactionwithwallet "02000000018c43092c2f20a3719a0bc8c725816906e93b812a8e4ad47b51f936dccec78e820000000000fdffffff0197d50a27010000001600149861d6a7a8a6f81dc8808c8f680c7e188c2d73ae00000000"
{
  "hex": "020000000001018c43092c2f20a3719a0bc8c725816906e93b812a8e4ad47b51f936dccec78e820000000000fdffffff0197d50a27010000001600149861d6a7a8a6f81dc8808c8f680c7e188c2d73ae0247304402200a243753e4417acd396221ef6461adf023b2c6b29a3fde1c87311c6bfc2863140220322ab5d37b10cf336c6f9ef4d504dfa7a7b1b5280680b790d0be42e7662ca1de012102759296d087fc8a6746c5949ccf44fb8c1ec84fd2898f0b3d636a1fb861f279e800000000",
  "complete": true
}
```

**e. Enviar e confirmar**

```bash
bitcoin-cli -datadir="." sendrawtransaction "020000000001018c43092c2f20a3719a0bc8c725816906e93b812a8e4ad47b51f936dccec78e820000000000fdffffff0197d50a27010000001600149861d6a7a8a6f81dc8808c8f680c7e188c2d73ae0247304402200a243753e4417acd396221ef6461adf023b2c6b29a3fde1c87311c6bfc2863140220322ab5d37b10cf336c6f9ef4d504dfa7a7b1b5280680b790d0be42e7662ca1de012102759296d087fc8a6746c5949ccf44fb8c1ec84fd2898f0b3d636a1fb861f279e800000000"
# 647c2b177ddeeb222e339e69a3237bdaca71aad881a6a81d74591c6a120934b4
```

```bash
bitcoin-cli -datadir="." generatetoaddress 1 bcrt1q9w437k3luux5crekejss56r8cysxhr4ypuha22
```

**f. Conferir o novo UTXO**

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "647c2b177ddeeb222e339e69a3237bdaca71aad881a6a81d74591c6a120934b4",
    "vout": 0,
    "address": "bcrt1qnpsadfag5mupmjyq3j8ksrr7rzxz6uawmpfuyk",
    "label": "",
    "scriptPubKey": "00149861d6a7a8a6f81dc8808c8f680c7e188c2d73ae",
    "amount": 49.49988759,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/4]03df6d57b8af03faf7ff2aeee55347c397ea08756403d88d5d2981e546529939e8)#9xz6j0nm",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
  ...
```

---

Ao longo desses três cenários vimos que, mesmo em uma transação “simples”, o **troco** é o detalhe que separa uma operação segura de um erro caro:

- **Cenário 1** – Envio parcial: o Core cria automaticamente um endereço de troco e calcula a taxa.
- **Cenário 2** – Envio total com `subtractfeefromamount`: o Core deduz a taxa do próprio output, evitando troco.
- **Cenário 3** – Envio total com taxa manual: você mesmo define `input – output = taxa`, sem troco.

⚠️ **Se você ignora o troco**, por exemplo, cria um `createrawtransaction` onde a soma dos outputs é menor que a soma dos inputs e **não adiciona nem troco nem `subtractfeefromamount,` toda a diferença vira taxa de mineração**.

Em mainnet isso pode significar perder muitos satoshis (ou bitcoins) em uma única transação.

Por isso, sempre se pergunte antes de assinar e transmitir:

- Os **outputs somam exatamente o que eu espero?**
- Estou deixando o Core cuidar do troco ou ajustei o valor manualmente para a taxa desejada?

Com essa checagem simples, você garante que cada satoshi vá para o destino certo e evita que “o resto” acabe nas mãos dos mineradores como taxa involuntária.

---

## **Transação com múltiplos outputs (batching)**

Uma prática comum para economizar taxas e espaço em bloco é enviar fundos para **vários destinatários dentro de uma única transação**. Esse método é conhecido como **batching** e é amplamente utilizado por exchanges e serviços de pagamento.

Em vez de criar várias transações, uma para cada pagamento, reunimos todos os outputs em um só *raw transaction*. O resultado é um **único input** (ou alguns inputs selecionados) alimentando **vários outputs**, reduzindo a taxa total, pois ela depende principalmente do tamanho em vbytes e não do valor transferido.

Vamos ver em um caso prático.

**a. Preparar os endereços de destino**
Vamos criar dois endereços para simular destinatários diferentes:

```bash
bitcoin-cli -datadir="." getnewaddress
# bcrt1q7waheqekh39xlscz5ct28dqhhhh0u8v8nwh42n (Kaká)
```

```bash
bitcoin-cli -datadir="." getnewaddress
# bcrt1qllxahh4su69rszmyjr93y3t07h57nwny0j95ks (Carol)
```

Suponha que temos um UTXO de **49.49988759 BTC** (resultado do cenário anterior).

**b. Criar a transação bruta com múltiplos outputs**
Definimos um valor para cada destinatário, por exemplo:

- Kaká: **0.7 BTC**
- Carol: **1.2 BTC**

```bash
bitcoin-cli -datadir="." createrawtransaction   '[{"txid":"647c2b177ddeeb222e339e69a3237bdaca71aad881a6a81d74591c6a120934b4","vout":0}]' '{"bcrt1q7waheqekh39xlscz5ct28dqhhhh0u8v8nwh42n":0.7,
    "bcrt1qllxahh4su69rszmyjr93y3t07h57nwny0j95ks":1.2}'
# 0200000001b43409126a1c59741da8a681d8aa71cada7b23a3699e332e22ebde7d172b7c640000000000fdffffff02801d2c0400000000160014f3bb7c8336bc4a6fc302a616a3b417bdeefe1d87000e270700000000160014ffcddbdeb0e68a380b6490cb12456ff5e9e9ba6400000000
```

Esse comando cria o **hex bruto** com **dois outputs**.

**c. Completar com taxa e troco**
Como estamos enviando apenas 1.9 BTC do total, precisamos que o Core calcule a taxa e crie o endereço de troco para o restante.

```bash
bitcoin-cli -datadir="." fundrawtransaction "0200000001b43409126a1c59741da8a681d8aa71cada7b23a3699e332e22ebde7d172b7c640000000000fdffffff02801d2c0400000000160014f3bb7c8336bc4a6fc302a616a3b417bdeefe1d87000e270700000000160014ffcddbdeb0e68a380b6490cb12456ff5e9e9ba6400000000" \
'{"feeRate":0.00001000}'
{
  "hex": "0200000001b43409126a1c59741da8a681d8aa71cada7b23a3699e332e22ebde7d172b7c640000000000fdffffff03801d2c0400000000160014f3bb7c8336bc4a6fc302a616a3b417bdeefe1d876ba9b71b01000000160014a71ab94297573c130d6ea2f9aa25047903f57787000e270700000000160014ffcddbdeb0e68a380b6490cb12456ff5e9e9ba6400000000",
  "fee": 0.00000172,
  "changepos": 1
}
```

**d. Assinar e enviar**

```bash
bitcoin-cli -datadir="." signrawtransactionwithwallet "0200000001b43409126a1c59741da8a681d8aa71cada7b23a3699e332e22ebde7d172b7c640000000000fdffffff03801d2c0400000000160014f3bb7c8336bc4a6fc302a616a3b417bdeefe1d876ba9b71b01000000160014a71ab94297573c130d6ea2f9aa25047903f57787000e270700000000160014ffcddbdeb0e68a380b6490cb12456ff5e9e9ba6400000000"
{
  "hex": "02000000000101b43409126a1c59741da8a681d8aa71cada7b23a3699e332e22ebde7d172b7c640000000000fdffffff03801d2c0400000000160014f3bb7c8336bc4a6fc302a616a3b417bdeefe1d876ba9b71b01000000160014a71ab94297573c130d6ea2f9aa25047903f57787000e270700000000160014ffcddbdeb0e68a380b6490cb12456ff5e9e9ba6402473044022070655be3c7e287e70b81a4e928abd20d02fc5fc264f9111a52c0094c392c4dc802203920cb46a11bbe08d8dcc9de5b8412b5556a62cd6ead46ca0786d78d31ee6e63012103df6d57b8af03faf7ff2aeee55347c397ea08756403d88d5d2981e546529939e800000000",
  "complete": true
}
```

```bash
bitcoin-cli -datadir="." sendrawtransaction "02000000000101b43409126a1c59741da8a681d8aa71cada7b23a3699e332e22ebde7d172b7c640000000000fdffffff03801d2c0400000000160014f3bb7c8336bc4a6fc302a616a3b417bdeefe1d876ba9b71b01000000160014a71ab94297573c130d6ea2f9aa25047903f57787000e270700000000160014ffcddbdeb0e68a380b6490cb12456ff5e9e9ba6402473044022070655be3c7e287e70b81a4e928abd20d02fc5fc264f9111a52c0094c392c4dc802203920cb46a11bbe08d8dcc9de5b8412b5556a62cd6ead46ca0786d78d31ee6e63012103df6d57b8af03faf7ff2aeee55347c397ea08756403d88d5d2981e546529939e800000000"
# b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79
```

**e. Confirmar e inspecionar**
Minerar um bloco para confirmar:

```bash
bitcoin-cli -datadir="." generatetoaddress 1 bcrt1q9w437k3luux5crekejss56r8cysxhr4ypuha22
```

Liste os UTXOs:

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79",
    "vout": 0,
    "address": "bcrt1q7waheqekh39xlscz5ct28dqhhhh0u8v8nwh42n",
    "label": "",
    "scriptPubKey": "0014f3bb7c8336bc4a6fc302a616a3b417bdeefe1d87",
    "amount": 0.70000000,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/5]039c8a99f8d6008801b97a6ec5f0ca231e706ddb28edebd12666b0f16aef7a48f2)#duqx02j9",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
    "txid": "b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79",
    "vout": 1,
    "address": "bcrt1q5udtjs5h2u7pxrtw5tu65fgy0ypl2au8rkfg62",
    "scriptPubKey": "0014a71ab94297573c130d6ea2f9aa25047903f57787",
    "amount": 47.59988587,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/1/3]022a3cae7145dcfe74772d35b16fdb40e5fe0cf8fc3950eb5b9048a2b70d271e6f)#7uhj7gdg",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/1/*)#jtyys78l"
    ],
    "safe": true
  },
  {
    "txid": "b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79",
    "vout": 2,
    "address": "bcrt1qllxahh4su69rszmyjr93y3t07h57nwny0j95ks",
    "label": "",
    "scriptPubKey": "0014ffcddbdeb0e68a380b6490cb12456ff5e9e9ba64",
    "amount": 1.20000000,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/6]037994b04a5183d16e24f1a3a2a08bf1fcd5c528e5efcc3855065a6f3e0659ae0f)#ax5l0vfn",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
  ...
```

Você verá **três outputs** (além de outros que não nos interessante aqui):

1. **0.7 BTC** para Kaká
2. **1.2 BTC** para Carol
3. O **troco** (`47.59988587`) de volta para a sua carteira.

---

**Por que o batching economiza?**

Se você criasse duas transações separadas, uma de 0.7 BTC e outra de 1.2 BTC, pagaria taxa **duas vezes** e criaria dois cabeçalhos, duas assinaturas etc.

No batching, a maior parte do tamanho da transação está nos inputs; aumentar apenas os outputs tem custo marginal bem menor.

---

## **Consolidação de UTXOs**

**Consolidar** é juntar vários UTXOs pequenos em um único UTXO maior.
**Vantagens:** transações futuras com menos inputs (mais baratas) e carteira mais simples.
**Cuidado:** consolidação liga aqueles UTXOs entre si (impacto de privacidade). Evite misturar KYC/non-KYC e prefira fazer quando as taxas estão baixas.

Vamos a um passo-a-passo para consolidar UTXOs.

**a) Identificar UTXOs pequenos**

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79",
    "vout": 0,
    "address": "bcrt1q7waheqekh39xlscz5ct28dqhhhh0u8v8nwh42n",
    "label": "",
    "scriptPubKey": "0014f3bb7c8336bc4a6fc302a616a3b417bdeefe1d87",
    "amount": 0.70000000,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/5]039c8a99f8d6008801b97a6ec5f0ca231e706ddb28edebd12666b0f16aef7a48f2)#duqx02j9",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
    "txid": "b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79",
    "vout": 2,
    "address": "bcrt1qllxahh4su69rszmyjr93y3t07h57nwny0j95ks",
    "label": "",
    "scriptPubKey": "0014ffcddbdeb0e68a380b6490cb12456ff5e9e9ba64",
    "amount": 1.20000000,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/6]037994b04a5183d16e24f1a3a2a08bf1fcd5c528e5efcc3855065a6f3e0659ae0f)#ax5l0vfn",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
    "txid": "1417f599358ea49a63dd253a3b3701ce0fa28cdf006522e4a3c50c48fce12e8e",
    "vout": 0,
    "address": "bcrt1qkqp9xzkre29gl7kl7d3s264nstysw7fqjj5pqf",
    "label": "",
    "scriptPubKey": "0014b002530ac3ca8a8ffadff363056ab382c9077920",
    "amount": 0.50000000,
    "confirmations": 4,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/1]0238caef26a2025d89d4230bcc7e2d1dbdcc8ce51ce1c07cd4509a76495bba07d9)#8q3llhqf",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  ...
]

```

Suponha que escolhemos esses **três UTXOs** resultantes dos exemplos anteriores:

- A: `txid b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79`, `vout:0`, **0.70000000 BTC**
- B: `txid b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79`, `vout:2`, **1.20000000 BTC**
- C: `txid 1417f599358ea49a63dd253a3b3701ce0fa28cdf006522e4a3c50c48fce12e8e`, `vout:0`, **0.50000000 BTC**
    
    **Total = 2.40000000 BTC**
    

**b) Gerar um endereço seu para receber a consolidação**

```bash
bitcoin-cli -datadir="." getnewaddress
# bcrt1qnk9lxpt4ch7zkp9ncdr3awe0aa0e49kp5v6453
```

**Opção 1 — Com `fundrawtransaction` (sem troco via `subtractFeeFromOutputs`)**

Mais simples: você informa o **total** na saída e pede para a taxa ser **descontada do próprio output**, evitando troco.

**1. Criar o hex bruto com 3 inputs e 1 output (2.4 BTC)**

```bash
bitcoin-cli -datadir="." createrawtransaction \
 '[{"txid":"b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79","vout":0},{"txid":"b9554be708c5ea7414876a3757a65df19cd5ddf8c19365c8425c3f8ce8066d79","vout":2},{"txid":"1417f599358ea49a63dd253a3b3701ce0fa28cdf006522e4a3c50c48fce12e8e","vout":0}]' \
  '{"bcrt1qnk9lxpt4ch7zkp9ncdr3awe0aa0e49kp5v6453":2.4}'
# 0200000003796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90000000000fdffffff796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90200000000fdffffff8e2ee1fc480cc5a3e4226500df8ca20fce01373b3a25dd639aa48e3599f517140000000000fdffffff01001c4e0e000000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c100000000
```

**2. Completar: taxa e “sem troco”**

```bash
bitcoin-cli -datadir="." fundrawtransaction "0200000003796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90000000000fdffffff796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90200000000fdffffff8e2ee1fc480cc5a3e4226500df8ca20fce01373b3a25dd639aa48e3599f517140000000000fdffffff01001c4e0e000000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c100000000" \
  '{"add_inputs":false, "feeRate":0.00001000, "subtractFeeFromOutputs":[0]}'
#
{
  "hex": "0200000003796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90000000000fdffffff796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90200000000fdffffff8e2ee1fc480cc5a3e4226500df8ca20fce01373b3a25dd639aa48e3599f517140000000000fdffffff010b1b4e0e000000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c100000000",
  "fee": 0.00000245,
  "changepos": -1
}
```

**changepos** igual a -1 indica que não há troco.
**3. Assinar e enviar**

```bash
bitcoin-cli -datadir="." signrawtransactionwithwallet "0200000003796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90000000000fdffffff796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90200000000fdffffff8e2ee1fc480cc5a3e4226500df8ca20fce01373b3a25dd639aa48e3599f517140000000000fdffffff010b1b4e0e000000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c100000000"
{
  "hex": "02000000000103796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90000000000fdffffff796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90200000000fdffffff8e2ee1fc480cc5a3e4226500df8ca20fce01373b3a25dd639aa48e3599f517140000000000fdffffff010b1b4e0e000000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c10247304402203664d96a5f91c916e213e9a6adabda0c4a2031abe9db7e1a8f2f996f9fdbad91022070ea8353ce9281456776f5e723c48c1aa022a4adb35a207f9644c0338d95c6310121039c8a99f8d6008801b97a6ec5f0ca231e706ddb28edebd12666b0f16aef7a48f20247304402203c350e5bd7a9a69fde895df1ae95d6935383c7ac7554f53ac10437391d45d3fd02202fbfc490b365afe774bb4771650ec9bb81e813a6df547e523ed9bacf4fa1d6f50121037994b04a5183d16e24f1a3a2a08bf1fcd5c528e5efcc3855065a6f3e0659ae0f0247304402206e422304d7a85fb96a9624c532cabd2ae0354711554410b7360cff55df14a57e02202bdbd8fb1983d5d3f24f859f735c11b174bfea9a5b813e77e8a9734047620a7001210238caef26a2025d89d4230bcc7e2d1dbdcc8ce51ce1c07cd4509a76495bba07d900000000",
  "complete": true
}
```

```bash
bitcoin-cli -datadir="." sendrawtransaction "02000000000103796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90000000000fdffffff796d06e88c3f5c42c86593c1f8ddd59cf15da657376a871474eac508e74b55b90200000000fdffffff8e2ee1fc480cc5a3e4226500df8ca20fce01373b3a25dd639aa48e3599f517140000000000fdffffff010b1b4e0e000000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c10247304402203664d96a5f91c916e213e9a6adabda0c4a2031abe9db7e1a8f2f996f9fdbad91022070ea8353ce9281456776f5e723c48c1aa022a4adb35a207f9644c0338d95c6310121039c8a99f8d6008801b97a6ec5f0ca231e706ddb28edebd12666b0f16aef7a48f20247304402203c350e5bd7a9a69fde895df1ae95d6935383c7ac7554f53ac10437391d45d3fd02202fbfc490b365afe774bb4771650ec9bb81e813a6df547e523ed9bacf4fa1d6f50121037994b04a5183d16e24f1a3a2a08bf1fcd5c528e5efcc3855065a6f3e0659ae0f0247304402206e422304d7a85fb96a9624c532cabd2ae0354711554410b7360cff55df14a57e02202bdbd8fb1983d5d3f24f859f735c11b174bfea9a5b813e77e8a9734047620a7001210238caef26a2025d89d4230bcc7e2d1dbdcc8ce51ce1c07cd4509a76495bba07d900000000"
# 61db943161c00e8cf797cb8d4e3d896e88f52c8e39490e735d70abaa6a74ce73
```

**4. Confirmar e verificar o novo UTXO único**

```bash
bitcoin-cli -datadir="." generatetoaddress 1 bcrt1q9w437k3luux5crekejss56r8cysxhr4ypuha22
```

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "61db943161c00e8cf797cb8d4e3d896e88f52c8e39490e735d70abaa6a74ce73",
    "vout": 0,
    "address": "bcrt1qnk9lxpt4ch7zkp9ncdr3awe0aa0e49kp5v6453",
    "label": "",
    "scriptPubKey": "00149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c1",
    "amount": 2.39999755,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/7]02b1f28fe1718cb0d19d63ca8f00f1da97a9ca6a2f2fe58ea38dc8764271fd9bb9)#v6xev5z7",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
  ...
```

Perceba que agora temos um UTXO com `2.39999755` BTC (2.4 BTC consolidados - taxa).

**Opção 2 — Total controle (sem `fundrawtransaction`)**
Podemos definir a taxa e já criar a saída como **soma(inputs) − taxa** (sem troco). Nesse cenário, vamos consolidar 3 UTXOs que receberam as recompensas de mineração em exemplos anteriores.

**1. Calcular o valor de saída**

```bash
VALOR=150-(0.0001)
VALOR=149.9999
```

**2. Criar o raw sem espaço para troco**

```bash
bitcoin-cli -datadir="." createrawtransaction \
'[{"txid":"347775cd427f4e7b88906ce5ca8c11570822063c76280cc2e63879e6ed956323","vout":0},{"txid":"cebd41bfe9964f604f7247ee0c27a1bec23a55880c5be1c91b3889f4e2277808","vout":0},{"txid":"1a2c538fb7b78a8898ddc82b79dd593922d402153c7ff97491e539a91b57fde7","vout":0}]' \
  '{"bcrt1qnk9lxpt4ch7zkp9ncdr3awe0aa0e49kp5v6453":149.9999}'
# 0200000003236395ede67938e6c20c28763c06220857118ccae56c90887b4e7f42cd7577340000000000fdffffff087827e2f489381bc9e15b0c88553ac2bea1270cee47724f604f96e9bf41bdce0000000000fdffffffe7fd571ba939e59174f97f3c1502d4223959dd792bc8dd98888ab7b78f532c1a0000000000fdffffff01f0ae117e030000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c100000000
```

**3. Assinar, enviar e confirmar**

```bash
bitcoin-cli -datadir="." signrawtransactionwithwallet "0200000003236395ede67938e6c20c28763c06220857118ccae56c90887b4e7f42cd7577340000000000fdffffff087827e2f489381bc9e15b0c88553ac2bea1270cee47724f604f96e9bf41bdce0000000000fdffffffe7fd571ba939e59174f97f3c1502d4223959dd792bc8dd98888ab7b78f532c1a0000000000fdffffff01f0ae117e030000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c100000000"
{
  "hex": "02000000000103236395ede67938e6c20c28763c06220857118ccae56c90887b4e7f42cd7577340000000000fdffffff087827e2f489381bc9e15b0c88553ac2bea1270cee47724f604f96e9bf41bdce0000000000fdffffffe7fd571ba939e59174f97f3c1502d4223959dd792bc8dd98888ab7b78f532c1a0000000000fdffffff01f0ae117e030000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c10247304402204aa694a69c037ab059f75affd9db353cc2d54438c2d22d0a69f5996ae4e3b4d302205ea15356e49c0ae44ba9e110e3e0ff1f83b76943ace7d62171e6fa7e70154b190121024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba70247304402202ceef57fb7564c5108dfcadb719b6dfc34747ec30b13fe2c306bb76ee73902c30220349cbc0e130f446bc0313afe0502850e792d3e0edc08d198f89091b04607d4b90121024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba70247304402202c56c84d7bc2bdac40cfb9d3baea64e23193fb9145cd1da9737795c4553991e002205d7ec73eff147ac9903057abe1ff78fe54cdcc63f8270a52810dd3c44d86ab390121024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba700000000",
  "complete": true
}
```

```bash
bitcoin-cli -datadir="." sendrawtransaction "02000000000103236395ede67938e6c20c28763c06220857118ccae56c90887b4e7f42cd7577340000000000fdffffff087827e2f489381bc9e15b0c88553ac2bea1270cee47724f604f96e9bf41bdce0000000000fdffffffe7fd571ba939e59174f97f3c1502d4223959dd792bc8dd98888ab7b78f532c1a0000000000fdffffff01f0ae117e030000001600149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c10247304402204aa694a69c037ab059f75affd9db353cc2d54438c2d22d0a69f5996ae4e3b4d302205ea15356e49c0ae44ba9e110e3e0ff1f83b76943ace7d62171e6fa7e70154b190121024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba70247304402202ceef57fb7564c5108dfcadb719b6dfc34747ec30b13fe2c306bb76ee73902c30220349cbc0e130f446bc0313afe0502850e792d3e0edc08d198f89091b04607d4b90121024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba70247304402202c56c84d7bc2bdac40cfb9d3baea64e23193fb9145cd1da9737795c4553991e002205d7ec73eff147ac9903057abe1ff78fe54cdcc63f8270a52810dd3c44d86ab390121024bdbdf6b6c264db5a9a9f2ffb6f964f228c722c419ffd7ae26a7b850bfce6ba700000000"
# 2c668e312971983fc465d8c79f5813732f288331cda23dd86fd73fc5339e2984
```

```bash
bitcoin-cli -datadir="." generatetoaddress 1 bcrt1q9w437k3luux5crekejss56r8cysxhr4ypuha22
```

Podemos listar os UTXOs para conferir a consolidação.

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "2c668e312971983fc465d8c79f5813732f288331cda23dd86fd73fc5339e2984",
    "vout": 0,
    "address": "bcrt1qnk9lxpt4ch7zkp9ncdr3awe0aa0e49kp5v6453",
    "label": "",
    "scriptPubKey": "00149d8bf30575c5fc2b04b3c3471ebb2fef5f9a96c1",
    "amount": 149.99990000,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([2f5cd395/84h/1h/0h/0/7]02b1f28fe1718cb0d19d63ca8f00f1da97a9ca6a2f2fe58ea38dc8764271fd9bb9)#v6xev5z7",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4WtpQ21uY5dQCNe2wu8GdTcB7zLmVcdvJPFjQ8c4FNq1wR4zsr1qc1XgZqVAmd6m6uHrSJhrfTHsy5cnw5yyQaWG49guuByL/84h/1h/0h/0/*)#rlp9dth8"
    ],
    "safe": true
  },
  {
  ...
```

Veja que agora temos um UTXO com `149.99990000` BTC.

---

Construir transações manualmente no Bitcoin Core é mais do que um exercício de curiosidade: é um **laboratório prático para entender o protocolo**. Ao longo deste artigo, vimos cenários que cobrem desde o envio básico com troco automático até estratégias mais avançadas como **batching** e **consolidação de UTXOs**.

Esses exemplos deixam claro que:

- **Cada satoshi importa** – negligenciar o cálculo de taxas ou o endereço de troco pode transformar uma simples distração em uma taxa gigantesca paga ao minerador.
- **Controle é poder** – escolher manualmente os inputs, definir a taxa e decidir quando consolidar UTXOs permite otimizar custos e simplificar a carteira.
- **Privacidade exige planejamento** – consolidar ou misturar UTXOs pode revelar vínculos entre endereços. Em ambientes de produção, combine estas técnicas com boas práticas de privacidade.

Praticar esses comandos em `regtest` ou `signet` fornece a segurança de um ambiente controlado, mas o aprendizado é diretamente aplicável à **mainnet**. Antes de enviar transações reais, revise sempre:

1. **Soma dos outputs vs. inputs** – garanta que a diferença seja a taxa pretendida.
2. **Destino do troco** – defina um endereço sob seu controle ou use `subtractfeefromamount` se quiser evitá-lo.
3. **Taxa de rede** – ajuste de acordo com o mempool para equilibrar custo e velocidade de confirmação.

Dominar essas práticas dá a você não apenas confiança para operar na rede, mas também **uma compreensão profunda do modelo UTXO** que sustenta o Bitcoin.

Nos próximos artigos, exploraremos outras questões avançadas relacionadas à transações, como **PSBTs (Partially Signed Bitcoin Transactions)**, **multisig** e **timelocks**.  ****
