# Chainstate, validação e políticas

Quando você roda um node Bitcoin, ele não é um simples “replicador de blocos”.

Ele é um **validador ativo**, que mantém estado, aplica regras, impõe políticas e decide **o que aceita, o que rejeita e o que propaga**.

---

### Chainstate: o estado vivo do Bitcoin

O **chainstate** é o banco de dados que contém o **UTXO set,** o conjunto de todas as saídas **ainda não gastas** da blockchain. O node **não recalcula saldos varrendo blocos**. Ele mantém esse estado atualizado **incrementalmente**.

**O que é o UTXO set?**

Cada entrada contém:

- `txid`
- `vout`
- valor
- scriptPubKey
- altura do bloco

Toda validação passa por ele.

---

**Inspecionando o chainstate**

Podemos inspecionar diretamente o *chainstate,* o conjunto de todas as saídas não gastas (UTXOs), usando o comando:

```bash
bitcoin-cli -datadir="." gettxoutsetinfo
```

Exemplo de saída:

```json
{
"height":1550,
"bestblock":"0da68f5e9fbe6266f7b08c7704e5d42b18c824005eb2153e098c82cac99ff6b3",
"txouts":1558,
"bogosize":114591,
"hash_serialized_3":"d97cf2b1fb4ac093c368d876052f51701d8a7f27bf7fff5500f2197f3ca124e6",
"total_amount":14937.84179662,
"transactions":1554,
"disk_size":111756
}
```

Essa saída descreve **o estado econômico atual do Bitcoin do ponto de vista do seu node**, ou seja, tudo aquilo que *pode* ser gasto neste momento.

**O que esses campos nos dizem?**

- **`height`**
    
    Altura do bloco mais recente considerado no *chainstate*. Neste exemplo, o estado reflete a blockchain até o bloco **1550**.
    
- **`bestblock`**
    
    Hash do bloco que define o estado atual do conjunto de UTXOs. Qualquer mudança nesse hash implica uma alteração no estado econômico global.
    
- **`txouts`**
    
    Número total de UTXOs existentes: **1558 saídas não gastas**.
    
    Cada UTXO representa uma “moeda” individual que pode ser usada como entrada em uma transação futura.
    
- **`transactions`**
    
    Número de transações distintas que contribuíram para o conjunto atual de UTXOs (**1554**). Uma única transação pode gerar múltiplos UTXOs.
    
- **`total_amount`**
    
    Soma de todos os bitcoins presentes no *chainstate*:
    
    **14 937.84179662 BTC**.
    
    Esse valor representa **todo o bitcoin atualmente disponível para gasto**, excluindo moedas já gastas e incluindo recompensas de mineração até essa altura.
    
- **`hash_serialized_3`**
    
    Hash criptográfico do conjunto completo de UTXOs serializado.
    
    Ele funciona como um *commitment* ao estado econômico global, permitindo que diferentes nodes verifiquem se possuem exatamente o mesmo conjunto de moedas não gastas.
    
- **`bogosize`**
    
    Um tamanho “estimado” em memória do conjunto de UTXOs, usado internamente para métricas e comparações (**114 591 bytes**).
    
- **`disk_size`**
    
    Espaço efetivamente ocupado pelo *chainstate* no disco: **111 756 bytes**.
    
    Esse número cresce ao longo do tempo à medida que o número de UTXOs aumenta.
    

Diferente da blockchain (que é um **registro histórico imutável**), o *chainstate* representa o **presente econômico do Bitcoin**.

É ele que permite que um node:

- valide se uma transação está tentando gastar moedas inexistentes,
- impeça *double-spending*,
- calcule corretamente saldos e taxas,
- opere sem precisar reprocessar toda a história a cada novo bloco.

Em outras palavras:

> O chainstate é o “livro-caixa vivo” do Bitcoin.
> 

Embora a blockchain conte *como* chegamos até aqui, é o *chainstate* que define **o que realmente pode ser gasto agora**.

---

### Validação incremental: como o node pensa

Quando um novo bloco chega, o node **não revalida tudo**.

Ele faz validação **incremental**:

1. Verifica o **header**
2. Confere Proof of Work
3. Checa conexão com a chain
4. Processa transações uma a uma
5. Atualiza o **UTXO set**
6. Remove UTXOs gastos
7. Adiciona novos UTXOs criados

Se qualquer etapa falhar → **bloco inválido**

---

### Verificando a saúde da blockchain

Podemos forçar o node a revalidar a blockchain já armazenada usando:

```bash
bitcoin-cli -datadir="." verifychain
```

Saída:

```bash
true
```

Esse comando instrui o Bitcoin Core a verificar blocos já presentes em disco, garantindo que:

- os **headers** continuam obedecendo às regras de consenso,
- todas as **transações** são válidas,
- os **scripts** (incluindo assinaturas) continuam sendo avaliados corretamente.

O valor retornado (`true`) indica que **nenhuma inconsistência foi encontrada** durante a verificação. Em outras palavras, o node percorreu a porção configurada da blockchain (por padrão, os blocos mais recentes) e confirmou que:

- não há blocos corrompidos,
- nenhuma regra de consenso foi violada,
- o estado atual deriva corretamente da história validada.

Se algum erro fosse detectado, por exemplo, um bloco inválido, dados corrompidos em disco ou uma falha de verificação de script, o comando retornaria `false`, e o node marcaria os blocos problemáticos como inválidos, interrompendo a sincronização normal até que o problema fosse resolvido.

---

### Forks, reorgs e pontas da chain

Um node Bitcoin pode enxergar **mais de uma ponta de blockchain ao mesmo tempo**. Isso acontece quando diferentes blocos competem para estender a mesma altura, seja por latência de rede, mineração simultânea ou tentativas inválidas.

Podemos inspecionar todas as “pontas” conhecidas pelo node com:

```bash
bitcoin-cli -datadir="." getchaintips
```

Exemplo de saída:

```json
[
{
"height":1550,
"hash":"0da68f5e9fbe6266f7b08c7704e5d42b18c824005eb2153e098c82cac99ff6b3",
"branchlen":0,
"status":"active"
}
]
```

**Interpretando a saída**

Cada objeto da lista representa uma **ponta de cadeia** (*chain tip*) conhecida pelo node:

- **`height`**
    
    A altura do último bloco daquela cadeia.
    
- **`hash`**
    
    O hash do bloco que define a ponta da cadeia.
    
- **`branchlen`**
    
    Quantos blocos aquela cadeia está atrás da chain ativa.
    
    Um valor `0` indica que essa é a própria chain principal.
    
- **`status`**
    
    O estado daquela cadeia do ponto de vista do consenso.
    

No exemplo acima, o node conhece **apenas uma ponta**, marcada como:

```json
"status":"active"
```

Isso significa que:

- não há forks conhecidos no momento,
- não existem cadeias competidoras,
- o consenso local está estável.

**Como isso muda quando há forks?**

Agora imagine que dois mineradores encontrem blocos quase ao mesmo tempo na altura 1550. O node pode ver algo assim:

```json
[
{
"height":1551,
"hash":"000000aaa...",
"branchlen":0,
"status":"active"
},
{
"height":1551,
"hash":"000000bbb...",
"branchlen":1,
"status":"valid-fork"
}
]
```

Nesse cenário:

- A primeira entrada é a **chain ativa**.
- A segunda é um **fork válido**, mas com menos trabalho acumulado.
- `branchlen: 1` indica que essa cadeia divergiu **um bloco atrás** do ponto comum.

O node **mantém ambas temporariamente**, aguardando para ver qual delas será estendida primeiro.

**Reorgs na prática**

Se o fork alternativo receber mais trabalho acumulado (por exemplo, mais blocos minerados), o node pode realizar um **reorg** (*reorganization*):

- blocos da chain antiga são desconectados,
- blocos da nova chain são conectados,
- o *chainstate* é atualizado para refletir o novo histórico vencedor.

Esse processo é automático e segue estritamente as regras de consenso.

**Cadeias inválidas e órfãs**

Também é possível encontrar outros estados:

- **`valid-fork`**
    
    Cadeia válida, mas não ativa.
    
- **`headers-only`**
    
    O node conhece apenas os headers, não os blocos completos.
    
- **`invalid`**
    
    Cadeia que violou regras de consenso e foi permanentemente descartada.
    

**Regra fundamental**

Embora seja comum dizer que o Bitcoin segue a *“cadeia mais longa”*, isso é apenas uma simplificação. A regra real é:

> O node segue a cadeia com maior trabalho acumulado (most work).
> 

O comprimento em blocos é irrelevante se o trabalho computacional total for menor.

---

### Mempool: onde tudo começa

Antes de entrar em um bloco, toda transação passa pelo **mempool**.

Ele funciona como uma *sala de espera* mantida por cada node, onde ficam as transações:

- **locais** (cada node tem o seu),
- **voláteis** (podem ser descartadas a qualquer momento),
- **governadas por políticas**, não por consenso.

**Inspecionando o mempool**

Podemos observar o estado atual do mempool com:

```bash
bitcoin-cli -datadir="." getmempoolinfo
```

Exemplo de saída:

```json
{
"loaded":true,
"size":0,
"bytes":0,
"usage":0,
"total_fee":0.00000000,
"maxmempool":300000000,
"mempoolminfee":0.00001000,
"minrelaytxfee":0.00001000,
"incrementalrelayfee":0.00001000,
"unbroadcastcount":0,
"fullrbf":true
}
```

### Interpretando os campos

- **`loaded`**
    
    Indica se o mempool foi carregado do disco na inicialização do node.
    
    `true` significa que, se houvesse transações pendentes anteriormente, elas foram restauradas.
    
- **`size`**
    
    Número de transações atualmente no mempool.
    
    Neste exemplo, `0` indica que **nenhuma transação está aguardando confirmação**.
    
- **`bytes`**
    
    Tamanho total bruto das transações no mempool, em bytes.
    
- **`usage`**
    
    Uso real de memória, incluindo estruturas internas do node.
    
    Mesmo com poucos bytes de transação, o `usage` pode ser maior.
    
- **`total_fee`**
    
    Soma de todas as taxas das transações atualmente no mempool.
    
    Aqui, como o mempool está vazio, o valor é `0.00000000 BTC`.
    
- **`maxmempool`**
    
    Tamanho máximo permitido para o mempool (**300 MB**).
    
    Quando esse limite é atingido, o node começa a **evictar** transações com menor taxa.
    
- **`mempoolminfee`**
    
    Taxa mínima dinâmica para uma transação **permanecer** no mempool.
    
    Esse valor sobe automaticamente quando o mempool está cheio.
    
- **`minrelaytxfee`**
    
    Taxa mínima absoluta para que o node **aceite e propague** uma transação.
    
    Transações abaixo desse valor são rejeitadas imediatamente.
    
- **`incrementalrelayfee`**
    
    Incremento mínimo exigido para substituições via RBF (*Replace-By-Fee*).
    
- **`unbroadcastcount`**
    
    Número de transações que ainda não foram anunciadas aos peers.
    
    Útil para depuração de propagação.
    
- **`fullrbf`**
    
    `true` indica que o node opera em modo **Full RBF**, permitindo a substituição de transações não confirmadas, mesmo sem sinalização explícita de RBF.
    

**Listando transações no mempool**

Para ver os identificadores das transações atualmente aceitas:

```bash
bitcoin-cli -datadir="." getrawmempool
```

- Se o mempool estiver vazio, a saída será uma lista vazia (`[]`).
- Caso contrário, cada entrada será um **txid** aguardando confirmação.
- A presença de um txid aqui **não garante** inclusão em bloco, apenas que a transação passou pelas políticas locais do node.

---

Diferente da blockchain e do *chainstate*, o mempool:

- **não é consenso**,
- **não é compartilhado globalmente**,
- **não é confiável como fonte de verdade**.

Por isso:

> Uma transação pode estar no seu mempool, mas não no do minerador, e simplesmente “morrer” sem nunca ser confirmada.
> 

---

### Policy Layer: válido não significa aceito

Uma das ideias mais importantes, e mais mal compreendidas, do Bitcoin é que **nem tudo que é válido precisa ser aceito ou propagado pelo seu node**. O protocolo Bitcoin separa claramente duas camadas:

A primeira é o **consenso**. Ela define as regras fundamentais do sistema: o que é um bloco válido, o que é uma transação válida, como assinaturas são verificadas, como o Proof of Work é avaliado. Essas regras **não podem ser quebradas**. Se forem, o bloco ou a transação simplesmente não fazem parte do Bitcoin.

A segunda é a **policy**. Ela não define o que é Bitcoin, mas define **como o seu node se comporta**. São regras locais que determinam o que o node aceita no mempool, o que ele retransmite para outros peers e o que ele ignora silenciosamente.

É aqui que surge uma distinção crucial: Uma transação pode ser **válida pelo consenso** e, ainda assim, ser **rejeitada pelo seu node**. Isso não é um erro. É uma escolha de projeto.

---

**O papel real das políticas**

As políticas existem para proteger o node e, por consequência, a rede. Elas impõem limites práticos: formatos considerados padrão (standardness), restrições de tamanho, regras contra dust, limites de sigops, mecanismos de proteção contra ataques de negação de serviço e exigência de uma taxa mínima para relay.

Nada disso muda o consenso do Bitcoin. Mas tudo isso influencia **quais transações circulam com facilidade na rede**. Cada node aplica essas regras de forma local. Não existe um “policiamento global”. Existe apenas um conjunto de nodes independentes tomando decisões defensivas.

---

**O que significa “bloquear” uma transação?**

Quando dizemos que um node bloqueia uma transação, isso pode significar coisas diferentes.

O node pode simplesmente não inseri-la no mempool. Pode aceitá-la localmente, mas decidir não propagá-la para seus peers. Ou pode ignorá-la completamente.

Tudo isso acontece **sem violar o consenso** e sem causar forks. É por isso que se diz que policy é **design, não bug**. Ela não enfraquece o Bitcoin, ela o torna viável em uma rede aberta e hostil.

---

**Compact Block Filters e responsabilidade com SPVs**

Além de validar e filtrar, nodes completos também ajudam clientes leves. Com os **Compact Block Filters (BIP158)**, um node pode fornecer filtros compactos que permitem a uma carteira SPV detectar se um bloco contém transações relevantes para ela, sem precisar baixar o bloco inteiro.

```bash
bitcoin-cli getblockfilter <blockhash>
```

Isso reduz uso de banda, melhora privacidade e reforça a descentralização, mostrando que um node não serve apenas a si mesmo, mas também ao ecossistema ao redor.

Além de validar blocos e manter o *chainstate*, nodes completos também desempenham um papel importante no suporte a **clientes leves (SPVs)**.

Com os **Compact Block Filters** definidos no **BIP158**, um node pode fornecer filtros compactos que permitem a uma carteira SPV verificar se um bloco **pode conter transações relevantes**, sem precisar baixar o bloco inteiro. Isso reduz o uso de banda, melhora a privacidade e reforça a descentralização da rede.

**Compact Block Filters em prática (regtest)**

Esse mecanismo pode ser testado facilmente em **regtest**, desde que o node tenha sido iniciado com o índice de filtros habilitado:

```bash
bitcoind -datadir="." -daemon -blockfilterindex=1
```

Após gerar alguns blocos, podemos consultar o filtro de um bloco específico.

Gerando blocos:

```bash
bitcoin-cli -datadir="." getnewaddress
bcrt1qymfwld4wpvm56a6hkagxsysvryq0vc7t3cqnf8

bitcoin-cli -datadir="." generatetoaddress 10 bcrt1qymfwld4wpvm56a6hkagxsysvryq0vc7t3cqnf8
```

Saída (hashes dos blocos minerados):

```
446b41dbb176c39837db34ea22d9155204bc13d808433f83e7e701270824cf52
43211400d6a224f2267ef54034d32f34dc7533fc91d57954f2325d97df05213b
4180543dd11c9a989186a37e92dd704fef8a430089e78756a13a814a205738ad
...
```

Agora podemos solicitar o filtro compacto do primeiro bloco minerado:

```bash
bitcoin-cli -datadir="." getblockfilter 446b41dbb176c39837db34ea22d9155204bc13d808433f83e7e701270824cf52
```

Resposta do node:

```json
{
"filter":"01602640",
"header":"9fbb9488198d8e4f0840ac2cf9d8017a1453f10e6d159602f9400b5cbeaea09b"
}
```

O que essa saída representa?

- **`filter`**
    
    O **Compact Block Filter (BIP158)** propriamente dito.
    
    Ele codifica, de forma probabilística, os elementos relevantes do bloco (scripts, chaves públicas, etc.), permitindo que um cliente leve teste se *vale a pena* baixar o bloco completo.
    
- **`header`**
    
    O **filter header**, encadeado criptograficamente com os filtros anteriores.
    
    Ele permite que clientes SPV validem a **continuidade e integridade da sequência de filtros**, de forma análoga ao encadeamento dos headers de blocos.
    

Mesmo em regtest, com blocos quase vazios, o filtro existe. Isso é importante:

> todo bloco possui um filtro, independentemente de conter ou não transações relevantes.
> 

### Experimento prático: quando o node rejeita uma transação válida

O objetivo aqui é demonstrar que uma transação pode:

- ser **válida pelo consenso**
- e ainda assim ser **rejeitada pelo node por policy**

O Bitcoin Core aplica **políticas de relay e de wallet**, que definem **limites mínimos *e* máximos de taxa** aceitáveis.

**1️⃣ Criando uma transação manual (raw)**

Para contornar as proteções do wallet automático, criamos uma transação manualmente:

```bash
bitcoin-cli -datadir="." createrawtransaction \
'[{"txid":"888d0863c1e6183ebbbccb66439af3341d34b649ddc9381417c5419de62e089f","vout":0}]' \
'{"bcrt1qymfwld4wpvm56a6hkagxsysvryq0vc7t3cqnf8":0.001}'
02000000019f082ee69d41c5171438c9dd49b6341d34f39a4366cbbcbb3e18e6c163088d880000000000fdffffff01a08601000000000016001426d2efb6ae0b374d7757b75068120c1900f663cb00000000
```

Depois, assinamos:

```bash
bitcoin-cli -datadir="." signrawtransactionwithwallet 02000000019f082ee69d41c5171438c9dd49b6341d34f39a4366cbbcbb3e18e6c163088d880000000000fdffffff01a08601000000000016001426d2efb6ae0b374d7757b75068120c1900f663cb00000000
{
  "hex": "020000000001019f082ee69d41c5171438c9dd49b6341d34f39a4366cbbcbb3e18e6c163088d880000000000fdffffff01a08601000000000016001426d2efb6ae0b374d7757b75068120c1900f663cb02473044022037c2725ab09abe53e606fc684a31d49420976a69297c21efbf87ecf5f75c95c802202fc1f578a2069c51d9b9c10fddeb2ecc2e9ca60fb7fa8571006998c9565e0a8601210243c4dcb97cc5632f58869e24dd483bfdd8836b48514b9de9dd1482af05a1e2c900000000",
  "complete": true
}
```

A transação é considerada **completa e válida** `"complete":true`.

**2️⃣ Tentando transmitir a transação**

Ao tentar enviá-la:

```bash
bitcoin-cli -datadir="." sendrawtransaction 020000000001019f082ee69d41c5171438c9dd49b6341d34f39a4366cbbcbb3e18e6c163088d880000000000fdffffff01a08601000000000016001426d2efb6ae0b374d7757b75068120c1900f663cb02473044022037c2725ab09abe53e606fc684a31d49420976a69297c21efbf87ecf5f75c95c802202fc1f578a2069c51d9b9c10fddeb2ecc2e9ca60fb7fa8571006998c9565e0a8601210243c4dcb97cc5632f58869e24dd483bfdd8836b48514b9de9dd1482af05a1e2c900000000
```

O node responde:

```
error code: -25
error message:
Fee exceeds maximum configured by user (e.g. -maxtxfee, maxfeerate)
```

O que realmente aconteceu?

- A transação é **válida pelo consenso**:
    - inputs existem,
    - assinaturas corretas,
    - nenhum double spend.
- Porém, o **fee implícito** ficou **alto demais** para os limites locais do node.
- O Bitcoin Core aplica uma **policy de proteção** contra:
    - erros de construção,
    - bugs,
    - ou transações que queimariam taxa acidentalmente.

👉 Resultado: **rejeição antes de entrar no mempool**.

Aqui vimos **duas políticas diferentes em ação**:

- ❌ `minrelaytxfee` → taxa **baixa demais**
- ❌ `maxtxfee / maxfeerate` → taxa **alta demais**

Ambas **não têm nada a ver com consenso**.

> O consenso define o que é válido.
> 
> 
> A policy define o que o seu node aceita e propaga.
> 

**E se um minerador incluir essa transação?**

Mesmo assim:

- se um minerador incluir essa transação em um **bloco válido**,
- respeitando apenas regras de consenso,

**o bloco será aceito por todos os nodes**.

Policies **não invalidam blocos**.

Elas só regulam **comportamento local e propagação**.

---

Ao longo deste artigo, vimos que um node Bitcoin não é um espectador passivo da blockchain. Ele mantém um estado econômico vivo por meio do *chainstate*, valida blocos de forma incremental, gerencia forks e reorgs, filtra transações no mempool e aplica políticas locais que protegem tanto a si quanto a rede como um todo. A distinção entre consenso e policy deixa claro que o Bitcoin não funciona por permissões globais, mas por decisões independentes tomadas por milhares de nodes soberanos. Rodar um node é assumir responsabilidade: verificar em vez de confiar, decidir em vez de aceitar cegamente e participar ativamente da segurança e da resiliência do sistema. É nesse ponto que o Bitcoin deixa de ser apenas uma tecnologia usada e passa a ser um protocolo compreendido.

Escrito por: Rafael Santos
