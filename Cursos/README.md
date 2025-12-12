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

## 🧩 Curso 1 — Dominando as Carteiras no Bitcoin Core

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

## ⚡ Curso 2 — Transações no Bitcoin Core e Signet

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

## 🧠 Curso 3 — Scripts: Como o Bitcoin Executa Suas Regras

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
* bitcoin-cli em regtest e signet

---

## 🔐 Curso 4 — Assinaturas Digitais no Bitcoin

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

## 🧱 Como Usar os Cursos

Você pode:

* estudar um curso isoladamente
* combinar cursos conforme seu interesse
* usar os cursos como base para os **Programas** (como o CoreCraft)

Cada curso possui sua própria pasta com:

* materiais teóricos
* exemplos práticos
* scripts e laboratórios

---

## 🧭 Filosofia dos Cursos

> Aqui você não aprende apenas *o que* o Bitcoin faz,
> mas *como* ele faz — e *por que* foi projetado assim.

---

© 2025 Bitcoin Coders — cursos técnicos, código aberto.
