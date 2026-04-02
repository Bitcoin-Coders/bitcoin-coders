# Schnorr e Taproot: a nova era das assinaturas

A chegada do Taproot em novembro de 2021 marcou uma das maiores evoluções técnicas da história do Bitcoin. Pela primeira vez, o protocolo adotou um novo algoritmo de assinatura, o Schnorr, trazendo simplicidade matemática, eficiência, linearidade e a possibilidade de agregar múltiplas assinaturas em uma única prova compacta. Com isso, multisigs deixaram de “entregar o jogo”, scripts complexos puderam ser ocultados até o momento do uso e transações avançadas passaram a parecer transações comuns. Taproot unificou a aparência dos outputs, otimizou o consumo de espaço em bloco e abriu a porta para uma nova geração de protocolos, desde MuSig2 até PTLCs. Este artigo explora exatamente essa nova era: por que Schnorr importa, o que Taproot realmente muda e como essas inovações tornam o Bitcoin mais privado, mais escalável e mais robusto.

### Por que o Bitcoin precisava evoluir além do ECDSA

O ECDSA serviu muito bem ao Bitcoin durante mais de uma década. Ele é seguro, amplamente estudado e suportado por praticamente todas as bibliotecas criptográficas modernas. No entanto, conforme o Bitcoin amadureceu, algumas **limitações estruturais** do ECDSA começaram a se tornar mais evidentes, não porque o algoritmo estivesse “quebrado”, mas porque sua forma de operação impõe barreiras à escalabilidade, privacidade e expressividade dos scripts.

A primeira limitação está na própria matemática: o ECDSA **não é linear**. Isso significa que, se duas partes querem assinar conjuntamente uma transação, elas precisam produzir **duas assinaturas separadas**, colocadas lado a lado no `scriptWitness` ou no `scriptSig`. Essa característica faz com que multisigs tradicionais revelem informações desnecessárias, como:

- quantas chaves fazem parte do arranjo,
- quais chaves participaram da assinatura,
- a ordem das chaves,
- e o próprio fato de que aquilo é uma multisig.

Ou seja, um multisig pré-Taproot é sempre distinguível, não importa se são 1-of-2, 2-of-3 ou 3-of-5: todos “vazavam” sua estrutura internamente, prejudicando a privacidade e aumentando o espaço ocupado no bloco.

Além disso, o ECDSA depende de uma codificação DER relativamente pesada, que introduz verificações adicionais, potenciais ambiguidades (especialmente no campo `s`, mitigadas apenas com a regra low-S) e complexidade extra para os nós validadores. Embora essas nuances não comprometam a segurança, elas tornam o sistema **mais complicado do que precisa ser**.

Há também o legado da maleabilidade: mesmo com BIP66, BIP62 e SegWit resolvendo suas facetas principais, o ECDSA continua sendo um algoritmo que **permite duas assinaturas matematicamente válidas** para a mesma mensagem. Isso exige cuidados adicionais no design de protocolos de camada 2 e de contratos mais elaborados.

Por fim, transações complexas, como scripts condicionais, timelocks, cláusulas alternativas e multisigs com dezenas de participantes, sempre deixaram uma “impressão digital” na blockchain, consumindo mais bytes e tornando claro para qualquer observador que aquele gasto não era um pagamento comum.

Era necessário um algoritmo que:

- fosse mais simples matematicamente,
- eliminasse completamente a maleabilidade,
- permitisse **agregação de chaves e assinaturas**,
- reduzisse a pegada on-chain,
- e tornasse transações avançadas **indistinguíveis** de transações comuns.

Essa evolução chegou com **Schnorr + Taproot**, abrindo uma nova fase no design de assinaturas e scripts no Bitcoin.

### Schnorr (BIP340): o que muda em relação ao ECDSA

O algoritmo de assinaturas de Schnorr não é apenas uma alternativa mais moderna ao ECDSA, ele representa um salto conceitual em simplicidade, eficiência e capacidade de composição. Na prática, Schnorr resolve problemas que estavam presentes no Bitcoin desde o início e abre espaço para funcionalidades que simplesmente **não eram possíveis** com ECDSA.

Do ponto de vista matemático, Schnorr é notavelmente elegante. Seu funcionamento é direto: gera-se um ponto aleatório `R = kG`, calcula-se um desafio `e = H(R || P || msg)` e então produz-se uma assinatura composta por apenas dois elementos:

```
s = k + e·d   (mod n)
assinatura = (R, s)
```

Já a verificação é ainda mais simples:

```
sG == R + eP
```

Essa clareza contrasta com as múltiplas camadas e verificações necessárias no ECDSA. Mas a grande vantagem não está apenas na estética: está na **linearidade**. Em Schnorr, somar chaves públicas e combinar assinaturas é matematicamente natural, não é um truque, não é um hack. Isso desbloqueia uma propriedade crucial:

> É possível transformar N assinaturas em uma única assinatura.
> 

E isso muda tudo. Multisigs deixam de revelar quantos signatários existem. Protocolos de múltiplas partes podem colaborar sem expor sua estrutura. A rede valida mais rapidamente. O espaço gasto em blocos diminui drasticamente. E, de quebra, a assinatura final é indistinguível de um pagamento simples.

Outro diferencial importante: Schnorr é **determinístico por construção**, eliminando completamente as ambigüidades que tornam o ECDSA vulnerável a ataques relacionados ao nonce `k`. A maleabilidade, que sempre foi um ponto sensível no Bitcoin, desaparece de forma natural com Schnorr, não como uma mitigação, mas como uma característica nativa do algoritmo.

Além disso, o formato de assinatura é fixo e limpo: **exatamente 64 bytes**, sem DER, sem integers ASN.1, sem zeros opcionais, sem regras de canonicidade complexas. Simplesmente `(R || s)`.

No contexto do Bitcoin, isso foi formalizado no **BIP340**, que define:

- uso de **x-only pubkeys** (apenas o coordenada x do ponto),
- formato de assinatura fixo de 64 bytes,
- esquema de hash específico (tagged hashing),
- normalização clara e ausência completa de maleabilidade.

O resultado é um algoritmo mais leve, mais robusto e muito mais “combinável” do que o ECDSA e é exatamente essa propriedade que torna possível o resto da arquitetura do Taproot.

### A chave do Taproot: Pay-to-Pubkey e a unificação das saídas

Antes do Taproot, o Bitcoin possuía múltiplos tipos de saída (P2PKH, P2SH, P2WSH, P2WPKH) cada uma com sua própria estrutura, tamanho e “impressão digital” na blockchain. Para qualquer observador externo, era trivial distinguir:

- pagamentos simples de carteiras convencionais,
- multisigs,
- scripts de timelock,
- contratos mais complexos,
- e até mesmo certas carteiras específicas.

Essa diversidade funcional era útil, mas criava um efeito colateral: **privacidade menor e previsibilidade menor**. Quanto mais variado o tipo de saída, mais fácil identificar padrões e inferir comportamentos.

O Taproot mudou esse modelo radicalmente ao introduzir uma nova forma de construir saídas do tipo *“pay-to-pubkey”*. Em vez de scripts identificáveis ou árvores de condições explícitas, o Taproot parte de uma ideia simples: Tudo é uma chave pública.

Mesmo scripts complexos são combinados em uma árvore de Merkle interna e, no final, o que aparece na blockchain é apenas **um único valor de 32 bytes**, derivado de:

- uma chave pública base (`internal key`), e
- opcionalmente, uma árvore de scripts (`script tree`) que fica totalmente oculta até ser usada.

A saída Taproot é construída como:

```
output_key = internal_key ⊕ hash_tap_tweak
```

E o resultado desse tweak é uma chave pública completamente válida, indistinguível de uma chave comum. Isso significa que:

- um gasto simples (key-path) parece exatamente igual a um P2PK “antigo”,
- um multisig MuSig2 parece exatamente igual a um pagamento de uma única chave,
- scripts complexos ficam invisíveis até serem utilizados (e mesmo assim só revelam o ramo necessário).

O efeito prático é profundo.

**Unificação visual**

Antes, analistas conseguiam reconhecer padrões (P2SH, P2WSH, multisig, LN, etc.).

Agora, todas as saídas Taproot têm **o mesmo tamanho e formato**.

**Privacidade estrutural**

Você pode ter:

- 2-of-3 multisig,
- 15-of-15 multisig,
- um script condicional complexo,
- um contrato com fallback,
- um timelock embarcado,
- ou nada disso.

A blockchain enxerga apenas **um único pubkey**.

**Otimização de espaço**

Se o gasto ocorrer via key-path (o mais comum), a transação revela apenas:

- uma assinatura Schnorr de 64 bytes
- e nada mais

Em muitos casos, isso substitui estruturas de script inteiras que antes ocupavam dezenas ou centenas de bytes.

**Modularidade**

A presença da árvore de scripts (MAST) permite adicionar condições alternativas sem torná-las públicas ou onerosas quando não usadas.

No fundo, a genialidade do Taproot está nessa fusão:

> Chave pública + tweak criptográfico → saída universal.
> 

Tudo parece um pagamento simples, mas pode carregar uma lógica extremamente sofisticada “por trás da chave”. Esse é o alicerce da MuSig2, PTLCs, contratos mais leves e uma nova geração de protocolos de segunda camada.

### MAST: Árvores de Scripts no Taproot

Antes do Taproot, sempre que um UTXO dependia de múltiplas condições, como *timelock OU multisig OU chave de recuperação,* **todo o script completo** precisava ser revelado na blockchain no momento do gasto, mesmo que apenas **uma** das condições fosse usada.

Isso significava:

- mais bytes,
- menos privacidade,
- scripts gigantes expostos,
- custos maiores de validação,
- e padrões fáceis de identificar (ruim para privacidade).

O Taproot resolve isso com o **MAST (Merkelized Abstract Syntax Tree)**, transformando o roteiro de verificação em uma **árvore Merkle**, onde **cada condição fica em um “ramo” isolado**.

---

**Como um MAST funciona (visão geral)**

1. Cada condição (script A, script B, script C…) vira uma **folha**.
2. Cada folha é **hasheada individualmente** → `H(A)`, `H(B)`, `H(C)`.
3. As folhas são combinadas **duas a duas** (como um Merkle tree normal):
    - `H(A)` concatenado com `H(B)` → `H(H(A) || H(B))`
4. Esse resultado é novamente combinado com o hash de `H(C)`:
    - `H( H(H(A)||H(B)) || H(C) )`
5. O resultado final dessa árvore é o **Merkle root**, que será incorporado no *tweak* da chave Taproot.

A imagem abaixo mostra isso visualmente:

---

![Artigo18-img1.png](./assets/Artigo18-img1.png)

**Por que isso é tão poderoso?**

**Privacidade**

Somente o *ramo usado* é revelado.

Se o gasto for pelo script B:

- `script B` é revelado,
- `H(A)` e `H(C)` são revelados **apenas para demonstrar que B faz parte da árvore,**
- todos os outros scripts ficam completamente ocultos.

Observadores externos **não têm como saber**:

- quantos scripts existiam,
- quais outras condições eram possíveis,
- qual era a lógica completa do contrato.

---

**Eficiência**

Antes:

um contrato com 10 condições podia revelar 300–600 bytes de script.

Agora, apenas:

- o script usado,
- mais poucos hashes intermediários.

Em muitos casos, isso reduz dezenas ou centenas de bytes.

---

**Modularidade**

Você pode compor contratos complexos:

- multisigs alternativas,
- caminhos de fallback,
- condições temporais,
- cláusulas de recuperação…

…**sem pagar nada extra** se não forem usadas.

---

**Combinação perfeita com Taproot**

O Merkle root do MAST é incorporado ao **tweak da internal key**, gerando a **Taproot output key**.

Isso significa:

> Para a blockchain, tudo continua parecendo um pagamento comum para uma chave única.
> 

Somente se o gasto não for pelo *key-path* é que um ramo do MAST aparece.

---

**Como um gasto MAST funciona na prática**

Para gastar via um script específico (por exemplo, script B):

O usuário precisa revelar apenas:

1. **O script B** (folha utilizada)
2. **Os dados necessários para executá-lo**
3. **A Merkle Proof** até o root
    - no exemplo: revelar `H(A)` e `H(C)`
4. O **script root** já está comprometido no output Taproot

O validador então calcula:

```
H(B) → H(H(A)||H(B)) → H( H(H(A)||H(B)) || H(C) )
```

E compara com o Merkle root do Taproot.

Se igual → o script é válido.

---

O MAST permite contratos complexos e privados, revelando apenas o mínimo necessário e tudo isso escondido atrás de um único endereço Taproot.

---

### **Resumindo o ScriptPubKey (script de bloqueio)**

Olhando o scriptPubKey de uma transação vemos:

```bash
"scriptPubKey": {
        "asm": "1 8b1656dc5c812625793ef37199103fc26fac86f54d9b1e42bf30ff339fa7304f",
        "desc": "rawtr(8b1656dc5c812625793ef37199103fc26fac86f54d9b1e42bf30ff339fa7304f)#8u2ykne3",
        "hex": "51208b1656dc5c812625793ef37199103fc26fac86f54d9b1e42bf30ff339fa7304f",
        "address": "tb1p3vt9dhzusynz27f77dcejyplcfh6eph4fkd3us4lxrln88a8xp8s8gpxu9",
        "type": "witness_v1_taproot"
      }
```

No Taproot, ele sempre tem esse formato:

`OP_1 <taproot_output_key_32_bytes>`

**`OP_1`:** Taproot v1

`<taproot_output_key_32_bytes>`: **chave publica** calculada na curva elíptica que envolve, uma **chave publica interna**, um **hash entre essa chave e o merkel root** e o **ponto gerador G.**

---

### **Resumindo o Witness (script de desbloqueio)**

Olhando o Witness, temos:

```bash
"txinwitness": [
        "81cebc1eb2db28511fb50de5b60d4888be5ff092947107939485e7ce1ae30ab659263ae39adb4fe7eb776b1d2e7ee60e5d307d7af2355632d997e30ca3579f41"
      ],
```

Simplesmente é uma assinatura Schnorr de 64 bytes (32 bytes de **R** + 32 bytesde **s**), onde:

`R = kG` —> um **ponto aleatório** na curva elíptica

`s = k + e·d   (mod n)` —> é calculado a partir de  um **nonce**, o **desafio** e a **chave privada**

`e = H(R || P || msg)` —> **Hash** entre o ponto **R**, a **chave pública** (que está no scriptPubKey) e a **mensgem/transação**

---

### Resumindo a verificação

O verificador apenas checa:

```bash
s·G  ==  R + e·P
```

Se iguais —> Assinatura válida

---

### Tapscript (BIP342): um script mais limpo e futuro-proof

Taproot não trouxe apenas um novo formato de chave e um novo algoritmo de assinatura. Ele também introduziu uma revisão profunda na própria linguagem de script do Bitcoin. O objetivo não era reinventar tudo, mas **remover restrições antigas**, simplificar o modelo de verificação e criar um espaço onde novas funcionalidades possam ser adicionadas de forma segura e incremental, sem necessidade de hard forks.

Esse novo ambiente operacional é o **Tapscript (BIP342),** uma evolução da linguagem de script do Bitcoin adaptada à era Schnorr.

A primeira diferença fundamental é estrutural: enquanto scripts do tipo P2WSH tinham limitações rígidas (como o limite de 10.000 bytes, regras complexas de verificação de limites e restrições herdadas), o Tapscript remove várias dessas travas. Isso não significa “scripts infinitos” ou “smart contracts Turing-completos”. Significa que a base técnica agora é mais limpa, mais consistente e mais preparada para extensões futuras.

Tapscript também modifica como a assinatura é verificada. Em vez de usar o modelo do ECDSA, que dependia de DER, de regras de canonicidade e de um processo de construção de preimage complicado, o Taproot passa a usar o modelo Schnorr, com preimages uniformes, assinaturas fixas de 64 bytes e uma lógica de verificação muito mais direta.

Outra melhoria crucial é o **tagged hashing**, introduzido como uma forma de domínios de hash para diferentes partes do protocolo. Isso evita colisões acidentais entre tipos de dados distintos e torna a verificação mais robusta contra ataques sutis envolvendo pré-imagens e colisões estruturais.

Além disso, o Tapscript adota um conjunto de regras de verificação mais maleáveis (“soft”) para opcodes ainda não existentes. Em outras palavras:

> novos opcodes poderão ser adicionados no futuro sem quebrar transações já existentes.
> 

Isso é importantíssimo para a evolução do Bitcoin. Em versões anteriores do script, adicionar opcodes exigia mudanças complexas, com risco de quebrar compatibilidade ou exigir novos mecanismos de validação. Com Tapscript, a estrutura é preparada para receber instruções adicionais, como opcodes relacionados a covenants, introspecção de transações ou verificações criptográficas mais avançadas, sem custo de compatibilidade.

O Tapscript também reavalia a forma como certos opcodes antigos funcionam. Muitos limites que eram herdados de versões pré-SegWit, como contadores de operações ou limites artificiais de tamanho de script, são flexibilizados ou reinterpretados no contexto SegWit v1. Isso resulta em verificações mais simples, previsíveis e eficientes para full nodes.

Por fim, Tapscript trabalha de forma integrada com a árvore de scripts do Taproot (MAST). Isso significa que cada ramo da árvore pode ter seu próprio conjunto de condições, e o Bitcoin só precisa verificar **o ramo revelado,** em vez de analisar um script monolítico gigante, como ocorria nos P2WSH. O resultado é mais privacidade, mais modularidade e menos bytes colocados na blockchain.

Em essência:

> O Tapscript é a “segunda metade” do Taproot: a parte que permite que o protocolo cresça.
> 

Ele simplifica o presente e abre o caminho para futuros avanços, mantendo a filosofia sistêmica do Bitcoin: máxima segurança, mínima complexidade, compatibilidade eterna.

### Como um gasto Taproot realmente aparece no Bitcoin (exemplo na Signet)

Para entender como uma entrada Taproot é registrada no Bitcoin hoje, vamos analisar uma transação real na **Signet**.

**1. Obtendo a transação**

Se o seu nó **não foi iniciado com**:

```
-txindex=1
```

então ele **não armazena todas as transações do blockchain**, apenas aquelas pertencentes às suas carteiras ou ainda presentes no mempool. Por isso, ao consultar uma transação confirmada pode ser necessário informar também o **hash do bloco** onde ela foi minerada.

O comando fica assim:

```bash
bitcoin-cli -datadir="." getrawtransaction <txid> true <blockhash>
```

No exemplo abaixo, analisamos a transação:

```
2d86980bc9b4f3b8b62dc771ef391647ab76e924265c22c387e2d09cddc393e2
```

Rodando o comando:

```bash
bitcoin-cli -datadir="." getrawtransaction 2d86980bc9b4f3b8b62dc771ef391647ab76e924265c22c387e2d09cddc393e2 true 0000001265868377fb0b0c0bb47cc1e6b5fb8d7db762b9b70640fe54f036f06f
```

---

**2. O que realmente importa: o witness**

O trecho relevante da transação é o `vin`:

```json
"vin": [
  {
    "txinwitness": [
      "81cebc1eb2db28511fb50de5b60d4888be5ff092947107939485e7ce1ae30ab659263ae39adb4fe7eb776b1d2e7ee60e5d307d7af2355632d997e30ca3579f41"
    ]
  }
]
```

Esse campo contém **tudo** o que um gasto Taproot *key-path* precisa.

**Observe:**

- há **somente 1 elemento** no witness
- esse elemento é uma **assinatura Schnorr**
- a assinatura tem exatamente **64 bytes**
- não há chave pública
- não há script
- não há `sighash` explícito

Isso confirma que o gasto foi feito via **Taproot key-path**, o caminho padrão de gasto no Taproot.

---

**3. Como interpretar esse formato**

**✔️ Taproot key-path (o que vimos acima)**

```
<assinatura_schnorr_64_bytes>
```

Somente isso.

O node já sabe qual é a chave pública Taproot tweaked (ela está no próprio output), de modo que basta apresentar **uma única assinatura Schnorr** para provar o gasto.

---

**4. Comparando com SegWit tradicional**

Para entender a diferença, veja o formato de um gasto **P2WPKH** (SegWit v0):

```
<assinatura DER> <sighash> <chave pública>
```

Ou seja:

- assinatura no formato **DER** (tamanho variável, ~71 bytes)
- um byte de **sighash** no final (`01`, `81` etc.)
- chave pública **33 bytes**

**Já no Taproot (seu exemplo real):**

```
<assinatura_schnorr_64_bytes>
```

Sem DER, sem chave pública, sem script.

Muito mais limpo, compacto e eficiente.

---

Este exemplo real na Signet mostra exatamente como um gasto Taproot aparece hoje:

- witness minimalista
- apenas 64 bytes de assinatura Schnorr
- sem dados extras
- sem DER
- sem scripts expostos

Esse é o formato ideal do **key-path spend**, que representa o uso mais comum e mais eficiente do Taproot e um dos motivos pelos quais Taproot simplifica tanto a estrutura das transações modernas no Bitcoin.

---

Schnorr e Taproot inauguram uma nova fase no design de assinaturas e scripts do Bitcoin. Ao combinar simplicidade matemática, agregação nativa, privacidade estrutural, otimização de espaço e uma arquitetura modular preparada para o futuro, o Taproot transforma transações avançadas em transações comuns, sem sacrificar segurança ou verificabilidade. MAST, MuSig2, PTLCs, Tapscript e diversas outras construções passam a ter um terreno sólido para florescer, reforçando o papel do Bitcoin como uma plataforma minimalista, mas extremamente expressiva quando necessário. A evolução é discreta na forma, mas profunda na essência: menos bytes, menos exposição, menos distinções… e muito mais poder. O resultado final é um Bitcoin mais eficiente, mais privado e mais preparado para os próximos anos.

Escrito por: Rafael Santos
