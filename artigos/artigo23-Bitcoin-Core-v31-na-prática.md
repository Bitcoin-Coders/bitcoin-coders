# Bitcoin Core v31 na prática: o que mudou (com bitcoin-cli)

A cada nova versão do Bitcoin Core, aparecem dezenas de mudanças. Algumas são realmente **visíveis** no dia a dia de quem usa o node.

Neste artigo, a ideia é simples:

👉 pegar algumas novidades da versão 31

👉 testar na prática com `bitcoin-cli` 

👉 comparar com a v30

👉 entender o que realmente mudou

---

### Preparação

Vou assumir que já temos duas versões rodando na signet:

- v30 (ex: `v30/bin/bitcoin-30.2/`)
- v31 (ex: `v31/bin/bitcoin-31.0/`)

Pra facilitar, crie aliases no terminal:

```bash
alias bitcoin-cli-30="v30/bin/bitcoin-30.2/bin/bitcoin-cli -datadir=$(pwd)/v30/data"
alias bitcoin-cli-31="v31/bin/bitcoin-31.0/bin/bitcoin-cli -datadir=$(pwd)/v31/data"
```

Agora, sempre que você chamar `bitcoin-cli-30`, estará interagindo com o node da versão 30, e ao usar `bitcoin-cli-31`, estará se comunicando com o node da versão 31.

Se quiser tornar permanente:

```bash
echo 'alias bitcoin-cli-30="v30/bin/bitcoin-30.2/bin/bitcoin-cli -datadir=$(pwd)/v30/data"' >> ~/.bashrc
echo 'alias bitcoin-cli-31="v31/bin/bitcoin-31.0/bin/bitcoin-cli -datadir=$(pwd)/v31/data"' >> ~/.bashrc
source ~/.bashrc
```

Teste:

```bash
bitcoin-cli-30 getblockchaininfo
bitcoin-cli-31 getblockchaininfo
```

Considero também que ambas versões já estão com uma wallet carregada.

### 🧪 Lab 1 — A mempool deixou de ser uma lista

Na v30, você enxerga a mempool como um conjunto de transações.

Na v31, aparece algo novo. Surge um novo RPC: `getmempoolcluster`.

Esse método permite consultar como uma transação está inserida dentro de um **cluster de transações relacionadas**, ou seja, um grupo de transações conectadas por dependência (pai, filho, etc.).

Tente rodar:

```bash
bitcoin-cli-31 getmempoolcluster "<txid>”
```

**obs:** <txid> precisa ser de uma transação que está na mempool

Exemplo:

```bash
bitcoin-cli-31 getmempoolcluster 1f73a5a24cb1c595474102eb70b1c46981ccb61bcb8db9d57269fffef906909e
{
  "clusterweight": 13408,
  "txcount": 24,
  "chunks": [
    {
      "chunkfee": 0.00000126,
      "chunkweight": 5008,
      "txs": [
        "1e01400dbb670e77ef5d29185b85a13cd5fb01f8da545d9a3c9f377f09c5a8c1",
        "37bbeb5623385904960a252f66ac1be0b3cb9265a026ec8dd9a89321d646f0e1",
        ...
      ]
    },
    ...
  ]
}
```

Agora compare com a v30:

```
bitcoin-cli-30 getmempoolcluster"<txid>"
```

Exemplo:

```bash
bitcoin-cli-30 getmempoolcluster 1f73a5a24cb1c595474102eb70b1c46981ccb61bcb8db9d57269fffef906909e
error code: -32601
error message:
Method not found

```

Resultado:

- v31 → funciona
- v30 → `Method not found`

Esse comando revela algo importante: o node agora organiza a mempool em **clusters de transações relacionadas**.

Ou seja:

> transações não são mais tratadas isoladamente
> 

### 🧪 Lab 2 — A mempool agora revela “chunks”

No Lab 1 vimos que a mempool passou a ser organizada em clusters.

Agora aparece um detalhe novo dentro dessa estrutura.

O RPC `getmempoolentry`, que já existia, ganhou novos campos na v31:

- `chunkweight`
- `fees.chunk`

Esses campos mostram como a transação está inserida dentro de um **chunk**, ou seja, uma unidade econômica dentro do cluster.

---

Para reproduzir, vamos criar um cenário simples de dependência.

Primeiro, crie uma transação (pai):

```bash
ADDR_PARENT=$(bitcoin-cli-31 getnewaddress "lab-entry-parent" bech32)

TXID_PARENT=$(bitcoin-cli-31 sendtoaddress "$ADDR_PARENT" 0.001)

echo $TXID_PARENT
```

---

Agora crie uma segunda transação (filha), gastando o troco da anterior:

```bash
ADDR_CHILD=$(bitcoin-cli-31 getnewaddress "lab-entry-child" bech32)

TXID_CHILD=$(bitcoin-cli-31 sendtoaddress "$ADDR_CHILD" 0.0009)

echo $TXID_CHILD
```

Depois que ambas estiverem na mempool, rode:

```bash
bitcoin-cli-31 getmempoolentry "$TXID_PARENT"
```

Exemplo (v31):

```bash
{
  "vsize": 141,
  "weight": 561,
  "time": 1777922760,
  "height": 302969,
  "descendantcount": 1,
  "descendantsize": 141,
  "ancestorcount": 1,
  "ancestorsize": 141,
  "wtxid": "dbd629f454ac8281bf9546296b341f256dba3502aa219053eb4ee4801724b1d5",
  "chunkweight": 561,
  "fees": {
    "base": 0.00000141,
    "modified": 0.00000141,
    "ancestor": 0.00000141,
    "descendant": 0.00000141,
    "chunk": 0.00000141
  },
  "depends": [
  ],
  "spentby": [
  ],
  "bip125-replaceable": true,
  "unbroadcast": false
}
```

Agora compare com a v30:

```bash
bitcoin-cli-30 getmempoolentry "$TXID_PARENT"
```

Exemplo (v30):

```bash
{
  "vsize": 141,
  "weight": 561,
  "time": 1777922767,
  "height": 302969,
  "descendantcount": 1,
  "descendantsize": 141,
  "ancestorcount": 1,
  "ancestorsize": 141,
  "wtxid": "dbd629f454ac8281bf9546296b341f256dba3502aa219053eb4ee4801724b1d5",
  "fees": {
    "base": 0.00000141,
    "modified": 0.00000141,
    "ancestor": 0.00000141,
    "descendant": 0.00000141
  },
  "depends": [
  ],
  "spentby": [
  ],
  "bip125-replaceable": true,
  "unbroadcast": false
}
```

---

**O que mudou**

Na v30, você vê:

- fee base
- fee com ancestors
- fee com descendants

Na v31, aparecem dois novos elementos:

👉 `fees.chunk`

👉 `chunkweight`

- `fees.chunk` representa o valor econômico do conjunto considerado
- `chunkweight` representa o tamanho (peso) desse conjunto

Isso representa a **unidade econômica considerada pelo node** ao avaliar inclusão no bloco.

---

- `ancestor` → soma de dependências anteriores
- `descendant` → soma incluindo filhos
- `chunk` → grupo econômico relevante dentro do cluster
- `chunkweight` → tamanho desse grupo

Ou seja:

> o node não está mais apenas rastreando dependências, ele está avaliando combinações economicamente viáveis
> 

### 🧪 Lab 3 — O bloco agora revela a coinbase diretamente

No Bitcoin, todo bloco começa com uma transação especial: a **coinbase**, que cria novos bitcoins e paga o minerador.

Até a versão 30, para analisar essa transação, você precisava primeiro obter o bloco e depois buscar a transação separadamente.

Na v31, isso muda.

O RPC `getblock` passou a incluir diretamente um novo campo:

👉 `coinbase_tx`

---

Para testar, pegue o hash do bloco mais recente:

```bash
BLOCKHASH=$(bitcoin-cli-31 getbestblockhash)

echo $BLOCKHASH
0000000b635be4da4ea6b2b5efa00350c6b939d0d89350e8b06d15f0f22e361d
```

---

Agora, consulte o bloco na v31:

```bash
bitcoin-cli-31 getblock "$BLOCKHASH" 1 | jq '.coinbase_tx'
{
  "version": 2,
  "locktime": 302969,
  "sequence": 4294967294,
  "coinbase": "037a9f040a2f7369676e65743a332f",
  "witness": "0000000000000000000000000000000000000000000000000000000000000000"
}
```

---

Agora compare com a v30:

```bash
bitcoin-cli-30 getblock "$BLOCKHASH" 1 | jq '.coinbase_tx'
null
```

---

**O que mudou**

Na v30, o `getblock` não expõe diretamente a coinbase.

Na v31, o bloco já traz essa informação pronta.

---

👉 antes: você precisava fazer múltiplas consultas

👉 agora: o node já entrega a informação consolidada

Isso torna mais simples:

- analisar recompensas de bloco
- entender a estrutura interna de um bloco
- construir ferramentas sobre o node

---

> o node passou a expor mais diretamente a estrutura do bloco, reduzindo o trabalho necessário para analisá-lo
> 

### 🧪 Lab 4 — Descobrindo quem está gastando um output

No Bitcoin, cada transação consome outputs anteriores (UTXOs).

Uma pergunta comum é:

> “quem está gastando esse output?”
> 

O RPC `gettxspendingprevout` já existia na v30, mas na v31 ele ficou mais completo. Agora ele aceita opções adicionais e pode retornar não apenas o `spendingtxid`, mas também a transação completa que está gastando aquele output.

---

Para reproduzir, primeiro escolha um UTXO confirmado da sua wallet:

```bash
bitcoin-cli-31 listunspent 1 9999999
```

Exemplo:

```bash
[
  {
    "txid": "2fbdee19456bc383e0cbf4729c351d37da3575c19b52211efa0aa4b83ab79351",
    "vout": 1,
    "amount": 0.00100000,
    "confirmations": 2,
    "spendable": true
  }
]
```

Agora salve os dados do UTXO em variáveis:

```bash
UTXO_TXID="2fbdee19456bc383e0cbf4729c351d37da3575c19b52211efa0aa4b83ab79351"
UTXO_VOUT=1
UTXO_AMOUNT=0.00100000
```

Vamos criar uma transação pai gastando esse UTXO:

```bash
ADDR_PARENT=$(bitcoin-cli-31 getnewaddress "lab-prevout-parent" bech32)

RAW_PARENT=$(bitcoin-cli-31 createrawtransaction \
'[{"txid":"'"$UTXO_TXID"'","vout":'"$UTXO_VOUT"'}]' \
'{"'"$ADDR_PARENT"'":0.00098000}')

SIGNED_PARENT=$(bitcoin-cli-31 signrawtransactionwithwallet "$RAW_PARENT" | jq -r '.hex')

TXID_PARENT=$(bitcoin-cli-31 sendrawtransaction "$SIGNED_PARENT")

echo $TXID_PARENT
```

Resultado:

```bash
a1d6286ea7bd2ccfe65a410a4715c304469de9ac042db7af2b647585dcfe55e4
```

Agora criamos uma transação filha gastando exatamente o `vout 0` da transação pai:

```bash
ADDR_CHILD=$(bitcoin-cli-31 getnewaddress "lab-prevout-child" bech32)

RAW_CHILD=$(bitcoin-cli-31 createrawtransaction \
'[{"txid":"'"$TXID_PARENT"'","vout":0}]' \
'{"'"$ADDR_CHILD"'":0.00096000}')
```

Como a transação pai ainda está na mempool, precisamos informar explicitamente os dados do output que será gasto:

```bash
PARENT_SCRIPT=$(bitcoin-cli-31 decoderawtransaction "$SIGNED_PARENT" | jq -r '.vout[0].scriptPubKey.hex')

PARENT_AMOUNT=$(bitcoin-cli-31 decoderawtransaction "$SIGNED_PARENT" | jq -r '.vout[0].value')
```

Agora assinamos e enviamos a filha:

```bash
SIGNED_CHILD=$(bitcoin-cli-31 signrawtransactionwithwallet "$RAW_CHILD" \
'[{"txid":"'"$TXID_PARENT"'","vout":0,"scriptPubKey":"'"$PARENT_SCRIPT"'","amount":'"$PARENT_AMOUNT"'}]' \
| jq -r '.hex')

TXID_CHILD=$(bitcoin-cli-31 sendrawtransaction "$SIGNED_CHILD")

echo $TXID_CHILD
```

Resultado:

```
099f522bf8abf3d3309038c389850ec725b36751310634e35309c1f81c811f9e
```

Agora vem a novidade da v31. Podemos perguntar ao node quem está gastando o output `vout 0` da transação pai e pedir que ele retorne também a transação completa:

```bash
bitcoin-cli-31 -named gettxspendingprevout \
outputs='[{"txid":"'"$TXID_PARENT"'","vout":0}]' \
return_spending_tx=true | jq
```

Resultado:

```bash
[
  {
    "txid": "a1d6286ea7bd2ccfe65a410a4715c304469de9ac042db7af2b647585dcfe55e4",
    "vout": 0,
    "spendingtxid": "099f522bf8abf3d3309038c389850ec725b36751310634e35309c1f81c811f9e",
    "spendingtx": "02000000000101e455fedc8575642bafb72d04ace99d4604c315470a415ae6cf2cbda76e28d6a10000000000fdffffff0100770100000000001600147ab64287ca1595b989dfaf8074a3f93c687cf996024730440220341f52de6a6bf3c276b36d01beb5ceef2ef92f412b819ccbf6fcedd47010862d0220207edf7d8f2c4b67094cd2f4ec9cc47d9e86425eab7ab4c29ce616a213dbcddc012103469f5dd4372e630f925420615a91818ae500b53fe7517f02058e13f728e69b0c00000000"
  }
]
```

Agora compare com a v30:

```bash
bitcoin-cli-30 gettxspendingprevout \
'[{"txid":"'"$TXID_PARENT"'","vout":0}]' \
'{"return_spending_tx":true}'
```

Resultado:

```bash
error code: -1
error message:
gettxspendingprevout [{"txid":"hex","vout":n},...]
```

**O que mudou**

Na v30, o `gettxspendingprevout` aceita apenas a lista de outputs e retorna, no máximo, o `spendingtxid`.

Na v31, ele aceita um objeto de opções. Com `return_spending_tx=true`, o node retorna também a transação completa que está gastando aquele output.

Isso muda a utilidade prática do RPC:

> antes, você descobria quem gastou; agora, você também consegue inspecionar como gastou.
> 

### 🧪 Lab 5 — A mempool como mercado de espaço em bloco

Até aqui vimos que a v31 passou a expor melhor a estrutura interna da mempool: clusters, chunks e relações entre transações. Agora vamos fechar com uma visão mais macro.

A v31 trouxe um novo RPC:

👉 `getmempoolfeeratediagram`

Esse método mostra uma espécie de **curva acumulada da mempool**, indicando como os chunks competem por espaço em bloco de acordo com o feerate.

Rode:

```bash
bitcoin-cli-31 getmempoolfeeratediagram | jq '.[0:15]'
```

Exemplo:

```bash
[
  {
    "weight": 0,
    "fee": 0E-8
  },
  {
    "weight": 662,
    "fee": 0.03071112
  },
  {
    "weight": 1615,
    "fee": 0.03073511
  },
  {
    "weight": 2535,
    "fee": 0.03075819
  },
  {
    "weight": 6907,
    "fee": 0.03081289
  },
  {
    "weight": 7475,
    "fee": 0.03081769
  },
  {
    "weight": 8307,
    "fee": 0.03082082
  },
  {
    "weight": 8984,
    "fee": 0.03082253
  },
  {
    "weight": 10537,
    "fee": 0.03082642
  },
  {
    "weight": 61777,
    "fee": 0.03088630
  },
  {
    "weight": 65265,
    "fee": 0.03088720
  }
]

```

Agora compare com a v30:

```bash
bitcoin-cli-30 getmempoolfeeratediagram
```

Resultado:

```bash
error code: -32601
error message:
Method not found
```

**Como interpretar esse diagrama**

Cada ponto do resultado mostra uma fronteira de inclusão econômica.

Por exemplo:

```bash
{
  "weight":121070,
  "fee":0.07170817
}
```

Isso não significa que existe necessariamente uma única transação com esse peso. Também não significa que o node está apenas agrupando transações por faixas de fee.

A leitura correta é:

> até esse peso acumulado, existe uma determinada condição econômica de inclusão no bloco.
> 

O `weight` representa espaço acumulado em unidades de peso. Um bloco pode ter até aproximadamente 4.000.000 weight units.

O `fee` representa o valor associado àquela fronteira econômica. Na prática, o diagrama ajuda a visualizar como a mempool está organizada do ponto de vista da competição por espaço.

Esses saltos acontecem por **chunks**, não necessariamente por transações individuais. Um chunk pode ser uma única transação ou um conjunto de transações relacionadas dentro de um cluster.

Por isso, quando vemos algo como:

```bash
{
  "weight":121070,
  "fee":0.07170817
},
{
  "weight":121902,
  "fee":0.07171130
}
```

a diferença de peso indica o próximo chunk considerado na curva. Esse chunk pode conter uma transação ou várias transações economicamente relacionadas.

**Um cuidado sobre a signet**

Como estamos usando signet, a curva tende a ser pouco dinâmica. A mempool é menor, há menos competição e quase tudo tende a ser confirmado com facilidade.

Na mainnet, em momentos de congestionamento, esse tipo de diagrama tende a ser muito mais expressivo, porque a competição por espaço em bloco é real.

**O que mudou**

Na v30, esse RPC não existe.

Na v31, o node passa a expor uma visão agregada da mempool como um mercado de espaço em bloco.

> antes, você via transações; agora, você consegue observar a estrutura econômica da mempool.
> 

---

### O que realmente mudou

Depois desses labs, dá pra resumir assim:

- v30: você via transações
- v31: você vê estruturas econômicas

Mais especificamente:

- clusters → relações entre transações
- chunks → unidades econômicas reais
- feerate diagram → mercado de espaço em bloco

---

***Nota sobre P2P**

A v31 também traz melhorias importantes na camada P2P:

- melhor suporte a package relay
- mudanças internas no processamento de transações
- integração com o novo modelo de cluster mempool

Mas essas mudanças são mais difíceis de observar diretamente via `bitcoin-cli`, pois envolvem comportamento distribuído entre nodes.

---

***Nota sobre a estimativa de taxas mais granular**

A v31 também trouxe melhorias no estimador de taxas.

O menor bucket de feerate passou de 1 sat/vB para 0.1 sat/vB, alinhando com o `minrelaytxfee` padrão do node. Na prática, isso permite estimativas mais precisas em cenários de baixa demanda por espaço em bloco.

Essa mudança não é facilmente observável em experimentos locais, pois depende de dados históricos acumulados pelo node.

---

A mudança da v31 não é só técnica.

> o que compete por espaço no bloco não são transações, são conjuntos de transações economicamente viáveis
> 

👉 agora você consegue ver isso diretamente com `bitcoin-cli`.

Escrito por: Rafael Santos
