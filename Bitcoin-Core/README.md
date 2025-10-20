# 🧠 Eixo 3. Bitcoin Core e Protocolos

> Internals, RPC, scripts, consenso, mineração, P2P e mempool.  
> Este eixo mergulha no código-fonte do Bitcoin Core, explorando seus componentes internos, mecanismos de consenso e validação.

---

## 🧭 Visão Geral

🎯 **Objetivo:** capacitar o aluno a compreender e navegar pelo código-fonte do Bitcoin Core, analisando seus módulos, processos de rede e consenso, e desenvolvendo autonomia para contribuir tecnicamente com o projeto.

📘 **Conteúdos principais:** Estrutura e compilação do Core, Scripts Bitcoin, PSBT e descriptors, Blocos e Mempool, Consenso e Mineração, Testes e Debug.

---

## 📘 Cursos

| Curso | Nível | Descrição | Principais Aulas |
|--------|--------|------------|------------------|
| 🧩 **Arquitetura e Compilação do Bitcoin Core** | Gênese → Satoshi | Entenda a estrutura do código, dependências e processos de build do Core. | Estrutura de diretórios · Compilação · Configuração e make targets · RPC Internals |
| ⚙️ **Scripts Avançados e PSBTs** | Satoshi | Estudo prático do Bitcoin Script, PSBT e automação de fluxos de assinatura. | Estrutura da PSBT · Parsing de scripts · Scripts multiassinatura · OpCodes importantes |
| 🔄 **Rede P2P e Mempool Internals** | Satoshi → Core | Como os nodes se comunicam, propagam transações e mantêm a mempool sincronizada. | Mensagens version/verack · inv/tx/block · Pool de transações e políticas de relay |
| ⛏️ **Mineração e Consenso** | Core | Funcionamento do Proof-of-Work, criação de blocos e validação de consenso. | Coinbase tx · Target e dificuldade · Verificação de blocos · Forks e reorganizações |
| 🧠 **Testes, Debug e Contribuição ao Core** | Core | Uso do test framework, debugging e fluxo técnico de submissão de código. | Functional tests · RPC testing · Logs e debugging · Build e patch workflow |
| 🔐 **Segurança, Política e Padrões de Código** | Core | Práticas de segurança, estilo e revisão técnica no código-fonte. | Guidelines · Auditoria de patches · Estilo e boas práticas de commits |

---

### 🧩 **Curso: Arquitetura e Compilação do Bitcoin Core**

*Nível Gênese → Satoshi*  
Primeiro contato com o código-fonte e ambiente de desenvolvimento do Core.

**Aulas:**
1. Estrutura do repositório e principais diretórios (`src/`, `test/`, `doc/`)  
2. Dependências e toolchain de build (autotools, cmake, make)  
3. Compilação e flags de otimização  
4. RPC e arquitetura modular  
5. Introdução ao `bitcoind` e `bitcoin-cli` internamente  

---

### ⚙️ **Curso: Scripts Avançados e PSBTs**

*Nível Satoshi*  
**Descrição:** Aprofundamento em Bitcoin Script, Partially Signed Bitcoin Transactions e automação de fluxos de assinatura.  
**Aulas:** a definir (incluindo scripts condicionais, PSBT em detalhe e integração com carteiras descriptor).

---

### 🔄 **Curso: Rede P2P e Mempool Internals**

*Nível Satoshi → Core*  
**Descrição:** Estuda as mensagens e o comportamento da rede P2P do Bitcoin, além da lógica de mempool e relay de transações.  
**Aulas:** a definir (mensagens, serialização, relay policies, compact block e validação).

---

### ⛏️ **Curso: Mineração e Consenso**

*Nível Core*  
**Descrição:** Explica a mineração, Proof-of-Work e o mecanismo de consenso da rede Bitcoin.  
**Aulas:** a definir (Coinbase tx, target, dificuldade, reorganizações e block template).  

---

### 🧠 **Curso: Testes, Debug e Contribuição ao Core**

*Nível Core*  
**Descrição:** Introduz o sistema de testes e o fluxo **técnico** de contribuição do Bitcoin Core — preparando o aluno para compreender a arquitetura de validação, os tipos de testes e o ciclo interno de desenvolvimento antes de entrar no processo colaborativo completo (abordado no Eixo 4 – Comunidade e Contribuição).  

**Aulas:**
1. Estrutura do test framework (`test/functional` e `test/util`)  
2. Execução de testes RPC e unitários  
3. Mock nodes e testes de rede  
4. Análise de logs e debugging com `-debug` e `gdb`  
5. Fluxo técnico de submissão: build, diff, patch e reexecução de testes  
6. Introdução ao ciclo de PRs (visão conceitual, sem revisão colaborativa)

---

### 🔐 **Curso: Segurança, Política e Padrões de Código**

*Nível Core*  
**Descrição:** Examina as políticas de segurança e as práticas de manutenção de código no Bitcoin Core.  
**Aulas:** a definir (security policy, disclosure process, guidelines e padrões de commits).  

---

## ⚡ **Cursos Especiais — BitUps (Workshops Imersivos)**

Os **BitUps** deste eixo unem teoria e prática do código-fonte com exercícios guiados em tempo real.  
São experiências curtas (2h–4h) voltadas à exploração do Core e análise de scripts e blocos.

| BitUp | Nível | Tema | Status |
|-------|-------|------|--------|
| 🧩 **BitUp 1 — Explorando o Código do Bitcoin Core** | Gênese → Satoshi | Navegação no repositório e primeiros comandos de build | Em desenvolvimento |
| ⚙️ **BitUp 2 — Scripts e PSBTs Avançados** | Satoshi | Construção, parsing e validação de PSBTs e scripts complexos | Em desenvolvimento |
| ⛏️ **BitUp 3 — Consenso e Validação de Blocos** | Core | Análise de blocos e simulação de reorganizações | Em desenvolvimento |

---

## 🚀 **Programa 1 – Core Insight: Explorando o Código do Bitcoin**

📅 **Duração:** 3 semanas  
🎯 **Objetivo:** desenvolver autonomia para entender, navegar e modificar o código do Bitcoin Core, conectando teoria e prática de rede, consenso e validação.

📘 **Formato:**
- Semana 1 → Conteúdo gravado: arquitetura, build e RPC internals  
- Semana 2 → Aulas ao vivo: scripts, PSBTs e rede P2P  
- Semana 3 → Hackathon: análise e modificação de código (mini feature ou PR simulado)

🔗 **Mais informações:** [bitcoincoders.org/#programas](https://bitcoincoders.org/#programas)

---

> 🧠 Este eixo representa o ápice técnico do Bitcoin Coders — o ponto em que o aluno deixa de apenas usar ferramentas e passa a compreender (e aprimorar) o código que as constrói.
