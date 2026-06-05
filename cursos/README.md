# 📚 Cursos — Bitcoin Coders

> Conteúdo técnico e modular para dominar o Bitcoin **na prática**, operando nodes, explorando o Bitcoin Core e ferramentas do ecossistema e entendendo o protocolo em profundidade.

---

## 🧠 Visão Geral

Os **Cursos do Bitcoin Coders** são módulos técnicos **autocontidos**, focados em subsistemas reais do Bitcoin.

Cada curso aprofunda um aspecto específico de fundamentos de programação, do protocolo, do Bitcoin Core ou de ferramentas do ecossistema, sempre com:

* uso intenso de **bitcoin-cli**, **RPC**, **APIs** e **SDKs** 
* experimentação em **regtest, signet e testnet**
* foco em **como o Bitcoin funciona de verdade**, não apenas na teoria

Os cursos podem ser feitos **independentemente**, mas foram pensados para se conectar conceitualmente.

---

## 🧩 [Curso 0 — Bitcoin na Prática com bitcoin-cli](https://bitcoincoders.org/curso/bitcoin-cli/)

[**Link para o curso**](https://bitcoincoders.org/curso/bitcoin-cli/)

**Resumo:**
Domine o funcionamento interno do Bitcoin explorando seus principais subsistemas diretamente no Bitcoin Core usando o bitcoin-cli.

**O que você aprende:**

* Como instalar, configurar e operar um node Bitcoin com Bitcoin Core
* Diferença entre mainnet, testnet, signet e regtest e quando usar cada uma
* Como funcionam carteiras, chaves, endereços e o modelo UTXO
* Tipos de endereços (Legacy, SegWit e Taproot) e suas diferenças práticas
* Como explorar, criar, assinar e transmitir transações manualmente
* Funcionamento de taxas, mempool e estratégias de confirmação (RBF, CPFP)
* Uso de PSBT, multisig e timelocks para segurança avançada
* Fundamentos de Bitcoin Script e validação de transações
* Como funcionam assinaturas digitais (ECDSA e Schnorr)
* Estrutura de blocos e processo de mineração na prática
* Comunicação P2P entre nodes e propagação de dados
* Validação, chainstate, políticas e comportamento real do node

---

## 🧩 [Curso 1 — Dominando as Carteiras no Bitcoin Core](https://bitcoincoders.org/curso/carteiras-bitcoin-core/)

[**Link para o curso**](https://bitcoincoders.org/curso/carteiras-bitcoin-core/)

**Resumo:**
Entenda como o Bitcoin Core gerencia fundos internamente, da criação de chaves ao controle de UTXOs. O curso mostra como wallets realmente funcionam dentro do node, indo além de abstrações de aplicativos gráficos.

**O que você aprende:**

* Arquitetura de wallets no Bitcoin Core
* `wallet.dat`, HD Wallets e Descriptor Wallets
* Geração e gerenciamento de chaves
* Tipos de endereços: Legacy, SegWit e Taproot
* Relação entre endereços, scripts e UTXOs

**Comandos e ferramentas:**

* `getnewaddress`
* `listunspent`
* `listdescriptors`
* `getwalletinfo`

---

## ⚡ [Curso 2 — Transações no Bitcoin Core e Signet](https://bitcoincoders.org/curso/transacoes-bitcoin-core/)

[**Link para o curso**](https://bitcoincoders.org/curso/transacoes-bitcoin-core/)

**Resumo:**
Aprenda a criar, analisar e enviar transações manualmente, entendendo como taxas, mempool e políticas do node afetam cada confirmação. Todo o curso é feito em **Signet**, permitindo testes realistas sem risco financeiro.

**O que você aprende:**

* Estrutura completa de uma transação Bitcoin
* Criação de transações brutas
* Cálculo e ajuste de taxas
* Funcionamento do mempool
* RBF (Replace-By-Fee) e CPFP
* PSBT, multisig e timelocks

**Comandos e ferramentas:**

* `createrawtransaction`
* `fundrawtransaction`
* `signrawtransactionwithwallet`
* `sendrawtransaction`

---

## 🧠 [Curso 3 — Scripts: Como o Bitcoin Executa Suas Regras](https://bitcoincoders.org/curso/scripts-bitcoin/)

[**Link para o curso**](https://bitcoincoders.org/curso/scripts-bitcoin/)

**Resumo:**
Descubra como o Bitcoin valida gastos usando **Bitcoin Script**. O curso explora a máquina de pilha, os opcodes e como scripts determinam quem pode gastar, quando e sob quais condições.

**O que você aprende:**

* Diferença entre `scriptPubKey` e `scriptSig`
* Máquina de pilha e modelo de execução
* Opcodes essenciais do Bitcoin
* Scripts condicionais
* Multisig e timelocks
* Como scripts se transformam em endereços

**Comandos e ferramentas:**

* `decodescript`
* `decoderawtransaction`
* `bitcoin-cli` em regtest e signet

---

## 🔐 [Curso 4 — Assinaturas Digitais no Bitcoin](https://bitcoincoders.org/curso/assinaturas-digitais-no-bitcoin/)

[**Link para o curso**](https://bitcoincoders.org/curso/assinaturas-digitais-no-bitcoin/)

**Resumo:**
Entenda como o Bitcoin prova a autorização de um gasto. Do ECDSA ao Schnorr, o curso mostra como assinaturas aparecem nas transações e como o protocolo evita maleabilidade.

**O que você aprende:**

* Assinaturas ECDSA (r, s)
* Formato DER e regra low-S
* Maleabilidade e suas implicações
* Papel do SIGHASH
* Assinaturas Schnorr e Taproot
* Witness e indistinguibilidade de transações

---

## ⛓️ [Curso 5 — Núcleo do Bitcoin: Blocos, Mineração, Propagação e Validação](https://bitcoincoders.org/curso/nucleo-do-bitcoin/)
[**Link para o curso**](https://bitcoincoders.org/curso/nucleo-do-bitcoin/)

**Resumo:**  
Entenda como o Bitcoin realmente funciona a partir do ponto de vista do node.  
Neste curso, você acompanha o ciclo completo de um bloco: como ele é montado, minerado, propagado na rede P2P e validado localmente. O foco está nas regras de consenso, no chainstate e nas políticas que definem o que um node aceita e retransmite, tudo explorado diretamente no Bitcoin Core.

**O que você aprende:**

Estrutura completa de um bloco Bitcoin
Cabeçalho do bloco: hash, nonce, target e difficulty
Como funciona a Proof of Work na prática
Mineração de blocos em regtest
Propagação de blocos e transações na rede P2P
Processo de validação de blocos pelo node
Chainstate, UTXO set e manutenção de estado
Forks, reorgs e pontas da blockchain
Diferença entre regras de consenso e políticas locais

**Comandos e ferramentas:**

* `getblockhash`
* `getblock`
* `getblockheader`
* `getdifficulty`
* `getchaintips`
* `getblocktemplate`
* `bitcoin-cli` em regtest e signet

**Códigos Utilizados:**

[miner_regtest.py](../assets/miner_regtest.py)

---
## ⛓️ [Curso 6 — Mineração além do nonce: escolhas, incentivos e paralelismo](https://bitcoincoders.org/curso/mineracao-alem-do-nonce/)
[**Link para o curso**](https://bitcoincoders.org/curso/mineracao-alem-do-nonce/)

**Resumo:**  
Mineração não é só “tentar nonces”. Antes de qualquer hash, um minerador precisa decidir quais transações entram no bloco, lidando com incentivos, taxas e dependências na mempool.
Neste Bitup, a gente percorre o fluxo completo: seleção econômica de transações → montagem de um bloco candidato real (via getblocktemplate) → Proof of Work → experimento 1 núcleo vs múltiplos núcleos, fechando com a intuição de por que isso naturalmente empurra o ecossistema para especialização (ASIC).

**O que você aprende:**

* Como um minerador escolhe transações na mempool: taxas, feerate e pacotes (pai/filho)
* Como obter um template real com getblocktemplate e transformar em bloco candidato
* Como montar coinbase, merkle root e header antes do PoW
* Como minerar “na mão” e submeter com submitblock, validando no getblockchaininfo
* Por que mineração é paralelizável (1 core vs multi-core)
* Por que isso leva a ASIC: força bruta paralela + função fixa + incentivo econômico

**Comandos e ferramentas:**

* `getnewaddress`
* `sendtoaddress`
* `createrawtransaction`
* `fundrawtransaction`
* `signrawtransactionwithwallet`
* `sendrawtransaction`
* `getrawmempool`
* `getmempoolentry`
* `submitblock`
* `getblocktemplate`
* `bitcoin-cli` em regtest

**Códigos Utilizados:**

[miner_regtest2.py](../assets/miner_regtest2.py)

[miner_multi.py](../assets/miner_multi.py)

---
## ⛓️ [Curso 7 — Bitcoin vs Computação Quântica: mito, risco e realidade](https://bitcoincoders.org/curso/bitcoin-vs-computacao-quantica/)
[**Link para o curso**](https://bitcoincoders.org/curso/bitcoin-vs-computacao-quantica/)

**Resumo:**  

Computação quântica não é ficção científica, mas também não é um botão mágico que “quebra o Bitcoin” da noite para o dia. Neste Bitup você vai entender, de forma técnica e realista, o que os algoritmos quânticos realmente fazem, quais partes do Bitcoin poderiam ser afetadas, quais cenários de risco são plausíveis e como o protocolo já está se preparando com conservadorismo e engenharia responsável.

**O que você aprende:**

* O que é fatoração e logaritmo discreto e por que isso importa para o Bitcoin
* Como funciona o algoritmo de Shor e por que ele ameaça ECDSA e Schnorr
* Como funciona o algoritmo de Grover e qual seu impacto real sobre hashes e mineração
* A diferença entre risco teórico e risco prático
* Por que o mito de “quebrar tudo de uma vez” não reflete a realidade técnica
* Como reutilização de endereço pode aumentar risco em cenários futuros
* O que acontece na janela entre mempool e confirmação
* Como a mineração se ajusta mesmo diante de vantagem tecnológica
* O estado atual da engenharia no Bitcoin (BIP 360, commit-and-reveal, assinaturas pós-quânticas, híbridos e agregação)
* Onde estamos hoje em hardware quântico (qubits físicos vs qubits lógicos) e o quão distante isso está de um ataque prático

---
## ⛓️ [Curso 8 — Quem manda no Bitcoin? consenso, regras e forks](https://bitcoincoders.org/curso/quem-manda-no-bitcoin/)
[**Link para o curso**](https://bitcoincoders.org/curso/quem-manda-no-bitcoin/)

**Resumo:**  

O Bitcoin não tem controle central . Mineradores produzem blocos, desenvolvedores escrevem código, nodes trocam dados e usuários escolhem o software que rodam, mas ninguém manda sozinho. Neste Bitup, você vai entender de forma técnica e prática como o Bitcoin realmente toma decisões: o que são regras de consenso, por que consenso não é votação, como forks surgem e por que divergências não “quebram” a rede, mas revelam como ela funciona de verdade.

**O que você aprende:**

* Por que a pergunta “quem manda no Bitcoin?” está errada desde o começo
* O que são regras de consenso e por que cada node valida tudo de forma independente
* Por que mineradores não conseguem impor blocos inválidos ao resto da rede
* Por que desenvolvedores não conseguem “forçar atualização”
* O papel real de nodes, mineradores, desenvolvedores e usuários no funcionamento do sistema
* O que significa dizer que consenso é convergência de regras
* O que é um fork “natural” e por que ele pode acontecer mesmo com todos seguindo as mesmas regras
* O que é um fork “de regra” e como ele surge quando nodes passam a discordar sobre validade
* A diferença entre soft fork e hard fork
* Como criar, em regtest, um fork natural entre dois nodes
* Como alterar uma regra do Bitcoin Core, recompilar e demonstrar um fork estrutural na prática

---
## ⛓️ [Curso 9 — Privacidade no Bitcoin: o que um node realmente sabe sobre você](https://bitcoincoders.org/curso/privacidade-no-bitcoin/)
[**Link para o curso**](https://bitcoincoders.org/curso/privacidade-no-bitcoin/)

**Resumo:**  

O Bitcoin não é anônimo. Ele foi projetado para ser transparente e verificável, não para esconder dados. Cada transação revela inputs, outputs, valores e relações entre UTXOs, informações suficientes para identificar padrões, inferir comportamentos e conectar atividades. Neste Bitup, você vai ver na prática como a privacidade no Bitcoin realmente funciona: o que um node enxerga, como heurísticas simples permitem rastreamento e por que decisões aparentemente pequenas, como reutilizar um endereço ou misturar UTXOs, podem comprometer completamente sua privacidade.

**O que você aprende:**

* Por que a ideia de que “Bitcoin é anônimo” está errada
* O que significa dizer que o Bitcoin é pseudônimo e não anônimo
* O que um node realmente enxerga ao validar a blockchain (inputs, outputs, valores e histórico)
* Como a estrutura das transações permite identificar padrões e inferir relações
* Por que reutilização de endereço reduz drasticamente a privacidade
* Como funciona o troco (change) e por que ele é uma das principais pistas de rastreamento
* Por que múltiplos inputs na mesma transação sugerem controle pela mesma entidade (heurística)
* O que acontece ao misturar UTXOs de origem KYC com não-KYC
* Como rastrear manualmente transações e seguir UTXOs usando bitcoin-cli
* Por que privacidade no Bitcoin não é padrão, é comportamento
* Como estruturar melhor o uso de carteiras para reduzir vazamento de informação

---
## 🧱 Como Usar os Cursos

Você pode:

* estudar um curso isoladamente
* combinar cursos conforme seu interesse
* usar os cursos como base para os **Programas** (como o CoreCraft)

Cada curso possui:

* materiais teóricos
* exemplos práticos
* scripts e laboratórios

---


© 2025 Bitcoin Coders — cursos técnicos, código aberto.
