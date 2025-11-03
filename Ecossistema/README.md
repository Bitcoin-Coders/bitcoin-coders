# ⚡ Eixo 2. Desenvolvimento para o Ecossistema Bitcoin

> SDKs, Lightning, wallets, APIs, integrações fiat, apps e UX dev.  
> Este eixo prepara o desenvolvedor para criar soluções reais que interagem com o ecossistema Bitcoin — tanto on-chain quanto na Lightning Network.

---

## 🧭 Visão Geral

🎯 **Objetivo:** Capacitar o aluno a dominar o uso de SDKs, bibliotecas e ferramentas para integrar Bitcoin e Lightning em aplicações reais — de carteiras e APIs a serviços e plataformas completas.

📘 **Conteúdos principais:** Bitcoin CLI e RPC, bitcoinjs-lib, python-bitcoinlib e rust-bitcoin, Lightning Network (LND, CLN, LDK, Breez), BDK (Bitcoin Development Kit), BTCPay e Strike, RGB, Fedimint e DID/Web5.

---

## 📘 Cursos

| Curso | Nível | Descrição | Principais Aulas |
|--------|--------|------------|------------------|
| 🖥️ **Bitcoin CLI e RPC** | Gênese → Satoshi | Base prática para operar e compreender o Bitcoin Core por linha de comando e via RPC. | Nós Bitcoin · Redes e endereços · Transações e scripts · Mempool e mineração |
| 🧩 **bitcoinjs-lib, python-bitcoinlib e rust-bitcoin** | Satoshi | Introdução às bibliotecas mais usadas no desenvolvimento Bitcoin multi-linguagem. | Criação e assinatura de transações · Leitura e decodificação de blocos |
| ⚡ **Lightning Network (LND, CLN, LDK, Breez)** | Satoshi → Core | Desenvolvimento de soluções com canais de pagamento, invoices e integração com SDKs Lightning. | Criação de canais · Envio de pagamentos · APIs LND/LDK |
| 🧱 **BDK (Bitcoin Development Kit)** | Satoshi → Core | Construção de carteiras e aplicações on-chain modernas com o BDK. | Carteiras descriptor · PSBTs · Sincronização com blockchain |
| 💳 **BTCPay e Strike** | Satoshi | Integração de pagamentos Bitcoin e Lightning em soluções reais. | Configuração e APIs · Webhooks e monitoramento |
| 🌈 **RGB, Fedimint e DID/Web5** | Core | Tecnologias emergentes para identidade descentralizada e protocolos de segunda camada. | Tokens e contratos · Federations · Identidade soberana |

---

### 🖥️ **Curso: Bitcoin CLI e RPC**

*Nível Gênese → Satoshi*  
Base do desenvolvimento técnico on-chain. Envolve o uso direto do Bitcoin Core e de seus comandos para entender o funcionamento da rede e das transações.

**Aulas:**
1. Nós Bitcoin  
2. Mainnet, Testnet, Signet e Regtest: O universo das redes Bitcoin  
3. Explorando os tipos de endereços no Bitcoin Core (Parte 1): Legacy  
4. HD Wallets e Descriptor Wallets: A evolução da geração de endereços  
5. SegWit: teoria e prática na Signet  
6. Como funciona uma carteira no Bitcoin Core: chaves, endereços e UTXOs  
7. Explorando Transações no Bitcoin Core  
8. Construindo Transações no Bitcoin Core  
9. Taxas, Mempool e Estratégias de Confirmação  
10. Transferências Avançadas e Segurança  
11. Introdução a Scripts e Assinaturas  
12. Bitcoin Script: Máquina de Execução e Pilha  
13. Scripts Condicionais e Contratos Base  
14. Como os Scripts se transformam em Endereços no Bitcoin  
15–18. **Assinaturas Digitais (4 aulas)** — teoria, ECDSA, DER encoding e verificação de assinaturas  
19–22. **Mineração e Blocos (4 aulas)** — estrutura de blocos, PoW, geração e propagação na rede  

---

### 🧩 **Curso: bitcoinjs-lib, python-bitcoinlib e rust-bitcoin**

*Nível Satoshi*  
**Descrição:** Introduz o desenvolvimento Bitcoin em diferentes linguagens, permitindo criar, assinar e validar transações de forma programática.  
**Aulas:** a definir (abordar criação de transações, parsing, integração RPC e testes multi-idioma).  

---

### ⚡ **Curso: Lightning Network (LND, CLN, LDK, Breez)**

*Nível Satoshi → Core*  
**Descrição:** Introdução completa à Lightning Network e seu ecossistema de SDKs.  
**Aulas:** a definir (propor canais, invoices, pagamentos, roteamento, integração via LND REST/gRPC e SDK Breez).  

---

### 🧱 **Curso: BDK (Bitcoin Development Kit)**

*Nível Satoshi → Core*  
**Descrição:** Desenvolvimento de carteiras e aplicações on-chain usando o BDK.  
**Aulas:** a definir (configuração do kit, carteiras descriptor, PSBTs, indexação e sincronização).  

---

### 💳 **Curso: BTCPay e Strike**

*Nível Satoshi*  
**Descrição:** Integração de pagamentos Bitcoin e Lightning em lojas e serviços.  
**Aulas:** a definir (instalação, configuração, integração via API, monitoramento e relatórios).  

---

### 🌈 **Curso: RGB, Fedimint e DID/Web5**

*Nível Core*  
**Descrição:** Explora protocolos complementares e emergentes no ecossistema Bitcoin para tokens, identidade e federações.  
**Aulas:** a definir (introdução a RGB, arquitetura Fedimint, princípios de identidade descentralizada e interoperabilidade com o Bitcoin).  

---

## ⚡ **Cursos Especiais — BitUps (Workshops Imersivos)**

Os **BitUps** deste eixo unem pares de cursos para prática aplicada com foco em prototipagem.  
São workshops curtos (2h–4h), com demonstrações ao vivo e experimentação prática.

| BitUp | Nível | Conteúdos Relacionados | Link | PDF |
|-------|-------|------------------------|------|-----|
| 🪙 **BitUp 1 — Rodando Nós e Explorando as Redes do Bitcoin** | Gênese → Satoshi | Bitcoin CLI e RPC | [Acessar o curso](https://bitcoincoders.org/curso/carteiras-bitcoin-core) |https://github.com/Bitcoin-Coders/bitcoin-coders/blob/main/Ecossistema/Bitup%20Coders%20-%2001.pdf|
| 🪙 **BitUp 2 — Carteiras Bitcoin Core** | Gênese → Satoshi | Bitcoin CLI e RPC | [Acessar o curso](https://bitcoincoders.org/curso/carteiras-bitcoin-core) |https://github.com/Bitcoin-Coders/bitcoin-coders/blob/main/Ecossistema/Dominando%20as%20Carteiras%20no%20Bitcoin%20Core_%20Da%20Teoria%20%C3%A0%20Pr%C3%A1tica%20na%20Signet.pdf|
| 🔄 **BitUp 3 — Transações Bitcoin Core** | Satoshi | Bitcoin CLI e RPC + bitcoinjs-lib/python-bitcoinlib | [Acessar o curso](https://bitcoincoders.org/curso/transacoes-bitcoin-core) |https://github.com/Bitcoin-Coders/bitcoin-coders/blob/main/Ecossistema/Transa%C3%A7%C3%B5es%20no%20Bitcoin%20Core%20e%20Signet.pdf|
| 🧠 **BitUp 4 — Scripts Bitcoin** | Satoshi → Core | Scripts, assinaturas e automação | [Acessar o curso](https://bitcoincoders.org/curso/scripts-bitcoin) |https://github.com/Bitcoin-Coders/bitcoin-coders/blob/main/Ecossistema/Scripts_%20como%20o%20Bitcoin%20executa%20suas%20regras.pdf|

---

## 🚀 **Programa 1 – CoreCraft: Domine o Bitcoin Core na Prática**

📅 **Duração:** 3 semanas  
🎯 **Objetivo:** dominar o Bitcoin Core de ponta a ponta — da linha de comando à integração programática, criando ferramentas e aplicações conectadas à rede.

📘 **Formato:**
- Semana 1 → Conteúdo gravado: fundamentos do Bitcoin Core e carteiras  
- Semana 2 → Aulas ao vivo: transações, scripts e automação  
- Semana 3 → Hackathon: projeto final integrando Bitcoin CLI + RPC + SDK  

🔗 **Mais informações:** [bitcoincoders.org/#programas](https://bitcoincoders.org/#programas)

---

> ⚡ Este eixo consolida a transição entre a compreensão técnica e a aplicação prática — formando desenvolvedores capazes de integrar Bitcoin em qualquer camada do ecossistema.
