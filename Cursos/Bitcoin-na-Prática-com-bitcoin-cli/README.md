# 🧰 Curso — Bitcoin na Prática com `bitcoin-cli`

> Um curso introdutório–fundamental para aprender Bitcoin **interagindo diretamente com um node**, usando o `bitcoin-cli` como ferramenta principal para explorar o protocolo, o Bitcoin Core e seus estados internos.

---

## 🧠 Visão Geral

O **Bitcoin na Prática com `bitcoin-cli`** é um curso técnico focado em **aprendizado ativo**:  
nada de abstrações gráficas ou carteiras mágicas.

Aqui, você aprende Bitcoin **falando diretamente com o node**, entendendo como cada comando reflete estruturas reais do protocolo e do Bitcoin Core.

O curso serve como:

* porta de entrada para o ecossistema técnico do Bitcoin
* base prática para cursos mais avançados (wallets, transações, scripts, mineração)
* guia mental para entender o que um node *realmente faz*

---

## 🎯 Objetivo do Curso

Ao final do curso, você será capaz de:

* operar um node Bitcoin local
* entender as diferenças entre as redes Bitcoin
* usar o `bitcoin-cli` com confiança
* interpretar UTXOs, endereços e estados do node
* criar um modelo mental correto do funcionamento do Bitcoin Core

---

## 🧩 Estrutura do Curso

O curso é dividido em **artigos progressivos**, cada um focado em um aspecto essencial da prática com o Bitcoin Core.

Os artigos são independentes, mas juntos constroem uma base sólida para todo o restante do ecossistema técnico.

---

## [🖥️ Artigo 1 — Nó Bitcoin com Bitcoin Core  
### Instalação, `bitcoind` e `bitcoin-cli` (primeiros passos)](./Nós Bitcoin.md)

**Resumo:**  
Neste artigo, você aprende a instalar e rodar um node Bitcoin com o Bitcoin Core, entendendo a separação entre o daemon (`bitcoind`) e a interface de controle (`bitcoin-cli`).  
O foco está em criar o primeiro contato prático com o node e seus comandos básicos.

**Você aprende:**

* O que é um node Bitcoin e por que rodar um
* Diferença entre `bitcoind` e `bitcoin-cli`
* Papel do `bitcoin-cli`
* Primeiros comandos RPC

**Comandos explorados:**

* `bitcoin-cli help`
* `getblockchaininfo`
* `getnetworkinfo`

---

## 🌐 Artigo 2 — Mainnet, Testnet, Signet e Regtest  
### O universo das redes Bitcoin

**Resumo:**  
Bitcoin não é uma rede única.  
Aqui você explora as diferentes redes disponíveis no Bitcoin Core, entendendo **quando e por que usar cada uma**, além de como alternar entre elas na prática.

**Você aprende:**

* Diferença entre Mainnet, Testnet, Signet e Regtest
* Casos de uso de cada rede
* Como iniciar o node em cada modo
* Impacto das redes nos dados e estados do node

**Comandos explorados:**

* `getblockchaininfo`
* flags de inicialização (`-testnet`, `-signet`, `-regtest`)

---

## 🔑 Artigo 3 — Como funciona uma carteira no Bitcoin Core  
### Chaves, endereços e UTXOs

**Resumo:**  
Este artigo desmonta o conceito de “carteira” no Bitcoin Core.  
Você aprende que uma wallet não guarda bitcoins, mas **chaves**, **scripts** e **referências a UTXOs**, todas gerenciadas pelo node.

**Você aprende:**

* O que realmente é uma wallet no Bitcoin
* Relação entre chaves privadas, públicas e endereços
* O papel dos UTXOs
* Como o Bitcoin Core rastreia fundos
* Diferença entre saldo confirmado e não confirmado

**Comandos explorados:**

* `getnewaddress`
* `listunspent`
* `getbalances`

---

## 🧾 Artigo 4 — Explorando os tipos de endereços no Bitcoin Core (Parte 1)  
### Legacy

**Resumo:**  
Neste artigo, você começa a explorar os **tipos de endereços Bitcoin**, começando pelos endereços Legacy (P2PKH).  
O foco está em entender como endereços se relacionam com scripts e regras de validação.

**Você aprende:**

* O que são endereços Legacy
* Como funcionam endereços P2PKH
* Relação entre endereço e `scriptPubKey`
* Por que existem diferentes formatos de endereços
* Implicações práticas de usar Legacy hoje

**Comandos explorados:**

* `getnewaddress "label" legacy`
* `getaddressinfo`

---

## 🧱 Como Usar Este Curso

Você pode usar este curso para:

* aprender Bitcoin do zero, de forma prática
* preparar o terreno para cursos avançados
* testar comandos e hipóteses em regtest ou signet
* construir intuição sobre o funcionamento do Bitcoin Core

Cada artigo pode ser lido isoladamente, mas o **maior ganho vem da prática contínua**.

---

© 2025 Bitcoin Coders — conteúdo técnico, prático e aberto.
