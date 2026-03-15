# Bitcoin Script: Máquina de Execução e Pilha

por Rafael Santos

No artigo anterior, vimos que o **Bitcoin Script** funciona como um sistema de *cadeados e chaves*. O `scriptPubKey` é o **cadeado** gravado no output de uma transação, enquanto o `scriptSig` é a **chave** fornecida no input da transação seguinte para tentar abri-lo.

Mas o que realmente acontece quando essa chave é girada? Como o Bitcoin “testa” se ela se encaixa?

A resposta está na **máquina de execução de scripts,** um mecanismo simples, mas determinístico, que transforma cada transação em um pequeno programa matemático.

Ela funciona de forma linear e previsível: recebe dados, aplica operações, e retorna um único resultado lógico no final, **TRUE** ou **FALSE**.

Podemos imaginar essa máquina como uma calculadora reversa (*stack machine*).

Ela possui uma pilha, uma estrutura em que os dados são empilhados e desempilhados conforme cada **opcode** é executado.

Não há variáveis, loops nem funções, apenas uma sequência de instruções que manipulam a pilha.

Cada node da rede executa exatamente as mesmas etapas:

1. Empilha os dados do `scriptSig`;
2. Aplica as operações do `scriptPubKey`;
3. E verifica se o resultado final no topo da pilha é verdadeiro (`TRUE`).

Se for, o gasto é considerado válido.

Se não for, a transação é rejeitada.

Esse processo é o coração da verificação no Bitcoin: um código mínimo que, ao ser reproduzido de forma idêntica em milhares de máquinas ao redor do mundo, **cria consenso** sem precisar de confiança entre as partes.

### Anatomia da Pilha de Execução

A **pilha** é o coração da execução de scripts no Bitcoin.

Cada node mantém uma pequena estrutura de dados onde valores são empilhados (*push*) e desempilhados (*pop*) conforme os **opcodes** são processados. Essa pilha segue a regra **LIFO (*Last In, First Out)***: o último elemento inserido é sempre o primeiro a ser removido.

Diferente de linguagens de programação tradicionais, o Bitcoin Script não usa variáveis, funções ou memória persistente. Toda a lógica acontece dentro dessa pilha temporária. Quando o script termina, ela deve conter **apenas um valor**, e esse valor deve ser **TRUE** para que o node aceite a transação.

---

### 🧮 Exemplo 1

Um script aritmético simples:

```bash
OP_2 OP_3 OP_ADD
```

1. `OP_2` empilha o número 2 → `[2]`
2. `OP_3` empilha o número 3 → `[2, 3]`
3. `OP_ADD` soma os dois valores do topo → `[5]`

✅ **Resultado final da pilha:** `[5]`

---

### 🧩 Exemplo 2

Um script lógico:

```bash
OP_TRUE OP_FALSE OP_BOOLAND
```

1. `OP_TRUE` empilha o valor verdadeiro → `[TRUE]`
2. `OP_FALSE` empilha o valor falso → `[TRUE, FALSE]`
3. `OP_BOOLAND` realiza o “E lógico” entre os dois valores do topo → `[FALSE]`

❌ **Resultado final:** `[FALSE]`

Esses exemplos mostram a essência da máquina de execução do Bitcoin:

cada comando atua sobre o topo da pilha, e o resultado é sempre **explícito, determinístico e verificável**.

---

### ⚙️ Pilha Principal e Pilha Alternativa

Além da pilha principal, o Bitcoin Script também mantém uma **pilha alternativa**, usada em alguns **opcodes de controle de fluxo**, como `OP_IF`, `OP_ELSE` e `OP_ENDIF`.

Ela funciona como um pequeno “buffer” auxiliar, mas não é usada em scripts de transação comuns (como P2PKH).

A maior parte das operações acontece exclusivamente na pilha principal, simples, direta e previsível.

💡 A beleza desse modelo está na transparência: qualquer pessoa pode reproduzir manualmente as mesmas operações e chegar ao mesmo resultado que todos os nodes da rede.

---

### Os opcodes em ação

Abaixo, vemos **como a pilha se transforma** quando aplicamos os opcodes mais importantes. Lembrando que a notação usa o **topo da pilha à direita**.

### 🔁 Manipulação de pilha

**OP_DUP** — duplica o topo

```bash
Antes:  [assinatura, chave_publica]
Aplica: OP_DUP
Depois: [assinatura, chave_publica, chave_publica]
```

**OP_DROP** — remove o topo

```bash
Antes:  [X, Y]
Aplica: OP_DROP
Depois: [X]
```

**OP_SWAP** — troca os dois do topo

```bash
Antes:  [X, Y]
Aplica: OP_SWAP
Depois: [Y, X]
```

**OP_OVER** — copia o segundo elemento para o topo

```bash
Antes:  [X, Y]
Aplica: OP_OVER
Depois: [X, Y, X]
```

---

### 🔐 Validação (hash, igualdade e assinatura)

**OP_HASH160** — aplica SHA256 depois RIPEMD160 no topo

```bash
Antes:  [assinatura, chave_publica]
Aplica: OP_HASH160
Depois: [assinatura, HASH160(chave_publica)]
```

**OP_EQUAL** — compara os dois do topo, retira os 2 elementos e empilha TRUE/FALSE

```bash
Antes:  [A, B]
Aplica: OP_EQUAL
Depois: 
Se A == B:
[TRUE]
Senão
[FALSE]
```

**OP_EQUALVERIFY** — igual ao OP_EQUAL, mas **falha** se for FALSE

```bash
Antes:  [HASH160(pubkey), pubKeyHash_esperado]
Aplica: OP_EQUALVERIFY
Depois: []         (continua, retirando os 2 elementos se iguais; aborta se diferentes)
```

**OP_CHECKSIG** — consome assinatura e chave pública; verifica assinatura da tx

```bash
Antes:  [assinatura, chave_publica]
Aplica: OP_CHECKSIG
Depois: [TRUE]     (ou [FALSE], se inválida)
```

---

### 🧪 Microexemplos encadeados (estilo “máquina da pilha”)

**P2PKH (núcleo da verificação)**

```bash
<assinatura> <chave_publica> OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG

1) push assinatura                      → [assinatura]
2) push chave_publica                    → [assinatura, chave_publica]
3) OP_DUP                                → [assinatura, chave_publica, chave_publica]
4) OP_HASH160                            → [assinatura, chave_publica, HASH160(chave_publica)]
5) push <pubKeyHash>                     → [assinatura, chave_publica, HASH160(pub), pubKeyHash]
6) OP_EQUALVERIFY                        → [assinatura, chave_publica]   (falha se ≠)
7) OP_CHECKSIG                           → [TRUE]
```

### 🧪 Comparações dentro da pilha

Nem sempre queremos apenas verificar e encerrar a execução.

Em alguns casos, é útil **comparar valores sem perder os dados originais,** por exemplo, quando o resultado de uma checagem será usado em uma operação seguinte.

É aí que entram combinações como `OP_OVER OP_EQUAL`:

```bash
Antes:  [X, Y]
Aplica: OP_OVER OP_EQUAL
Depois: [X, TRUE]  (se forem iguais)
```

O `OP_OVER` duplica o segundo elemento da pilha (o `X`), e o `OP_EQUAL` faz a comparação entre os dois últimos (`Y` e `X`).

O resultado lógico (`TRUE` ou `FALSE`) fica no topo, **preservando o primeiro valor**, pronto para ser usado nas próximas operações.

Esse tipo de construção mostra como o Bitcoin Script, mesmo com instruções simples, permite criar **lógicas de decisão controladas** sem variáveis, apenas empilhando e manipulando dados.

---

Podemos ver mais alguns exemplos. Esses scripts não estão ligados a transações reais, eles servem apenas para demonstrar a **lógica pura** do Bitcoin Script, como se estivéssemos observando o interpretador linha por linha.

Cada comando atua sobre o topo da pilha, empilhando ou removendo elementos até chegar a um resultado final.

---

### 🧩 Exemplos práticos

| Script | Resultado esperado | Explicação |
| --- | --- | --- |
| `OP_TRUE` | `[TRUE]` | Empilha o valor lógico verdadeiro. |
| `OP_FALSE OP_NOT` | `[TRUE]` | Empilha `FALSE`, depois inverte com `OP_NOT`. |
| `5 5 OP_EQUAL` | `[TRUE]` | Compara dois valores iguais. |
| `5 4 OP_EQUAL` | `[FALSE]` | Compara valores diferentes. |
| `OP_2 OP_3 OP_ADD 5 OP_EQUAL` | `[TRUE]` | Soma `2 + 3`, compara o resultado com `5`. |

Esses exemplos mostram que cada transação é, na prática, uma execução previsível e determinística, sem loops, sem variáveis, sem mistério.

Quando um node executa um script de verdade (como no caso de um P2PKH), ele apenas repete essa mesma lógica: empilhar, processar e verificar se o resultado final é **TRUE**.

---

## Explorando scripts em simuladores

Nesta etapa, vamos **experimentar scripts simples diretamente em um simulador de scripts** ([siminchen.github.io/bitcoinIDE](https://siminchen.github.io/bitcoinIDE)).

A ferramenta permite simular o comportamento da pilha e visualizar o efeito de cada opcode, ajudando a compreender como o Bitcoin processa instruções lógicas e aritméticas em transações.

Os exemplos a seguir podem ser colados diretamente no editor e executados clicando em **Run** ou então passo-a-passo clicando em **Step**.

---

### 🧩 Exemplo 1 — Soma e comparação

**Script:**

```bash
OP_2 OP_3 OP_ADD 5 OP_EQUAL
```

![Artigo12-img2.webp](../assets/Artigo12-img2.webp)

**Execução passo a passo:**

1. `OP_2` → empilha o número 2 → `[2]`
2. `OP_3` → empilha o número 3 → `[2, 3]`
3. `OP_ADD` → soma os dois valores do topo → `[5]`
4. `5` → empilha o número 5 → `[5, 5]`
5. `OP_EQUAL` → compara → `[TRUE]`

**Resultado final:** `[TRUE]`

Esse script demonstra como o Bitcoin Script executa operações determinísticas sobre valores.

---

### 🔁 Exemplo 2 — Comparando sem perder o valor original

**Script:**

```bash
17 17 OP_OVER OP_EQUAL
```

![Artigo12-img3.webp](../assets/Artigo12-img3.webp)

**Execução passo a passo:**

1. `17` → `[17]`
2. `17` → `[17, 17]`
3. `OP_OVER` → duplica o segundo elemento → `[17, 17, 17]`
4. `OP_EQUAL` → compara os dois do topo → `[17, TRUE]`

**Resultado final:** `[17, TRUE]`

Aqui o uso de `OP_OVER` permite comparar dois elementos sem perder o valor original.

Esse tipo de operação é útil em scripts que precisam verificar igualdade mas continuar processando o dado original.

---

### 🔒 Exemplo 3 — Simulando o cadeado de um P2PKH

**Script:**

```bash
022cb7fcfb1377e85e3c5ac300028890059ff84e9d8e1b6f35a808ebf3e477e7f1 OP_DUP OP_HASH160 AD28C4C54C4084A74E944B8E60916910FB9089B3 OP_EQUALVERIFY
```

![Artigo12-img4.webp](../assets/Artigo12-img4.webp)

**Execução passo a passo:**

1. Empilha a chave pública (aqui representada em texto).
2. `OP_DUP` duplica o topo da pilha → `[pubkey, pubkey]`
3. `OP_HASH160` calcula o hash do topo → `[pubkey, HASH160(pubkey)]`
4. Empilha o hash esperado (`AD28C4C5...`) → `[pubkey, HASH160(pubkey), AD28C4C5...]`
5. `OP_EQUALVERIFY` compara os dois últimos valores → `[pubkey]` (continua se iguais)

**Resultado final:** `[pubkey]`

Esse script representa o “cadeado” clássico de um endereço P2PKH, onde o Bitcoin verifica se a chave pública apresentada corresponde ao hash registrado no output.

---

### ⚠️ Observação importante

O simulador **Bitcoin IDE** trata todos os dados como **texto ASCII**, e não como bytes binários.

Por isso, o hash gerado para a chave pública acima (`AD28C4C5...`) é o `HASH160` da *string textual* `"022cb7..."`, e não da chave pública real.

No ambiente do Bitcoin Core, o mesmo dado binário produziria o hash verdadeiro:

`90283BCC2BF2BEAE3BCEC2B9B451C209225B89C9`.

Essa diferença não invalida o experimento, ela apenas reforça que o IDE é uma ferramenta **didática**, ideal para entender a lógica da pilha, mesmo que não reproduza fielmente os bytes da rede real.

---

Ao observar a pilha em ação, fica evidente que o **Bitcoin Script** é muito mais do que um mecanismo de validação: ele é uma linguagem minimalista capaz de expressar lógica condicional e controle de acesso diretamente na camada base da rede.Nos exemplos deste artigo, vimos como operações simples como duplicar, comparar e verificar assinaturas, formam a base de segurança de todo o sistema.

No **próximo artigo**, vamos **expandir essa lógica** para scripts mais complexos, que envolvem múltiplas chaves e restrições temporais. Exploraremos instruções como `OP_CHECKMULTISIG`, `OP_CHECKLOCKTIMEVERIFY`, `OP_CHECKSEQUENCEVERIFY` e estruturas condicionais (`OP_IF`, `OP_ELSE`, `OP_ENDIF`), aprendendo como o Bitcoin permite criar **contratos base** sem precisar sair da sua própria camada fundamental.

Esses blocos de construção são o primeiro passo para compreender como o protocolo dá origem a formas mais avançadas de interação, como a Lightning Network e os contratos inteligentes sobre Taproot.
