# Implementando métricas on-chain com Bitcoin Core

Métricas on-chain aparecem o tempo todo em análises sobre Bitcoin.

Quantidade de transações, taxas pagas, utilização dos blocos, idade de UTXOs, Coin Days Destroyed, realized cap e muitas outras.

Mas essas métricas não existem prontas dentro da blockchain.

O que existe são dados brutos:

```
blocos
 ├── timestamp
 ├── weight
 └── transações
       ├── inputs
       ├── outputs
       ├── valores
       └── witness
```

Uma métrica on-chain surge quando esses dados são extraídos, transformados e agregados.

O processo, de forma simplificada, é:

```
dados da blockchain
        ↓
extração
        ↓
transformação
        ↓
agregação
        ↓
métrica
```

Neste artigo vamos implementar duas métricas simples usando apenas um node Bitcoin Core:

- utilização dos blocos;
- fee rate mediano das transações.

A ideia não é construir uma plataforma de análise, mas mostrar como métricas on-chain podem ser derivadas diretamente dos dados da blockchain.

---

### 1. Utilização dos blocos

Um bloco Bitcoin pode ter no máximo:

```
4.000.000 weight units
```

Podemos então definir a utilização de um bloco como:

```
utilização = weight do bloco / 4.000.000
```

Por exemplo, um bloco com:

```
weight = 3.600.000
```

possui:

```
3.600.000 / 4.000.000 = 90%
```

de utilização.

O Bitcoin Core já fornece o `weight` diretamente:

```bash
bitcoin-cli -datadir="." getblockhash <altura>
```

e depois:

```bash
bitcoin-cli -datadir="." getblock <hash>
```

Entre os campos retornados teremos:

```bash
{
  "height": 000000,
  "nTx": 0000,
  "weight": 0000000
}
```

A métrica, portanto, é apenas uma transformação desse dado bruto.

Em Python:

```python
MAX_BLOCK_WEIGHT = 4_000_000
utilization = block["weight"] / MAX_BLOCK_WEIGHT * 100
```

Se fizermos isso para vários blocos consecutivos, conseguimos construir uma série temporal da utilização da rede.

---

### 2. Fee rate das transações

A segunda métrica exige descer um nível e analisar as transações dentro do bloco.

Podemos solicitar ao Bitcoin Core que retorne as transações completas:

```bash
bitcoin-cli -datadir="." getblock <hash> 2
```

Cada transação contém, entre outros campos:

```bash
{
  "txid": "...",
  "vsize": 182,
  "weight": 726,
  "fee": 0.00001234
}
```

O fee rate pode então ser calculado por:

```bash
fee rate = fee / vsize
```

Convertendo a fee para satoshis:

```bash
fee_sats = fee_btc * 100_000_000

fee_rate = fee_sats / tx["vsize"]
```

O resultado é expresso em:

```bash
sat/vB
```

Ao fazer isso para todas as transações de um bloco, podemos obter, por exemplo, o fee rate mediano.

```python
median_fee_rate = statistics.median(fee_rates)
```

A coinbase é ignorada, porque não paga fee.

---

### 3. Um pequeno coletor de métricas

Podemos juntar as duas ideias em um único script.

A função abaixo analisa um bloco:

```python
def analyze_block(height):
    block_hash = bitcoin_cli("getblockhash", height)
    block = bitcoin_cli("getblock", block_hash, 2)

    weight = block["weight"]

    utilization = (
        weight / 4_000_000 * 100
    )

    fee_rates = []
    total_fees_btc = 0

    for tx in block["tx"]:

        if "fee" not in tx:
            continue

        fee_btc = float(tx["fee"])
        fee_sats = fee_btc * 100_000_000

        fee_rate = (
            fee_sats / tx["vsize"]
        )

        fee_rates.append(fee_rate)
        total_fees_btc += fee_btc

    median_fee_rate = (
        statistics.median(fee_rates)
        if fee_rates
        else 0
    )

    return {
        "height": height,
        "transactions": len(block["tx"]),
        "weight": weight,
        "utilization": utilization,
        "fees_btc": total_fees_btc,
        "median_fee_rate": median_fee_rate,
    }
```

Agora basta percorrer uma sequência de blocos:

```python
tip = bitcoin_cli("getblockcount")

start = tip - 143

for height in range(start, tip + 1):
    data = analyze_block(height)

    print(
        height,
        data["utilization"],
        data["median_fee_rate"]
    )
```

Isso nos permite analisar os últimos:

```
144 blocos
```

aproximadamente um dia de atividade da rede.

---

### 4. Aplicando à mainnet

Executamos o script sobre os últimos 144 blocos da mainnet, aproximadamente um dia de atividade da rede.

Para cada bloco coletamos:

```
altura
número de transações
weight
utilização do bloco
fees totais
fee rate mediano
```

O resultado foi:

```
Blocos analisados:       144
Transações:              563.561
Utilização média:        98,47%
Fees totais:             4,36242932 BTC
Fee rate mediano:        1,20 sat/vB
```

A Figura abaixo mostra as duas métricas ao longo do período. Como dois blocos apresentaram utilização muito baixa, o painel superior utiliza uma escala ampliada para mostrar com mais detalhe os demais blocos.

![**Figura 1 —** Utilização dos blocos e fee rate mediano nos últimos 144 blocos da mainnet.](Implementando%20m%C3%A9tricas%20on-chain%20com%20Bitcoin%20Core/grafico_metricas_mainnet_144.png)

**Figura 1 —** Utilização dos blocos e fee rate mediano nos últimos 144 blocos da mainnet.

A utilização média foi bastante alta: 98,47%. Em grande parte do período, os blocos ficaram muito próximos do limite de 4 milhões de weight units.

Ao mesmo tempo, o fee rate mediano variou bastante entre os blocos. O bloco `969468`, por exemplo, teve mediana de `8,10 sat/vB`, enquanto outros blocos igualmente próximos do limite ficaram abaixo de `0,30 sat/vB`.

Esse contraste já mostra por que diferentes métricas precisam ser analisadas em conjunto.

### 5. Uma métrica isolada não conta toda a história

Um bloco cheio não significa necessariamente que as transações estão pagando fees elevadas.

Nos dados analisados, praticamente todos os blocos estavam próximos do limite de peso, mas os fee rates variaram de forma significativa.

Em alguns blocos, a mediana passou de `5 sat/vB`. Em outros, mesmo com utilização próxima de 100%, ficou em torno de `0,25–0,30 sat/vB`.

Isso acontece porque as duas métricas medem coisas diferentes. A utilização do bloco indica quanto da capacidade disponível foi ocupada. O fee rate indica quanto as transações pagaram por unidade desse espaço.

Por isso, olhar apenas para uma das duas pode esconder parte do comportamento da rede.

---

### 6. Como surgem métricas mais complexas?

O mesmo princípio pode ser usado para construir métricas muito mais sofisticadas.

Por exemplo:

**Número de transações**

```
bloco
  ↓
contar transações
```

**Fees totais**

```
transações
  ↓
somar fees
```

**Idade de UTXOs gastos**

```
input
  ↓
localizar output anterior
  ↓
descobrir quando foi criado
  ↓
calcular idade
```

**Coin Days Destroyed**

```
UTXO gasto
  ↓
valor × idade
  ↓
somar resultados
```

Outras métricas podem ainda combinar os dados da blockchain com informações externas.

A realized cap, por exemplo, exige também conhecer o preço do Bitcoin no momento em que cada moeda foi movimentada.

---

### 7. O que uma plataforma de métricas on-chain faz?

Ferramentas de análise on-chain em larga escala fazem essencialmente versões muito mais sofisticadas desse processo.

Elas:

```
leem a blockchain
      ↓
indexam transações e UTXOs
      ↓
extraem características
      ↓
agregam dados
      ↓
constroem séries temporais
```

A diferença está principalmente na escala. Enquanto nosso script consulta apenas alguns blocos diretamente no Bitcoin Core, plataformas especializadas mantêm grandes bancos de dados e índices preparados para responder rapidamente a consultas sobre toda a história da blockchain.

Mas a origem dos dados continua sendo a mesma.

---

### Conclusão

Métricas on-chain não são informações adicionais inseridas no Bitcoin. Elas são interpretações construídas a partir dos dados que a própria blockchain registra.

Neste experimento usamos apenas alguns campos:

```
block weight
transaction fee
transaction vsize
```

e a partir deles construímos duas métricas:

```
utilização do bloco
fee rate mediano
```

O mesmo processo pode ser estendido para dezenas de outros indicadores.

No fim, boa parte da análise on-chain pode ser resumida em uma pergunta:

> **Que informação podemos extrair quando começamos a combinar os dados que já existem dentro da blockchain?**
> 

por: Rafael Penna
