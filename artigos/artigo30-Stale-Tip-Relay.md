# Stale Tip Relay: a proposta para enxergar blocos que perderam a corrida

Quando um novo bloco é encontrado no Bitcoin, ele começa a ser propagado pela rede para que outros nodes possam validá-lo e atualizar sua própria visão da blockchain.

Na maior parte do tempo, esse processo acontece sem grandes surpresas. Mas existe uma situação possível: dois mineradores podem encontrar blocos diferentes praticamente ao mesmo tempo, ambos apontando para o mesmo bloco anterior.

Por alguns instantes, a rede passa a ter duas pontas concorrentes:

```
             bloco 110
              /   \
           111A   111B
```

Os dois blocos podem ser perfeitamente válidos. O problema é que apenas uma dessas branches acabará fazendo parte da cadeia com mais trabalho acumulado.

Se um novo bloco for encontrado sobre `111B`, por exemplo:

```
             110
            /   \
         111A   111B
                  |
                112B
```

a branch da direita passa a ser a cadeia ativa. O bloco `111A`, apesar de válido, perdeu a corrida.

Ele se tornou um **stale block**.

Isso não é nenhuma novidade no Bitcoin. A novidade é uma proposta apresentada recentemente na lista Bitcoin-Dev chamada **Stale Tip Relay**, que sugere mudar o que acontece com a informação sobre esses blocos depois que eles perdem essa disputa.

A proposta foi publicada em 29 de julho de 2026 por Ram e w0xlt, a partir de um trabalho anterior de Anthony Towns. Ela define uma nova mensagem P2P opcional chamada `staletip`, destinada justamente a propagar informações sobre pontas stale recentes.

Mas antes de entender a proposta, vale observar um problema que existe hoje.

### Nem todos os nodes enxergam a mesma história

Quando a rede identifica uma cadeia vencedora, ela é rapidamente propagada entre os nodes.

A branch perdedora, por outro lado, deixa de ter importância para a sincronização normal da blockchain. Na prática, isso significa que um node que chegou a receber um determinado bloco stale pode conhecê-lo, enquanto outro node, um pouco mais distante daquela disputa, pode nunca saber que ele existiu.

Podemos observar esse comportamento utilizando três nodes Bitcoin Core em regtest. A ideia do experimento é simples: criar uma situação em que um dos nodes conheça uma branch que perdeu a disputa, enquanto outro node, mais distante, nunca chega a receber esse bloco.

Vamos chamar os três nodes de A, B e C.

### Preparando os três nodes

Primeiro criamos três instâncias independentes do Bitcoin Core:

```bash
mkdir -p /tmp/staletip/{nodeA,nodeB,nodeC}
```

Iniciamos o Node A:

```bash
bitcoind -regtest \
  -datadir=/tmp/staletip/nodeA \
  -daemon \
  -server \
  -listen=1 \
  -port=19000 \
  -rpcport=19010 \
  -fallbackfee=0.00001
```

O Node B:

```bash
bitcoind -regtest \
  -datadir=/tmp/staletip/nodeB \
  -daemon \
  -server \
  -listen=1 \
  -port=19100 \
  -rpcport=19110 \
  -fallbackfee=0.00001
```

E o Node C:

```bash
bitcoind -regtest \
  -datadir=/tmp/staletip/nodeC \
  -daemon \
  -server \
  -listen=1 \
  -port=19200 \
  -rpcport=19210 \
  -fallbackfee=0.00001
```

Para facilitar os comandos, criamos três aliases:

```bash
alias cliA='bitcoin-cli -regtest -datadir=/tmp/staletip/nodeA -rpcport=19010'
alias cliB='bitcoin-cli -regtest -datadir=/tmp/staletip/nodeB -rpcport=19110'
alias cliC='bitcoin-cli -regtest -datadir=/tmp/staletip/nodeC -rpcport=19210'
```

Podemos confirmar que todos começaram no bloco 0:

```bash
cliA getblockcount
cliB getblockcount
cliC getblockcount
```

Resultado:

```
0
0
0
```

### Criando uma cadeia comum

Primeiro conectamos C ao Node B:

```bash
cliC addnode "127.0.0.1:19100" onetry
```

Criamos uma wallet no Node B:

```bash
cliB createwallet miner
```

Geramos um endereço:

```bash
ADDR_B=$(cliB -rpcwallet=miner getnewaddress)
```

E mineramos 110 blocos:

```bash
cliB generatetoaddress 110 "$ADDR_B"
```

Como B e C estão conectados, ambos chegam ao bloco 110:

```bash
cliB getblockcount
cliC getblockcount
```

Resultado:

```
110
110
```

Agora conectamos A ao B:

```bash
cliA addnode "127.0.0.1:19100" onetry
```

E confirmamos:

```bash
cliA getblockcount
```

```
110
```

Nesse momento, os três nodes compartilham exatamente a mesma cadeia:

```
0 → ... → 110
```

### Criando uma branch que apenas A conhece

Agora isolamos completamente o Node A:

```bash
cliA setnetworkactive false
```

O número de conexões cai para zero:

```bash
cliA getconnectioncount
```

```
0
```

Enquanto B e C continuam conectados, A está sozinho.

Criamos uma wallet nele:

```bash
cliA createwallet miner
```

Geramos um endereço:

```bash
ADDR_A=$(cliA -rpcwallet=miner getnewaddress)
```

E mineramos um único bloco:

```bash
STALE=$(cliA -rpcwallet=miner generatetoaddress 1 "$ADDR_A" | jq -r '.[0]')
```

O hash encontrado no nosso experimento foi:

```
43d0e3a419338b8092b83327c512c60f1e362e52230130d397e1d24e8a82b9f5
```

Esse é o bloco 111 conhecido apenas por A.

Enquanto isso, B continua conectado a C e minera dois novos blocos:

```bash
cliB -rpcwallet=miner generatetoaddress 2 "$ADDR_B"
```

No nosso teste, os hashes foram:

```
111B:
19c3a2b423dd57d275b86734a94cda21526c532db8c2c4ec5e20fbf9abafa3ea

112B:
69a0b85ecc145798c53afeb439c21ebeb1416fae12a33952b306d1c50075e4f5
```

Agora temos:

```
             110
            /   \
         111A   111B
                  |
                112B
```

Mas essas duas branches não são conhecidas por todos.

A conhece apenas:

```
110 → 111A
```

B e C conhecem:

```
110 → 111B → 112B
```

### O Node C nunca recebeu o bloco de A

Podemos confirmar isso consultando o header de `111A` no Node A:

```bash
cliA getblockheader "$STALE"
```

O comando funciona normalmente e retorna o header do bloco.

Agora fazemos exatamente a mesma consulta no Node C:

```bash
cliC getblockheader "$STALE"
```

O resultado é:

```
error code: -5
error message:
Block not found
```

C nunca recebeu aquele bloco.

Se consultarmos suas tips:

```bash
cliC getchaintips
```

ele conhece somente:

```json
[
  {
    "height": 112,
    "hash": "69a0b85ecc145798c53afeb439c21ebeb1416fae12a33952b306d1c50075e4f5",
    "branchlen": 0,
    "status": "active"
  }
]
```

### Reconectando A

Agora reativamos a rede do Node A:

```bash
cliA setnetworkactive true
```

E conectamos novamente ao Node B:

```bash
cliA addnode "127.0.0.1:19100" onetry
```

A recebe os blocos `111B` e `112B` e passa a considerar essa cadeia como ativa.

Confirmamos:

```bash
cliA getblockcount
```

```
112
```

Agora vem a parte mais interessante.

Executando:

```bash
cliA getchaintips
```

obtemos:

```json
[
  {
    "height": 112,
    "hash": "69a0b85ecc145798c53afeb439c21ebeb1416fae12a33952b306d1c50075e4f5",
    "branchlen": 0,
    "status": "active"
  },
  {
    "height": 111,
    "hash": "43d0e3a419338b8092b83327c512c60f1e362e52230130d397e1d24e8a82b9f5",
    "branchlen": 1,
    "status": "valid-fork"
  }
]
```

A reconhece a cadeia até o bloco 112 como ativa, mas continua lembrando do bloco `111A`, agora classificado como `valid-fork`.

No Node C, porém:

```bash
cliC getchaintips
```

continua retornando somente:

```json
[
  {
    "height": 112,
    "hash": "69a0b85ecc145798c53afeb439c21ebeb1416fae12a33952b306d1c50075e4f5",
    "branchlen": 0,
    "status": "active"
  }
]
```

E mesmo depois de todos estarem novamente conectados e sincronizados, C continua sem conhecer o bloco stale:

```bash
cliC getblockheader "$STALE"
```

```
error code: -5
error message:
Block not found
```

O resultado final do experimento é, portanto:

```
Node A
----------------
112B    active
111A    valid-fork

Node C
----------------
112B    active
```

Os dois nodes concordam perfeitamente sobre qual é a blockchain ativa. Mas apenas um deles sabe que o bloco `111A` existiu.

É exatamente esse tipo de diferença de visibilidade que motiva a proposta do **Stale Tip Relay**.

### A ideia do Stale Tip Relay

A proposta tenta permitir que essa informação continue circulando.

Para isso, ela introduz uma nova mensagem P2P:

```
staletip
```

Nodes que desejarem participar desse mecanismo poderiam anunciar a peers compatíveis a existência de uma branch stale recente.

Em vez de simplesmente esquecer a informação:

```
A -------- B -------- C

A conhece 111A

C nunca fica sabendo
```

poderíamos ter algo conceitualmente parecido com:

```
A -------- B -------- C
       |
       └── existe uma stale tip partindo daqui
```

A mensagem não significa que o bloco stale deve voltar para a cadeia ativa, nem altera qualquer regra de consenso. Ela apenas permite informar aos outros peers que aquela branch existiu.

A proposta inclui na mensagem o ponto onde ocorreu a bifurcação, uma sequência de headers da branch e uma indicação de que o node possui ou não o bloco correspondente disponível para ser solicitado.

O principal benefício seria tornar a observação da rede mais confiável. Com mais nodes compartilhando informações sobre stale tips recentes, pesquisadores e ferramentas de monitoramento dependeriam menos de estar “no lugar certo, na hora certa” para enxergar um bloco que perdeu a disputa. Isso permitiria medir melhor a taxa de stale blocks, comparar a qualidade da propagação de blocos entre diferentes regiões e conexões da rede e identificar com mais clareza situações anormais, como atrasos de relay, partições temporárias ou comportamentos incomuns de mineração. Tudo isso sem alterar a escolha da cadeia ativa: o Stale Tip Relay adicionaria informação sobre o que aconteceu ao redor do consenso, não mudaria o consenso em si.
Também existem limites para evitar que o mecanismo se transforme em uma forma barata de consumir recursos da rede. O draft propõe, entre outras restrições, branches com no máximo 20 headers, stale tips a no máximo 1.000 blocos da ponta ativa e um cache de até 10 tips recentes.

### Mais informação também significa mais complexidade

A proposta ainda está em discussão. Uma das questões levantadas na Bitcoin-Dev é justamente se melhorar a observabilidade dos stale blocks traz benefícios suficientes para justificar novas mensagens e novos dados circulando pela rede.

Também foram apontadas preocupações relacionadas a possíveis vetores de DoS e fingerprinting.

Portanto, o Stale Tip Relay não é uma mudança definida para o Bitcoin Core. É uma proposta em desenvolvimento tentando responder a uma questão interessante:

**quanto da história recente da rede vale a pena continuar propagando depois que o consenso sobre a cadeia vencedora já foi alcançado?**

Hoje, como vimos no nosso experimento, dois nodes podem concordar perfeitamente sobre a blockchain e ainda assim terem visões bastante diferentes sobre as branches que perderam a corrida.

O Stale Tip Relay propõe fazer com que uma parte dessa história deixe de desaparecer tão rapidamente.

por: Rafael Penna
