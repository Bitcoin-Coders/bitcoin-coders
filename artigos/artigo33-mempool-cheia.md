# O que acontece quando a mempool do Bitcoin fica cheia?

Quando uma transação Bitcoin é transmitida para um node, ela normalmente entra na **mempool**, onde aguarda até ser incluída em um bloco.

Mas a mempool não pode crescer indefinidamente. Cada node define quanto de memória está disposto a utilizar para armazenar transações não confirmadas.

O que acontece quando esse espaço acaba?

Para observar esse comportamento, criamos um laboratório em `regtest`, limitamos a mempool a apenas **5 MB** e começamos a preenchê-la com transações de diferentes taxas.

O objetivo era observar três coisas:

```
1. quando a mempool atingiria o limite;
2. quais transações seriam removidas;
3. como o mempoolminfee reagiria.
```

### Iniciando o node

Criamos um diretório separado para o experimento:

```bash
mkdir -p ~/mempool-full-test
cd ~/mempool-full-test
```

Como já havia outras instâncias do Bitcoin Core rodando na máquina, iniciamos esse node isolado e sem conexões P2P:

```bash
bitcoind \
  -regtest \
  -datadir="$PWD" \
  -server \
  -daemon \
  -listen=0 \
  -fallbackfee=0.00001 \
  -maxmempool=5 \
  -rpcport=29491
```

O parâmetro importante para o experimento é:

```bash
-maxmempool=5
```

Com isso, limitamos o uso da mempool a aproximadamente **5 MB**.

Podemos conferir o estado inicial com:

```bash
bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  getmempoolinfo
```

Obtivemos:

```bash
{
  "loaded": true,
  "size": 0,
  "bytes": 0,
  "usage": 0,
  "total_fee": 0.00000000,
  "maxmempool": 5000000,
  "mempoolminfee": 0.00001000,
  "minrelaytxfee": 0.00001000,
  "incrementalrelayfee": 0.00001000,
  "unbroadcastcount": 0,
  "fullrbf": true
}
```

Nesse momento:

```bash
maxmempool       = 5.000.000 bytes
mempoolminfee    = 1 sat/vB
incrementalrelay = 1 sat/vB
```

A mempool estava completamente vazia.

### Criando saldo para o experimento

Criamos uma carteira:

```bash
bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  createwallet teste
```

Depois geramos um endereço:

```bash
ADDR=$(bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  -rpcwallet=teste \
  getnewaddress)
```

E mineramos 110 blocos:

```bash
bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  -rpcwallet=teste \
  generatetoaddress 110 "$ADDR"
```

Após isso, a carteira mostrava:

```bash
{
  "mine": {
    "trusted": 500.00000000,
    "untrusted_pending": 0.00000000,
    "immature": 5000.00000000
  }
}
```

Já tínhamos saldo maduro suficiente para preparar o laboratório.

### Criando 1.500 UTXOs independentes

Queríamos gerar muitas transações sem depender umas das outras.

Se criássemos uma longa cadeia em que cada transação gastasse uma saída ainda não confirmada da anterior, outros limites da mempool poderiam interferir no experimento.

Por isso, primeiro criamos **1.500 UTXOs confirmados e independentes de 0,002 BTC**.

Geramos 1.500 novos endereços:

```python
import subprocess
import json

base = [
    "bitcoin-cli",
    "-regtest",
    "-datadir=/home/penna/mempool-full-test",
    "-rpcport=29491",
    "-rpcwallet=teste",
]

outputs = {}

for i in range(1500):
    addr = subprocess.check_output(
        base + ["getnewaddress"],
        text=True
    ).strip()

    outputs[addr] = 0.002

with open("/tmp/mempool_outputs.json", "w") as f:
    json.dump(outputs, f)
```

Depois usamos `sendmany` para criar uma transação contendo os 1.500 outputs:

```bash
TXID=$(bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  -rpcwallet=teste \
  sendmany "" "$(cat /tmp/mempool_outputs.json)")
```

A transação criada foi:

```bash
2064114bfdab5698ae4a0bb8c39349b19267a90e067777d7b45be8b4d376f91b
```

Confirmamos essa transação minerando mais um bloco:

```bash
bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  -rpcwallet=teste \
  generatetoaddress 1 "$ADDR"
```

Por fim, verificamos quantos UTXOs de exatamente `0,002 BTC` estavam disponíveis:

```bash
bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  -rpcwallet=teste \
  listunspent 1 \
  | jq '[.[] | select(.amount == 0.00200000)] | length'
```

Resultado:

```bash
1500
```

Tínhamos agora 1.500 entradas independentes prontas para alimentar a mempool.

### Construindo transações grandes

O próximo passo era encher a mempool sem precisar criar dezenas de milhares de transações.

Para isso, cada UTXO de `0,002 BTC` foi gasto em uma transação contendo:

```
1 input
120 outputs
```

Essas transações ficaram com aproximadamente:

```
3799 vB
```

Cada uma delas era independente das demais.

Para controlar a taxa paga, construímos as transações manualmente utilizando:

```
createrawtransaction
signrawtransactionwithwallet
decoderawtransaction
sendrawtransaction
```

Primeiro criávamos uma versão provisória da transação:

```bash
raw = rpc([
    "createrawtransaction",
    json.dumps(inputs),
    json.dumps(outputs)
])
```

Depois assinávamos:

```bash
signed = rpc_json(
    ["signrawtransactionwithwallet", raw],
    wallet=True
)
```

E decodificávamos para descobrir seu `vsize`:

```bash
decoded = rpc_json([
    "decoderawtransaction",
    signed["hex"]
])

vsize = decoded["vsize"]
```

Conhecendo o tamanho, podíamos escolher exatamente a fee desejada.

Por exemplo, para uma transação de 3799 vB:

```
1 sat/vB → 3.799 sats
2 sat/vB → 7.598 sats
3 sat/vB → 11.397 sats
5 sat/vB → 18.995 sats
```

O valor restante do UTXO era dividido entre os 120 outputs.

Por fim, transmitíamos a transação:

```bash
txid = rpc([
    "sendrawtransaction",
    signed["hex"]
])
```

Repetimos esse processo em diferentes faixas de feerate.

### Primeira etapa: enchendo a mempool

Começamos enviando:

```
300 transações × 1 sat/vB
300 transações × 2 sat/vB
203 transações × 3 sat/vB
```

Total:

```
803 transações
```

Depois consultamos novamente:

```bash
bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  getmempoolinfo
```

O resultado foi:

```bash
size: 803
bytes: 3.050.594
usage: 4.705.920
maxmempool: 5.000.000
mempoolminfee: 1 sat/vB
```

A mempool estava quase cheia.

### `bytes` e `usage` não são a mesma coisa

Nesse ponto aparece um detalhe importante.

Embora tivéssemos:

```
bytes = 3,051 MB
```

o uso de memória era:

```
usage = 4,706 MB
```

`bytes` representa o tamanho virtual das transações armazenadas.

Já `usage` representa o uso dinâmico de memória necessário para manter essas transações e suas estruturas associadas dentro da mempool.

É esse valor que deve ser comparado com:

```
maxmempool = 5 MB
```

Nossa mempool, portanto, já estava utilizando cerca de:

```
4,706 / 5,000 ≈ 94%
```

da memória permitida.

Ainda havia algum espaço.

### Adicionando transações mais caras

Em seguida começamos a transmitir outras **300 transações**, agora pagando:

```
5 sat/vB
```

Acompanhamos o estado da mempool a cada 25 transações.

O início foi:

```bash
INÍCIO:
txs=803
bytes=3.051 MB
usage=4.706 MB
minfee=1 sat/vB
```

Após 25 novas transações:

```bash
TX 25:
txs=828
bytes=3.146 MB
usage=4.852 MB
minfee=1 sat/vB
```

Após 50:

```bash
TX 50:
txs=853
bytes=3.241 MB
usage=4.998 MB
minfee=1 sat/vB
```

Nesse momento praticamente não havia mais memória disponível.

Mas continuamos enviando transações de 5 sat/vB.

### A mempool para de crescer

Ao chegar à transação 75, observamos uma mudança:

```bash
TX 75:
txs=853
bytes=3.241 MB
usage=4.998 MB
minfee=2 sat/vB
```

Continuamos:

```bash
TX 100:
txs=853
bytes=3.241 MB
usage=4.998 MB
minfee=2 sat/vB

TX 150:
txs=853
bytes=3.241 MB
usage=4.998 MB
minfee=2 sat/vB

TX 200:
txs=853
bytes=3.241 MB
usage=4.998 MB
minfee=2 sat/vB

TX 250:
txs=853
bytes=3.241 MB
usage=4.998 MB
minfee=2 sat/vB

TX 300:
txs=853
bytes=3.241 MB
usage=4.998 MB
minfee=2 sat/vB
```

As novas transações continuavam sendo aceitas.

Mas:

```
size
bytes
usage
```

praticamente não aumentavam mais. Alguma coisa precisava estar saindo.

### Descobrindo quais transações sobreviveram

Para verificar a composição da mempool, exportamos todas as entradas:

```bash
bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  getrawmempool true > /tmp/mempool_depois.json
```

Depois calculamos a feerate de cada uma:

```bash
jq -r '
  to_entries[]
  | ((.value.fees.base * 100000000) / .value.vsize | round)
' /tmp/mempool_depois.json \
| sort -n \
| uniq -c
```

Antes das transações de 5 sat/vB, tínhamos:

```
300 × 1 sat/vB
300 × 2 sat/vB
203 × 3 sat/vB
```

Depois de transmitir todas as 300 transações de 5 sat/vB, a distribuição era:

```
 50 × 1 sat/vB
300 × 2 sat/vB
203 × 3 sat/vB
300 × 5 sat/vB
```

Portanto:

```
250 transações de 1 sat/vB desapareceram
```

enquanto:

```
300 transações de 5 sat/vB entraram
```

As primeiras 50 transações novas ainda conseguiram ocupar o espaço livre.

Depois disso, para cada nova transação mais cara que entrava, o Bitcoin Core precisava liberar espaço removendo transações menos competitivas.

No final ainda havia:

```
853 transações
```

exatamente o mesmo número observado quando a mempool chegou ao limite.

### O `mempoolminfee` sobe

Depois das remoções, consultamos novamente:

```bash
bitcoin-cli \
  -regtest \
  -datadir="$PWD" \
  -rpcport=29491 \
  getmempoolinfo
```

O resultado relevante era:

```bash
{
  "size": 853,
  "usage": 4997920,
  "maxmempool": 5000000,
  "mempoolminfee": 0.00002000,
  "incrementalrelayfee": 0.00001000
}
```

Convertendo:

```bash
mempoolminfee = 2 sat/vB
```

No início do experimento esse valor era:

```bash
1 sat/vB
```

Depois que o Core precisou começar a remover transações de 1 sat/vB, o piso dinâmico subiu.

No nosso laboratório:

```
feerate das transações removidas = 1 sat/vB
incrementalrelayfee              = 1 sat/vB
```

O novo piso passou para:

```
2 sat/vB
```

### Mas ainda havia transações de 1 sat/vB

Aqui apareceu uma situação curiosa.

Apesar de:

```
mempoolminfee = 2 sat/vB
```

a mempool ainda continha:

```
50 transações de 1 sat/vB
```

Confirmamos isso olhando diretamente para algumas das transações restantes.

Por exemplo:

```
vsize: 3799
fee:   3799 sats
```

Logo:

```
feerate = 1 sat/vB
```

O `mempoolminfee` ter subido para 2 sat/vB, portanto, não significava que todas as transações antigas abaixo desse piso haviam desaparecido imediatamente.

Restava então uma pergunta:

> Uma nova transação de 1 sat/vB ainda conseguiria entrar?
> 

### Tentando enviar uma nova transação de 1 sat/vB

Pegamos outro UTXO confirmado e construímos uma transação pequena.

Ela tinha:

```
vsize: 110 vB
fee:   110 sats
```

Portanto:

```
110 sats / 110 vB = 1 sat/vB
```

Tentamos transmiti-la com:

```bash
sendrawtransaction
```

O Bitcoin Core respondeu:

```bash
error code: -26
error message:
mempool min fee not met, 110 < 220
```

A mensagem mostra exatamente o que estava acontecendo.

Nossa transação oferecia:

```
110 sats
```

Mas, com o `mempoolminfee` em 2 sat/vB, uma transação de 110 vB precisava pagar pelo menos:

```
110 × 2 = 220 sats
```

A nova transação de 1 sat/vB foi rejeitada.

Mesmo enquanto ainda existiam 50 transações antigas pagando exatamente essa mesma feerate dentro da mempool.

### O que aconteceu?

O experimento pode ser resumido assim:

```
mempool vazia
mempoolminfee = 1 sat/vB
        |
        v
entram txs de 1, 2 e 3 sat/vB
        |
        v
usage = 4,706 MB
        |
        v
começam a entrar txs de 5 sat/vB
        |
        v
usage chega a 4,998 MB
        |
        v
não há mais espaço
        |
        v
Core remove txs de menor feerate
        |
        v
250 txs de 1 sat/vB são removidas
        |
        v
mempoolminfee sobe para 2 sat/vB
        |
        v
novas txs de 1 sat/vB passam a ser rejeitadas
```

### Conclusão

Uma mempool cheia não funciona simplesmente como uma fila que fecha quando não há mais espaço.

No nosso experimento, novas transações com taxas mais altas continuaram entrando mesmo depois de a mempool atingir praticamente os 5 MB configurados.

Para isso, o Bitcoin Core passou a remover transações menos competitivas.

Começamos com:

```
300 × 1 sat/vB
300 × 2 sat/vB
203 × 3 sat/vB
```

e terminamos com:

```
 50 × 1 sat/vB
300 × 2 sat/vB
203 × 3 sat/vB
300 × 5 sat/vB
```

Ao mesmo tempo:

```
mempoolminfee
1 sat/vB → 2 sat/vB
```

O teste final mostrou ainda um comportamento menos intuitivo: havia transações antigas de 1 sat/vB dentro da mempool, mas uma nova transação pagando a mesma taxa já não conseguia entrar.

Quando a memória disponível se torna escassa, portanto, as transações passam a competir não apenas por espaço nos próximos blocos, mas também pelo próprio espaço dentro da mempool do node.

por: Rafael Penna
