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

[**Acesse o artigo aqui**](./artigo11-Introdução-a-Scripts-e-Assinaturas.md)

**Resumo**

Apresenta os fundamentos que permitem ao Bitcoin verificar quem está autorizado a gastar fundos. O artigo introduz o **Bitcoin Script**, explica o papel das **chaves públicas e privadas**, e mostra como as **assinaturas digitais** são usadas para provar a autorização de uma transação. Ao final, um exemplo prático com **bitcoin-cli** demonstra como esses elementos aparecem na validação real de uma transação.

**O que você aprende**

- O que é o **Bitcoin Script** e qual seu papel nas regras de gasto
- Como funcionam **chaves privadas e chaves públicas** no Bitcoin
- Como as **assinaturas digitais** provam a autorização de uma transação
- Como o node valida uma transação utilizando scripts e assinaturas
- Como observar esses elementos na prática usando **bitcoin-cli**

---

## ⚙️ Bitcoin Script: Máquina de Execução e Pilha

[**Acesse o artigo aqui**](./artigo12-Bitcoin-Script.md)

**Resumo**

Explora como o Bitcoin realmente executa scripts durante a validação de uma transação. O artigo apresenta a **máquina de execução do Bitcoin Script**, explicando como a pilha é utilizada para processar dados e opcodes. A partir da anatomia da pilha principal e da pilha alternativa, você acompanha como as operações são avaliadas passo a passo e como diferentes instruções transformam o estado da execução. Ao final, exemplos em **simuladores de script** ajudam a visualizar o comportamento real dos scripts.

**O que você aprende**

- Como funciona a **máquina de execução do Bitcoin Script**
- A estrutura da **pilha principal**
- Como os **opcodes** manipulam dados e controlam o fluxo de execução
- Como os scripts são avaliados durante a validação de transações
- Como explorar e testar scripts usando **simuladores de Bitcoin Script**

---

## 🔐 Scripts Condicionais e Contratos Base

[**Acesse o artigo aqui**](./artigo13-Scripts-Condicionais-e-Contratos-Base.md)

**Resumo**

Explora como o Bitcoin permite construir regras de gasto mais sofisticadas utilizando **Bitcoin Script**. O artigo mostra como a pilha pode representar diferentes condições de validação, introduzindo estruturas como **multisig**, **timelocks** e fluxos condicionais. A partir disso, você entende como o Bitcoin implementa contratos básicos sem estado, incluindo exemplos como **scripts duais**, onde múltiplos caminhos de gasto são possíveis dependendo das condições atendidas.

**O que você aprende**

- Como a **pilha representa regras de gasto** no Bitcoin Script
- Como funciona o **multisig** com `OP_CHECKMULTISIG`
- O que são **timelocks** e como restringem o gasto no tempo
- Uso de `OP_CHECKLOCKTIMEVERIFY (CLTV)` para bloqueio de transações
- Estruturas condicionais com `OP_IF`, `OP_ELSE` e `OP_ENDIF`
- Como construir **scripts duais** com múltiplos caminhos de validação

---

## 🔑 Como os Scripts se transformam em Endereços no Bitcoin

[**Acesse o artigo aqui**](./artigo14-Como-os-Scripts-se-transformam-em-Endereços-no-Bitcoin.md)

**Resumo**

Explica como os endereços Bitcoin são derivados de scripts e representam, na prática, **condições de gasto**. O artigo percorre o caminho completo: da definição do “cadeado” (a regra de gasto), passando pela construção do `scriptPubKey`, até o processo de “envelopar” esse script em um endereço. Também mostra como decodificar um endereço para entender qual script ele representa, finalizando com um exemplo prático no **Bitcoin Core**.

**O que você aprende**

- Como definir a **condição de gasto** (o “cadeado”) de um script
- Como o `scriptPubKey` representa essa condição em código
- Como scripts são **convertidos em endereços** (Base58, Bech32)
- Como **interpretar e decodificar** um endereço Bitcoin
- Como observar todo esse processo na prática usando **bitcoin-cli**

---

## 🔐 Assinaturas no Bitcoin: o elo entre posse e gasto

[**Acesse o artigo aqui**](./artigo15-Assinaturas-no-Bitcoin.md)

**Resumo**

Explica como as assinaturas digitais conectam a posse de uma chave à autorização de gasto no Bitcoin. O artigo mostra onde a assinatura aparece dentro de uma transação, como ocorre o ciclo completo de validação e o que exatamente é assinado durante esse processo. Ao final, exemplos práticos com **bitcoin-cli** permitem observar essas estruturas diretamente no funcionamento real do node.

**O que você aprende**

- Onde a **assinatura digital aparece** na estrutura de uma transação
- Como funciona o **ciclo de validação** no Bitcoin
- O que é **efetivamente assinado** (SIGHASH e partes da transação)
- Como o node verifica a autorização de gasto
- Como explorar assinaturas na prática usando **bitcoin-cli**

---

## 🔐 ECDSA no Bitcoin: anatomia da assinatura

[**Acesse o artigo aqui**](./artigo16-ECDSA-no-Bitcoin.md)

**Resumo**

Explora em profundidade como funcionam as assinaturas digitais no Bitcoin a partir do algoritmo **ECDSA**. O artigo apresenta o propósito fundamental de uma assinatura, provar a posse de uma chave privada sem revelá-la, e explica como isso é possível usando criptografia de curva elíptica. A partir da curva **secp256k1**, você entende como o ECDSA gera e valida assinaturas, finalizando com um exemplo prático em **Python**.

**O que você aprende**

- O propósito de uma **assinatura digital** no Bitcoin
- Como funciona a curva elíptica **secp256k1**
- Como o algoritmo **ECDSA** gera e valida assinaturas
- Como a posse da chave privada é provada sem revelá-la
- Como implementar e observar assinaturas na prática com **Python**

---

## 🔐 O formato DER e o SIGHASH nas assinaturas Bitcoin

[**Acesse o artigo aqui**](./artigo17-formato-DER-e-SIGHASH.md)

**Resumo**

Explora como o Bitcoin padroniza e valida assinaturas digitais através do **formato DER** e do mecanismo de **SIGHASH**. O artigo mostra por que o uso de DER é essencial para garantir consistência e segurança, detalha a estrutura interna das assinaturas e explica como o Bitcoin calcula o **hash (preimage)** que será efetivamente assinado. Também aborda regras de consenso como **low-S** e finaliza com a análise de um **scriptSig real**, desmontando cada componente da assinatura.

**O que você aprende**

- Por que o Bitcoin utiliza o **formato DER** para assinaturas
- A **estrutura interna** de uma assinatura DER
- Como o Bitcoin constrói o **hash (preimage)** que será assinado
- O papel do **SIGHASH** na definição do que está sendo assinado
- Regras de consenso como **assinaturas canônicas (low-S)**
- Como analisar uma assinatura real a partir de um **scriptSig**

---

## 🔐 Schnorr e Taproot: a nova era das assinaturas

[**Acesse o artigo aqui**](./artigo18-Schnorr-e-Taproot.md)

**Resumo**

Explora a evolução das assinaturas no Bitcoin com a introdução do **Schnorr** e do **Taproot**. O artigo mostra por que o ECDSA possuía limitações e como o Schnorr (BIP340) traz simplicidade, eficiência e novas possibilidades. A partir disso, você entende como o Taproot unifica saídas, incorpora **MAST** para scripts mais eficientes e introduz o **Tapscript (BIP342)** como base para o futuro do protocolo. Ao final, um exemplo prático na **Signet** mostra como um gasto Taproot aparece no Bitcoin real.

**O que você aprende**

- Por que o Bitcoin evoluiu além do **ECDSA**
- O que muda com o **Schnorr (BIP340)**
- Como o **Taproot** unifica saídas (Pay-to-Pubkey)
- O papel do **MAST** (Merkle Abstract Syntax Tree)
- Como são estruturados o **scriptPubKey** e o **witness** no Taproot
- Como ocorre a **verificação de uma transação Taproot**
- O que é o **Tapscript (BIP342)** e por que ele é mais flexível
- Como um gasto Taproot aparece na prática (Signet)

---

## ⛓️ Blocos Bitcoin

[**Acesse o artigo aqui**](./artigo19-Blocos-Bitcoin.md)

**Resumo**

Apresenta a estrutura e o papel dos blocos no funcionamento do Bitcoin. O artigo explica o que é um bloco, como ele organiza transações e como é validado pelos nodes. A partir da análise do **header de 80 bytes**, você entende como funcionam elementos como **nonce, target e bits**, que sustentam a **Proof of Work**. Também mostra por que minerar é, na prática, encontrar um hash válido e como blocos são construídos antes de serem propagados pela rede, incluindo exemplos com **bitcoin-cli**.

**O que você aprende**

- O que é um **bloco Bitcoin** e qual seu papel na rede
- Como explorar blocos usando **bitcoin-cli**
- Estrutura completa do **block header (80 bytes)**
- Como funcionam **nonce, target e bits**
- Por que minerar é encontrar um **hash válido**
- Como ocorre a **construção de blocos** pelos mineradores

---

## ⛏️ Mineração na prática: minerando blocos na regtest com bitcoin-cli

[**Acesse o artigo aqui**](./artigo20-Mineração-na-prática.md)

**Resumo**

Mostra na prática como funciona o processo de mineração no Bitcoin utilizando o ambiente **regtest** e o **bitcoin-cli**. O artigo percorre todo o fluxo de construção de um bloco: desde a verificação do estado da blockchain, passando pela obtenção do template, montagem da **coinbase**, construção do header e execução da Proof of Work. Ao final, um minerador em **Python** demonstra como encontrar um hash válido e submeter o bloco com `submitblock`.

**O que você aprende**

- Como funciona a **mineração em regtest** com controle total do ambiente
- Como verificar o estado atual da blockchain via **bitcoin-cli**
- Como obter e interpretar o **getblocktemplate**
- Como construir uma **transação coinbase**
- Como montar o **header do bloco**
- Como implementar um minerador simples em **Python**
- Como enviar e validar um bloco com `submitblock`

---

## 🌐 P2P Bitcoin: como nodes conversam

[**Acesse o artigo aqui**](./artigo21-P2P-Bitcoin.md)

**Resumo**

Explora como os nodes Bitcoin se comunicam diretamente na rede **P2P**, sem intermediários. O artigo mostra que cada node atua simultaneamente como cliente, servidor, validador e retransmissor, e explica por que o **RPC não faz parte da rede Bitcoin**. A partir das mensagens do protocolo (`version`, `inv`, `tx`, `block`, etc.), você entende como dados são anunciados, solicitados e propagados em um grafo dinâmico de conexões. Também são apresentados exemplos práticos de conexão entre nodes e observação do tráfego real com ferramentas como **tcpdump**.

**O que você aprende**

- Os diferentes papéis de um **node Bitcoin** na rede
- Por que o **RPC não faz parte da rede P2P**
- Quais são as principais **mensagens do protocolo Bitcoin**
- Como funciona a **topologia dinâmica da rede**
- Por que a propagação ocorre por **anúncio (inv) e não envio direto**
- Como o modelo de **confiança zero** exige validação completa
- Como estabelecer **conexões P2P entre nodes**
- Como observar o tráfego real da rede com **tcpdump**

---

## ⚖️ Chainstate, validação e políticas

[**Acesse o artigo aqui**](artigo22-Chainstate-validação-e-políticas.md)

**Resumo**

Explora como o Bitcoin Core mantém o estado da blockchain e toma decisões sobre o que aceitar ou rejeitar. O artigo apresenta o **chainstate** como o estado vivo do sistema, explica como a **validação incremental** ocorre à medida que novos blocos e transações chegam e mostra como forks e reorgs são tratados. Também destaca o papel da **mempool** e da **policy layer**, evidenciando que nem toda transação válida pelo consenso é necessariamente aceita pelo node. Ao final, um experimento prático demonstra esse comportamento na prática.

**O que você aprende**

- O que é o **chainstate** e como ele representa o estado atual do Bitcoin
- Como funciona a **validação incremental** de blocos e transações
- Como verificar a **saúde da blockchain** com bitcoin-cli
- O que são **forks, reorgs e pontas da chain**
- O papel da **mempool** no fluxo das transações
- Diferença entre **regras de consenso e políticas locais (policy)**
- Por que uma transação válida pode ser **rejeitada pelo node**
- Como observar esse comportamento em um **experimento prático**

---

## 🚀 Bitcoin Core v31 na prática: o que mudou (com bitcoin-cli)

[**Acesse o artigo aqui**](./artigos/artigo23-Bitcoin-Core-v31-na-prática.md)

**Resumo**

Explora as principais novidades da versão 31 do Bitcoin Core através de experimentos práticos com **bitcoin-cli**. O artigo compara diretamente a v31 com a v30, mostrando como a nova versão passa a expor conceitos mais avançados da mempool, como **clusters**, **chunks** e a competição econômica por espaço em bloco. Também apresenta novos RPCs e melhorias em comandos existentes, permitindo observar mudanças reais no comportamento do node.

**O que você aprende**

- Como comparar o comportamento do **Bitcoin Core v30 e v31**
- O que são **clusters de transações** e como explorá-los com `getmempoolcluster`
- Como interpretar **chunks**, `chunkweight` e `fees.chunk`
- Como visualizar a **coinbase diretamente** com o novo campo `coinbase_tx`
- Como rastrear quem gastou um output usando `gettxspendingprevout`
- Como interpretar o **getmempoolfeeratediagram** e a competição por espaço em bloco
- O impacto das mudanças da v31 na organização da mempool
- Como a nova versão expõe melhor a estrutura econômica do Bitcoin

---

## 📖 10 blocos marcantes da história do Bitcoin (e o que eles ensinam)

[**Acesse o artigo aqui**](./artigos/artigo24-10-blocos-marcantes.md)

**Resumo**

Explora dez blocos reais da blockchain que ajudam a entender momentos importantes da evolução do Bitcoin. Em vez de apresentar apenas teoria, o artigo utiliza blocos históricos como portas de entrada para conceitos fundamentais do protocolo, incluindo emissão monetária, UTXOs, halving, consenso, SegWit, Taproot, mineração e taxas. Cada bloco é analisado diretamente na blockchain, com exemplos usando exploradores e **bitcoin-cli**, mostrando como a história do Bitcoin pode ser observada através dos próprios dados da rede.

**O que você aprende**

- O significado do **Genesis Block** e da primeira coinbase
- Como ocorreu a **primeira transação entre pessoas** (Satoshi → Hal Finney)
- O que foi o bug dos **184 bilhões de bitcoins** e como a rede reagiu
- Como funciona o **halving** e a política monetária programada
- O impacto do **BIP66** e das assinaturas DER no consenso
- Como o **SegWit** alterou a estrutura das transações
- Por que um bloco pode ser válido mesmo sem criar novos bitcoins
- O papel das **taxas de transação** na segurança futura da rede
- Como a mineração é um processo probabilístico, mesmo para mineradores solo

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
