# 📖 Artigos — Bitcoin Coders

> Explorações técnicas sobre o funcionamento do Bitcoin utilizando **Bitcoin Core**, **bitcoin-cli** e experimentos práticos em redes de teste.

---

# 🧠 Visão Geral

A seção **Artigos do Bitcoin Coders** reúne textos técnicos que exploram o funcionamento do Bitcoin **na prática**, utilizando diretamente o **Bitcoin Core**.

Os artigos combinam:

- experimentos com **bitcoin-cli**
- análise de **transações e UTXOs**
- exploração de **carteiras e endereços**
- testes em **signet, testnet e regtest**

O objetivo é permitir que desenvolvedores entendam o protocolo **operando um node real**, observando como o Bitcoin funciona de dentro para fora.

---

# ⚙️ Série — Bitcoin na Prática com Bitcoin-cli

Uma série de artigos progressivos que exploram os fundamentos do Bitcoin utilizando diretamente o **Bitcoin-cli** e sua interface de linha de comando.

---

## 🧱 Nó Bitcoin com Bitcoin Core: instalação, bitcoind e bitcoin-cli (primeiros passos)

[**Acesse o artigo aqui**](./artigo01-no-bitcoin.md)

**Resumo**

Introdução ao Bitcoin Core e ao funcionamento de um node Bitcoin. O artigo mostra como instalar o software, iniciar o daemon `bitcoind` e interagir com o node usando `bitcoin-cli`.

**O que você aprende**

- O que é um node Bitcoin
- Diferença entre Bitcoin Core e outras implementações
- Instalação do Bitcoin Core
- Uso do `bitcoind`
- Primeiros comandos com `bitcoin-cli`

---

## 🌐 Mainnet, Testnet, Signet e Regtest: o universo das redes Bitcoin

[**Acesse o artigo aqui**](./artigo02-redes-bitcoin.md)

**Resumo**

Explora as diferentes redes do ecossistema Bitcoin e suas aplicações para desenvolvimento, testes e experimentação.

**O que você aprende**

- Diferença entre **mainnet, testnet, signet e regtest**
- Quando usar cada rede
- Como iniciar um node em cada ambiente
- Vantagens da **signet para experimentação**

---

## 💼 Como funciona uma carteira no Bitcoin Core: chaves, endereços e UTXOs

[**Acesse o artigo aqui**](./artigo03-carteira-bitcoin.md)

**Resumo**

Explora como o Bitcoin Core gerencia fundos internamente, mostrando como chaves, endereços e UTXOs se relacionam dentro de uma carteira.

**O que você aprende**

- Estrutura de uma carteira Bitcoin
- Relação entre **chaves privadas, chaves públicas e endereços**
- Modelo **UTXO**
- Como o Bitcoin Core rastreia saldos

---

## 🧾 Explorando os tipos de endereços no Bitcoin Core (Parte 1): Legacy

[**Acesse o artigo aqui**](./artigo04-endereços-bitcoin.md)

**Resumo**

Analisa os primeiros formatos de endereços utilizados no Bitcoin e como eles aparecem na prática dentro do Bitcoin Core.

**O que você aprende**

- Endereços **Legacy (P2PKH)**
- Estrutura Base58
- Scripts associados aos endereços
- Compatibilidade com nodes e carteiras

---

## 🔑 HD Wallets e Descriptor Wallets: a evolução da geração de endereços das carteiras do Bitcoin Core

[**Acesse o artigo aqui**](./artigo05-HD-Wallets.md)

**Resumo**

Explora a evolução das carteiras no Bitcoin Core, da geração simples de chaves até o modelo moderno baseado em **descriptors**.

**O que você aprende**

- HD Wallets e derivação de chaves
- Seeds e árvores de derivação
- Descriptor Wallets
- Como o Bitcoin Core gerencia endereços modernos

---

## ⚡ SegWit: teoria e prática na Signet

[**Acesse o artigo aqui**](./artigo06-segwit.md)

**Resumo**

Introduz o SegWit e mostra como ele altera a estrutura das transações, além de demonstrar sua utilização em uma rede de teste.

**O que você aprende**

- O que é **Segregated Witness**
- Estrutura de transações SegWit
- Witness e weight
- Benefícios do SegWit
- Experimentos em **signet**

---

## 🔎 Explorando Transações no Bitcoin Core

[**Acesse o artigo aqui**](./artigo07-explorando-transações.md)

**Resumo**

Analisa a estrutura de uma transação Bitcoin e como ela pode ser observada diretamente pelo node.

**O que você aprende**

- Estrutura de uma transação
- Inputs e outputs
- Scripts envolvidos
- Relação com o modelo UTXO

---

## 🧪 Construindo Transações no Bitcoin Core

[**Acesse o artigo aqui**](./artigo08-construindo-transações.md)

**Resumo**

Mostra como criar transações manualmente usando o Bitcoin Core, permitindo controle detalhado sobre inputs, outputs e taxas.

**O que você aprende**

- Criação de **transações brutas**
- Uso de `createrawtransaction`
- Assinatura de transações
- Envio manual de transações

---

## 💰 Taxas, Mempool e Estratégias de Confirmação

[**Acesse o artigo aqui**](./artigo09-taxas-mempool.md)

**Resumo**

Explora o papel das taxas no Bitcoin e como a mempool influencia o tempo de confirmação das transações.

**O que você aprende**

- Como as taxas são calculadas
- Funcionamento da **mempool**
- Estratégias de confirmação
- RBF e CPFP

---

## 🔐 Transferências Avançadas e Segurança

[**Acesse o artigo aqui**](./artigo10-transferências-avançadas.md)

**Resumo**

Explora mecanismos avançados de segurança e controle de gastos no Bitcoin. O artigo apresenta ferramentas que permitem construir transações mais seguras e flexíveis, incluindo **PSBT**, **multisig** e **timelocks**, mostrando como esses recursos são usados para coordenação entre múltiplos participantes, proteção de fundos e criação de políticas de gasto mais sofisticadas.

**O que você aprende**

- O que são **PSBTs (Partially Signed Bitcoin Transactions)** e quando utilizá-las
- Como funciona o modelo **multisig** e suas aplicações em segurança
- Diferença entre assinaturas parciais e finais em transações
- Como funcionam **timelocks** (`CLTV` e `CSV`)
- Como essas ferramentas permitem criar políticas de gasto mais seguras

---

## 🔐 Introdução a Scripts e Assinaturas

[**Acesse o artigo aqui**](./artigo11-Introducao-a-Scripts-e-Assinaturas.md)

**Resumo**

Apresenta os fundamentos que permitem ao Bitcoin verificar quem está autorizado a gastar fundos. O artigo introduz o **Bitcoin Script**, explica o papel das **chaves públicas e privadas**, e mostra como as **assinaturas digitais** são usadas para provar a autorização de uma transação. Ao final, um exemplo prático com **bitcoin-cli** demonstra como esses elementos aparecem na validação real de uma transação.

**O que você aprende**

- O que é o **Bitcoin Script** e qual seu papel nas regras de gasto
- Como funcionam **chaves privadas e chaves públicas** no Bitcoin
- Como as **assinaturas digitais** provam a autorização de uma transação
- Como o node valida uma transação utilizando scripts e assinaturas
- Como observar esses elementos na prática usando **bitcoin-cli**

---
  
# 🧭 Como Usar os Artigos

Você pode:

- ler artigos individualmente
- acompanhar a série completa **Bitcoin na Prática com Bitcoin Core**
- usar os artigos como material complementar para os **Cursos**

Os artigos incluem:

- comandos completos com **bitcoin-cli**
- experimentos em **signet e regtest**
- análise de dados reais do node

---

© 2026 Bitcoin Coders — artigos técnicos open source sobre Bitcoin.
