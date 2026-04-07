# Blocos Bitcoin

A blockchain do Bitcoin é, essencialmente, uma cadeia de blocos. Nesse artigo vamos entender **o que exatamente é um bloco**, como ele é construído, o que significa **minerar**, o que é **Proof of Work** e como o Bitcoin Core valida essas estruturas internamente.

Vamos usar comandos do bitcoin-cli (`getblock`, `getblockheader`, `getdifficulty`, `getchaintips`, `getblocktemplate`) e construir um entendimento sólido desse motor que mantém o Bitcoin funcionando desde 2009.

### **O que é um bloco no Bitcoin?**

Um bloco é um “pacote” de dados contendo:

- um **header** (80 bytes)
- uma lista de transações
- metadados como tamanho, peso, número de transações, hash do bloco anterior, etc.

Do ponto de vista do node, o bloco serve para duas funções críticas:

1. **Confirmar transações**
2. **Competir na mineração para estender a cadeia válida**

E aqui está uma parte importante:

> O node não confia no minerador.
> 
> 
> Ele verifica absolutamente tudo antes de aceitar um bloco.
> 

Para entender como essa validação funciona, precisamos abrir o bloco e o header por dentro.

### **Explorando o bloco com o bitcoin-cli**

Vamos começar inspecionando o bloco gênese (signet).

```bash
bitcoin-cli -datadir="." getblockhash 0
00000008819873e925422c1ff0f99f7cc9bbb232af63a077a480a3633bee1ef6
```

Isso retorna o hash do bloco 0 (gênese).

Agora vamos abrir o bloco:

```bash
bitcoin-cli -datadir="." getblock 00000008819873e925422c1ff0f99f7cc9bbb232af63a077a480a3633bee1ef6
{
  "hash": "00000008819873e925422c1ff0f99f7cc9bbb232af63a077a480a3633bee1ef6",
  "confirmations": 281914,
  "height": 0,
  "version": 1,
  "versionHex": "00000001",
  "merkleroot": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
  "time": 1598918400,
  "mediantime": 1598918400,
  "nonce": 52613770,
  "bits": "1e0377ae",
  "target": "000000148b520000000000000000000000000000000000000000000000000000",
  "difficulty": 0.001126515290698186,
  "chainwork": "000000000000000000000000000000000000000000000000000000000049d414",
  "nTx": 1,
  "nextblockhash": "00000086d6b2636cb2a392d45edc4ec544a10024d30141c9adf4bfd9de533b53",
  "strippedsize": 285,
  "size": 285,
  "weight": 1140,
  "tx": [
    "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
  ]
}
```

Vamos detalhar cada parte agora.

### Estrutura completa do header (80 bytes)

Cada bloco do Bitcoin começa com um **header fixo de 80 bytes**.

Esse header é a parte que realmente entra no cálculo do hash do bloco (`double-SHA256`), define o alvo de mineração e encadeia todos os blocos da blockchain.

Embora ferramentas como `bitcoin-cli getblockheader` exibam diversas informações adicionais, **o header real do protocolo contém apenas 6 campos**, sempre com o mesmo tamanho:

| Campo | Tamanho | Descrição |
| --- | --- | --- |
| **version** | 4 bytes | Sinaliza regras de consenso e softforks ativados |
| **previousblockhash** | 32 bytes | Hash do bloco anterior, encadeando a blockchain |
| **merkleroot** | 32 bytes | Raiz de Merkle das transações do bloco |
| **time** | 4 bytes | Timestamp Unix declarado pelo minerador |
| **bits** | 4 bytes | Target compactado usado na prova de trabalho |
| **nonce** | 4 bytes | Número incrementado pelo minerador para tentar encontrar um hash válido |

Total:

👉 **80 bytes exatos**

👉 **A única parte realmente minerada**

👉 **A única entrada do cálculo de hash do bloco**

**Vendo o header “cru” (somente os 80 bytes)**

Para visualizar o header exatamente como ele é armazenado no bloco (sem metadados, sem interpretação, apenas o hex serializado) usamos (com `false` no fim):

```bash
bitcoin-cli -datadir="." getblockheader 00000008819873e925422c1ff0f99f7cc9bbb232af63a077a480a3633bee1ef6 false
0100000000000000000000000000000000000000000000000000000000000000000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a008f4d5fae77031e8ad22203
```

Explicando a saída (em hex):

```bash
01000000   ← version (4 bytes, little-endian → versão 1)
0000000000000000000000000000000000000000000000000000000000000000   ← previousblockhash (32 bytes)
000000003ba3edfd7a7b12b27ac72c3e67768f617fc81bc3888a51323a9fb8aa4b1e5e4a   ← merkleroot (32 bytes)
008f4d5f   ← time (4 bytes)
ae77031e   ← bits (4 bytes)
8ad22203   ← nonce (4 bytes)
```

Esse é o **header real** que os mineradores transformam em um hash válido ao competir pela prova de trabalho.

Se rodarmos sem o `false`:

```bash
bitcoin-cli -datadir="." getblockheader 00000008819873e925422c1ff0f99f7cc9bbb232af63a077a480a3633bee1ef6
{
  "hash": "00000008819873e925422c1ff0f99f7cc9bbb232af63a077a480a3633bee1ef6",
  "confirmations": 281914,
  "height": 0,
  "version": 1,
  "versionHex": "00000001",
  "merkleroot": "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
  "time": 1598918400,
  "mediantime": 1598918400,
  "nonce": 52613770,
  "bits": "1e0377ae",
  "target": "000000148b520000000000000000000000000000000000000000000000000000",
  "difficulty": 0.001126515290698186,
  "chainwork": "000000000000000000000000000000000000000000000000000000000049d414",
  "nTx": 1,
  "nextblockhash": "00000086d6b2636cb2a392d45edc4ec544a10024d30141c9adf4bfd9de533b53"
}
```

O Bitcoin Core devolve um **JSON enriquecido**, com campos que **não fazem parte do header.** 

Essas informações são calculadas pelo node a partir do estado da blockchain e da interpretação dos dados, mas **não pertencem aos 80 bytes do header** serializado.

### **Nonce, Target e Bits: o coração da Prova de Trabalho**

O Bitcoin não pede que mineradores encontrem um número mágico.

Ele pede que encontrem **um hash abaixo de um alvo (target)**.

O processo é simples, mas computacionalmente difícil:

```bash
1. pegar o header
2. calcular SHA256d(header)
3. comparar o resultado com o target
4. se não for menor… incrementar nonce e tentar novamente
5. se o nonce estourar, modificar outros campos (ex: timestamp ou coinbase)
```

Vendo os dados do exemplo anterior:

```bash
bitcoin-cli -datadir="." getblockheader 00000008819873e925422c1ff0f99f7cc9bbb232af63a077a480a3633bee1ef6
{
...
  "bits": "1e0377ae",
  "target": "000000148b520000000000000000000000000000000000000000000000000000",
  "difficulty": 0.001126515290698186,
...
}
```

O campo `bits` do header **não é o alvo diretamente.** Ele é uma **codificação compactada** do target:

```bash
1 byte   = expoente
3 bytes  = mantissa

target = mantissa × 256^(expoente − 3)
```

Já a dificuldade é definida como:

```bash
dificuldade = target_original / target_atual
```

Onde:

- `target_original` é o target do bloco gênese (o mais “fácil” possível).
- `target_atual` vem do campo `bits`.

**Resumindo…**

O campo `bits` no header define, de forma compactada, o alvo de prova de trabalho.

Ao expandi-lo, obtemos o `target`, que é o limite numérico que o hash do bloco precisa ser menor. A dificuldade reportada pelo Bitcoin Core (`bitcoin-cli getdifficulty`) é simplesmente a razão entre o alvo original (bloco gênese) e o alvo atual. Quanto menor o target, maior a dificuldade e mais trabalho computacional é necessário para encontrar um nonce válido.

### Por que minerar é encontrar um hash válido

A mineração não escolhe um hash.

Ela **gera** um hash ao processar os dados do bloco.

Esse hash deve cumprir:

```bash
SHA256(SHA256(header)) < target
```

A função SHA-256 é **determinística**, porém **imprevisível**: pequenas mudanças no header (ex.: incrementar o nonce) produzem resultados totalmente diferentes.

Isso faz com que:

- **não exista estratégia melhor** do que tentar combinações;
- mineradores testem **bilhões de nonces por segundo**;
- se o nonce de 32 bits se esgotar, modificam:
    - o timestamp, ou
    - a coinbase (que altera o merkle root), gerando um novo header e recomeçando o processo.

---

Ao encontrar um hash que fica abaixo do target, o minerador:

1. **anuncia o bloco** ao resto da rede;
2. os nodes verificam:
    - validade do PoW,
    - transações,
    - tamanho do bloco,
    - regras de consenso;
3. se tudo estiver correto, o bloco é **aceito na cadeia mais difícil**;
4. o minerador recebe:
    - **subsidio de bloco (block reward)**
    - **+ todas as taxas de transação (fees)**.

---

A Prova de Trabalho oferece três propriedades fundamentais:

- **Custo para produzir blocos** (não dá para falsificar trabalho).
- **Dificuldade ajustável** (mantém média de ~10 min/bloco).
- **Segurança cumulativa** (a cadeia mais difícil é a mais cara de ser superada).

### Construção dos blocos

Até agora entendemos:

- como o header é estruturado,
- como seu hash é calculado,
- e como a Prova de Trabalho depende de encontrar um hash abaixo do target.

Mas ainda falta uma pergunta essencial:

**Como, exatamente, um minerador constrói esse header que ele vai tentar hashear bilhões de vezes?**

Para isso existe um comando no Bitcoin Core: `getblocktemplate`.

Ele revela:

- quais transações estão disponíveis para serem incluídas no bloco,
- qual é o `bits` (e portanto o target) a ser usado,
- quais regras de consenso estão ativas,
- e qual é o esqueleto do bloco que o minerador deve montar.

O block template é o ponto de partida da mineração. Veremos como funciona a mineração no próximo artigo.

---

Neste artigo vimos como funcionam os blocos no Bitcoin e entendemos seus elementos fundamentais: o header de 80 bytes, o encadeamento via `previousblockhash`, o `merkleroot`, a codificação compactada do alvo (`bits`), o cálculo do `target` e o processo probabilístico da Prova de Trabalho baseado em `SHA256d(header)`.

Todo esse mecanismo existe por uma razão simples: **garantir que a cadeia mais difícil de produzir seja também a mais cara de ser atacada**. A segurança do Bitcoin nasce dessa combinação entre estrutura, hash, dificuldade e validação independente.

No próximo artigo, vamos transformar essa teoria em prática: vamos **minerar blocos**, observar o crescimento da blockchain localmente, receber o reward da coinbase e entender, passo a passo, como o Bitcoin Core monta e aceita blocos na *regtest*. Essa será a ponte natural para compreender a mineração por dentro, vendo a blockchain surgir e controlando cada detalhe com o `bitcoin-cli`.

Escrito por:  

Rafael Santos
