# Scripts Condicionais e Contratos Base

por Rafael Santos

 No artigo anterior, vimos o **Bitcoin Script** em sua forma mais essencial, uma pilha que processa operações e decide, passo a passo, se uma transação é válida. Agora, daremos um passo além: veremos como essa mesma pilha pode representar **regras de gasto**.

Cada transação Bitcoin é, na prática, um **pequeno programa** que deve terminar sua execução com o resultado `TRUE`. Isso garante que todos os nodes cheguem à mesma conclusão ao validar uma transação, sem precisar de intermediários.

Mesmo sem ser uma linguagem completa como as de propósito geral, o **Bitcoin Script** é expressivo o suficiente para descrever **quem pode gastar, quando e sob quais condições**.

Ele usa instruções simples (**opcodes)** para criar combinações lógicas como:

- “se X e Y assinarem, o gasto é válido” (`AND`);
- “se o prazo ainda não passou, use esta regra; senão, use outra” (`IF` / `ELSE`);
- “só aceite a transação se o tempo for maior que N” (`CHECKLOCKTIMEVERIFY`).

---

💡 **Experimento rápido com o Bitcoin Core**

Mesmo sem construir uma transação completa, podemos **testar scripts isolados** diretamente no Bitcoin Core, usando o comando `decodescript`.

Esse comando interpreta um script em formato **hexadecimal** e mostra sua forma legível (ASM), além dos endereços correspondentes.

Exemplo: um script que usa `OP_IF` e `OP_ELSE` para decidir entre duas condições.

```bash
bitcoin-cli -regtest decodescript "6351670068"
```

Saída:

```json
{
  "asm": "OP_IF 1 OP_ELSE 0 OP_ENDIF",
  "desc": "raw(6351670068)#fhsnu8qg",
  "type": "nonstandard",
  "p2sh": "2N93YqRsiWUkZUEyMcb55hEZgwLY25qoncN",
  "segwit": {
    "asm": "0 5a675dfcc938bd86227554f49be874165554f232d0b1695c4bd930a3ea55503f",
    "desc": "addr(tb1qtfn4mlxf8z7cvgn42n6fh6r5ze24fu3j6zckjhztmyc286j42qlsyv9tnx)#wjp4xrj9",
    "hex": "00205a675dfcc938bd86227554f49be874165554f232d0b1695c4bd930a3ea55503f",
    "address": "tb1qtfn4mlxf8z7cvgn42n6fh6r5ze24fu3j6zckjhztmyc286j42qlsyv9tnx",
    "type": "witness_v0_scripthash",
    "p2sh-segwit": "2NGSAJicABGCR6h7VrHCFS28Pg8XVAzK28Y"
  }
}
```

O campo `"asm"` mostra o script em formato legível, enquanto `"p2sh"` e `"segwit"` exibem os **endereços derivados** que poderiam receber fundos com base nesse script.

Isso permite que qualquer desenvolvedor **teste, verifique e visualize** scripts personalizados antes de aplicá-los em uma transação real.

Para entender melhor, esse script é composto pelos seguintes bytes e instruções:

| Hex | Opcode | Função |
| --- | --- | --- |
| `63` | **OP_IF** | Verifica o topo da pilha: se for diferente de zero (`TRUE`), executa o bloco seguinte até `OP_ELSE`; caso contrário, pula para depois de `OP_ELSE`. |
| `51` | **OP_TRUE** | Coloca o valor lógico `TRUE` (equivalente a `1`) na pilha. |
| `67` | **OP_ELSE** | Define o início do bloco alternativo (executado se a condição for `FALSE`). |
| `00` | **OP_FALSE** | Coloca o valor lógico `FALSE` (equivalente a `0`) na pilha. |
| `68` | **OP_ENDIF** | Encerra a estrutura condicional iniciada por `OP_IF`. |

🔍 **Em resumo:**

O script completo significa:

```
SE (condição verdadeira)
    empilha TRUE
SENÃO
    empilha FALSE
FIM
```

Na prática, ele é um pequeno **programa condicional**, que sempre empilha `1` ou `0` dependendo da condição avaliada — um excelente exemplo introdutório de **controle de fluxo no Bitcoin Script**.

---

### Multisig com `OP_CHECKMULTISIG`

Um dos recursos mais poderosos do Bitcoin Script é a possibilidade de exigir **múltiplas assinaturas** para liberar fundos. Em vez de depender de uma única chave privada, um endereço *multisig* (“multi-assinatura”) combina várias chaves públicas em uma mesma regra de gasto. Isso permite criar carteiras compartilhadas, cofres de segurança e até sistemas de governança descentralizada.

Em termos simples:

> “Um endereço multisig exige que m de n participantes assinem para que o gasto seja considerado válido.”
> 

Por exemplo, um **2-de-3 multisig** significa que qualquer duas das três chaves registradas podem movimentar os fundos.

---

### 🧠 Estrutura geral do script

O formato do script multisig é o seguinte:

```bash
<m> <pubkey1> <pubkey2> <pubkey3> <n> OP_CHECKMULTISIG
```

Onde:

- `<m>` é o número mínimo de assinaturas exigidas;
- `<n>` é o número total de chaves envolvidas;
- `OP_CHECKMULTISIG` verifica se as assinaturas fornecidas realmente correspondem às chaves declaradas.

Um exemplo de 2-de-3 seria:

```bash
OP_2 <pubkey1> <pubkey2> <pubkey3> OP_3 OP_CHECKMULTISIG
```

---

### 💻 Exemplo prático com o Bitcoin Core

Vamos criar e inspecionar um endereço multisig diretamente no terminal (modo `signet`):

1. **Criar 3 novos endereços:**
    
    ```bash
    bitcoin-cli -datadir="." -rpcwallet=signetwallet getnewaddress
    # tb1qge4dzkxfphnuke75evgavsg5hzv8yepp5zcp27
    
    bitcoin-cli -datadir="." -rpcwallet=signetwallet getnewaddress
    # tb1qcxy5ygmsj2fnrt082y09esdn5ya4k7jdwztdjn
    
    bitcoin-cli -datadir="." -rpcwallet=signetwallet getnewaddress
    # tb1qdnf9w7u235vvqag3cfqzjupzsg2y3646fm2mpd
    ```
    
2. **Obter as `pubkey` dos 3 endereços:**

```bash
bitcoin-cli -datadir="." -rpcwallet=signetwallet getaddressinfo tb1qge4dzkxfphnuke75evgavsg5hzv8yepp5zcp27
{
  ...,
  "pubkey": "0276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df6213",
  ...
}

bitcoin-cli -datadir="." -rpcwallet=signetwallet getaddressinfo tb1qcxy5ygmsj2fnrt082y09esdn5ya4k7jdwztdjn
{
...,
  "pubkey": "020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3",
}

bitcoin-cli -datadir="." -rpcwallet=signetwallet getaddressinfo tb1qdnf9w7u235vvqag3cfqzjupzsg2y3646fm2mpd
{
...,
  "pubkey": "0202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe52",
}

```

O comando `getaddressinfo`  mostrará, entre outros dados, o campo `"pubkey"`, que é a chave pública associada ao endereço.

3. **Criar o script multisig (2-de-3):**

Podemos utilizar o comando `createmultisig` para criar o script multisig a partir das 3 `pubkey.`

```bash
bitcoin-cli -datadir="." createmultisig 2 '["0276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df6213","020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3","0202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe52"]'

{
  "address": "2N2iqBAJvyKA2zzhHGUFPwbufqzNs3vGKJo",
  "redeemScript": "52210276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df621321020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3210202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe5253ae",
  "descriptor": "sh(multi(2,0276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df6213,020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3,0202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe52))#gdaf5m8n"
}
```

- O campo `"address"` é o endereço **P2SH multisig,** o destino onde os bitcoins podem ser enviados.
- O campo `"redeemScript"` contém o **script de bloqueio real**, em formato hexadecimal.

Ao decodificar esse script com:

```bash
bitcoin-cli -datadir="." decodescript "52210276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df621321020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3210202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe5253ae"
{
  "asm": "2 0276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df6213 020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3 0202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe52 3 OP_CHECKMULTISIG",
  "desc": "multi(2,0276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df6213,020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3,0202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe52)#lugfm7u3",
  "type": "multisig",
  "p2sh": "2N2iqBAJvyKA2zzhHGUFPwbufqzNs3vGKJo",
  "segwit": {
    "asm": "0 b69f95a35df8ab1b1b924f8e5f7ceecb230d7ee5318c0efd0a2ec2988c2d99f5",
    "desc": "wsh(multi(2,0276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df6213,020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3,0202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe52))#rex36vz8",
    "hex": "0020b69f95a35df8ab1b1b924f8e5f7ceecb230d7ee5318c0efd0a2ec2988c2d99f5",
    "address": "tb1qk60etg6alz43kxujf7897l8wev3s6lh9xxxqalg29mpf3rpdn86stxeawe",
    "type": "witness_v0_scripthash",
    "p2sh-segwit": "2MxnLjcU2FdCiFqur7R7XD4PFDWd4vXcRfB"
  }
}
```

A saída mostrará o ASM correspondente:

```bash
2 0276d4d259f156bc953231ae2365555c9a445d50f40e0f9d49f43b062a38df6213 020498177dced0022d4538f0b39a09d315ec944c7205307dc126af8f132975cae3 0202835b62db105222c0d5208b31189660bd8a2f636d25d91329f73be56282fe52 3 OP_CHECKMULTISIG
```

Perceba que é exatamente o formato de script multisig:

```bash
OP_2 <pubkey1> <pubkey2> <pubkey3> OP_3 OP_CHECKMULTISIG
```

---

### 🧩 Entendendo o papel de `OP_CHECKMULTISIG`

O `OP_CHECKMULTISIG` é o responsável por comparar cada assinatura apresentada (`scriptSig`) com as chaves públicas listadas no script.

**RedeemScript (cadeado):**

```bash
OP_2 <pubkey1> <pubkey2> <pubkey3> OP_3 OP_CHECKMULTISIG
```

**ScriptSig (chave):**

```bash
OP_0 <assinatura1> <assinatura2>
```

Quando os dois são concatenados e executados, a pilha evolui assim:

| Etapa | Operação executada | Estado da pilha | Observação |
| --- | --- | --- | --- |
| **1** | Empilha `OP_0` (dummy) e as duas assinaturas | `[OP_0, assinatura1, assinatura2]` | O `OP_0` é necessário por um bug histórico. |
| **2** | Empilha `OP_2` (número de assinaturas requeridas) | `[OP_0, assinatura1, assinatura2, 2]` | O valor 2 indica que duas assinaturas devem ser válidas. |
| **3** | Empilha três chaves públicas e `OP_3` | `[OP_0, assinatura1, assinatura2, 2, pubkey1, pubkey2, pubkey3, 3]` | Agora há 3 chaves públicas e o total de chaves `n = 3`. |
| **4** | Executa `OP_CHECKMULTISIG` | `[TRUE]` | O opcode verifica se pelo menos 2 assinaturas são válidas para as 3 chaves. Retorna `TRUE` se sim. |

---

🧠 **O que acontece “por dentro” do `OP_CHECKMULTISIG`:**

1. Lê o número de chaves públicas (`n`), retira-as da pilha.
2. Lê o número de assinaturas (`m`), retira-as também.
3. Compara cada assinatura com as chaves disponíveis.
4. Retorna `TRUE` se encontrar ao menos `m` correspondências válidas.

---

---

### Timelocks

Como vimos em artigos anteriores, nem toda regra de gasto depende apenas de quem tem a chave. Ás vezes, depende também **de quando** os fundos podem ser gastos.

É aqui que entram os **timelocks**: mecanismos que bloqueiam uma transação até um ponto específico no tempo ou altura de bloco.

### 🔸 `OP_CHECKLOCKTIMEVERIFY` (CLTV): bloqueio no script

Enquanto `nLockTime` (também visto em artigo anterior) atua no nível da transação, o `OP_CHECKLOCKTIMEVERIFY` (ou **CLTV**) age diretamente no **script de bloqueio**.

Com ele, é possível dizer:

> “Esses bitcoins só podem ser gastos depois do bloco X (ou depois da data Y).”
> 

O formato geral é:

```bash
<blockheight> OP_CHECKLOCKTIMEVERIFY OP_DROP <script_normal>
```

- `<timestamp>` ou `<blockheight>` define o ponto mínimo de liberação.
- `OP_CHECKLOCKTIMEVERIFY` verifica se a transação respeita esse limite.
- `OP_DROP` remove o valor da pilha (pois já foi verificado).
- O restante do script (`<script_normal>`) é então executado normalmente.

---

### 💻 Exemplo prático: bloqueio até o bloco 300.000

Vamos criar um script que só pode ser gasto **a partir do bloco 300.000**. Lembre que o `decodescript` interpreta um script em formato **hexadecimal** 

```bash
bitcoin-cli -datadir="." decodescript "03e09304b17551"
```

Saída:

```json
{
  "asm": "300000 OP_CHECKLOCKTIMEVERIFY OP_DROP 1",
  "desc": "raw(03e09304b17551)#pll48me7",
  "type": "nonstandard",
  "p2sh": "2MuHsVSqmSpoddRxrDoAbpP6Jya38pDNFid",
  "segwit": {
    "asm": "0 0b86eaa54b486b835452603ece907a856b5770e8dc2df9e189d991ee296b4639",
    "desc": "addr(tb1qpwrw4f2tfp4cx4zjvqlvayr6s444wu8gmsklncvfmxg7u2ttgcus2kqnd5)#6q4h0ctd",
    "hex": "00200b86eaa54b486b835452603ece907a856b5770e8dc2df9e189d991ee296b4639",
    "address": "tb1qpwrw4f2tfp4cx4zjvqlvayr6s444wu8gmsklncvfmxg7u2ttgcus2kqnd5",
    "type": "witness_v0_scripthash",
    "p2sh-segwit": "2MutdmQihXZr3TXc8bYnc1oVyAeQs1iEyf6"
  }
}
```

Nesse exemplo:

- O **`asm`** mostra a sequência de opcodes do script.
- O **`p2sh`** e o **`segwit.address`** são endereços válidos para receber fundos que respeitam essa regra.

Se você enviar bitcoins para o endereço `2MuHsVS...` e tentar gastar antes do bloco 300.000, o node rejeitará a transação com erro semelhante a:

```
non-BIP68-final: locktime requirement not satisfied
```

Após o bloco 300.000, a condição é satisfeita, o script retorna `TRUE`, e os fundos podem ser movimentados normalmente.

---

Os timelocks permitem criar **contratos baseados em tempo**, como depósitos com prazo ou mecanismos de fallback (“se ninguém gastar até X blocos, libera para outro endereço”). Eles são a base de mecanismos usados em soluções avançadas como **Lightning Network**.

---

## Estruturas condicionais: OP_IF / OP_ELSE / OP_ENDIF

Os scripts do Bitcoin não possuem *loops* nem variáveis, mas permitem **decisões condicionais** com os opcodes `OP_IF`, `OP_ELSE` e `OP_ENDIF`.

Com eles, é possível criar **contratos que escolhem entre dois caminhos de execução,** como “se A assinar, paga para X; senão, paga para Y”.

Cada condição é controlada pelo **valor no topo da pilha**:

- se `TRUE` → executa o bloco entre `OP_IF` e `OP_ELSE` (ou até `OP_ENDIF` se não houver `ELSE`),
- se `FALSE` → ignora esse bloco e executa o trecho após `OP_ELSE`.

---

### 💻 Exemplo prático

Vamos decodificar um script simples com duas possibilidades:

```bash
bitcoin-cli -datadir="." decodescript "6351670068"
```

Saída resumida:

```json
{
  "asm": "OP_IF 1 OP_ELSE 0 OP_ENDIF",
  "desc": "raw(6351670068)#fhsnu8qg",
...
}
```

---

### 🧠 Interpretação

- `63` → `OP_IF`
- `51` → `OP_TRUE`
- `67` → `OP_ELSE`
- `00` → `OP_FALSE`
- `68` → `OP_ENDIF`

Esse script executa assim:

| Valor no topo da pilha | Caminho executado | Resultado final |
| --- | --- | --- |
| `[TRUE]` | executa bloco entre `OP_IF` e `OP_ELSE` | `[TRUE]` |
| `[FALSE]` | ignora o primeiro bloco e executa após `OP_ELSE` | `[FALSE]` |

Com essa estrutura, é possível criar scripts do tipo:

- “Se Alice assinar → envia para X; senão → retorna para Bob após N blocos”
- “Se o oráculo confirmar o evento → paga a parte vencedora”

Esses são os **blocos fundamentais de contratos condicionais** no Bitcoin.

---

### Script dual

Agora que já dominamos **multisig**, **timelocks** e **condições com IF/ELSE**, podemos combinar tudo em um **contrato Bitcoin completo**, que representa **duas possibilidades exclusivas de gasto**, controladas por tempo e assinatura.

> 🔸 Antes do bloco 273100 → A pode gastar.
> 
> 
> 🔸 Depois do bloco 273100 → **B** pode gastar.
> 

É um exemplo real de contrato condicional e temporal, diretamente na camada base do Bitcoin.

---

### 🧠 Estrutura do script

```bash
OP_IF
  036ae41e66b25bab55932a82b0f523d078158c98a0a0d60326bc6a83e370bbe35f OP_CHECKSIGVERIFY 273100 OP_CHECKLOCKTIMEVERIFY OP_DROP
OP_ELSE
  0307b4825b0ad5ce1dd42b0cf2d9add5305e07d9eb76105f7bc130c0cac5bce70f OP_CHECKSIG
OP_ENDIF
```

Esse script exige:

- **assinatura de A** (`036ae41e...`) antes do bloco 273100;
- ou **assinatura de B** (`0307b482...`) depois desse bloco.

---

### 💻 Decodificando o script

Convertendo o script para hexadecimal:

```bash
6321036ae41e66b25bab55932a82b0f523d078158c98a0a0d60326bc6a83e370bbe35fac03cc2a04b17567210307b4825b0ad5ce1dd42b0cf2d9add5305e07d9eb76105f7bc130c0cac5bce70fac68
```

Agora, podemos decodificá-lo com o Bitcoin Core:

```bash
bitcoin-cli -datadir="." decodescript "6321036ae41e66b25bab55932a82b0f523d078158c98a0a0d60326bc6a83e370bbe35fac03cc2a04b17567210307b4825b0ad5ce1dd42b0cf2d9add5305e07d9eb76105f7bc130c0cac5bce70fac68"
```

Saída resumida:

```json
{
  "asm": "OP_IF 036ae41e66b25bab55932a82b0f523d078158c98a0a0d60326bc6a83e370bbe35f OP_CHECKSIG 273100 OP_CHECKLOCKTIMEVERIFY OP_DROP OP_ELSE 0307b4825b0ad5ce1dd42b0cf2d9add5305e07d9eb76105f7bc130c0cac5bce70f OP_CHECKSIG OP_ENDIF",
  ...
}
```

---

### ⚙️ Interpretação da execução

**🔹 Caminho 1 — [TRUE] → antes do bloco 273100 (assinatura de A)**

| Etapa | Operação | Pilha (topo à direita) | Descrição |
| --- | --- | --- | --- |
| 1 | `PUSH TRUE` | `[TRUE]` | Valor condicional inicial |
| 2 | `OP_IF` | `[]` | Entra no ramo `IF` |
| 3 | `PUSH <assinatura_A>` | `[assinatura_A]` | A assinatura é empilhada |
| 4 | `PUSH <pubkey_A>` | `[assinatura_A, pubkey_A]` | Empilha a chave pública de A |
| 5 | `OP_CHECKSIGVERIFY` | `[]` | Verifica assinatura de A — se inválida → falha |
| 6 | `PUSH 273100` | `[273100]` | Empurra o limite de bloco |
| 7 | `OP_CHECKLOCKTIMEVERIFY` | `[273100]` | Compara o nLockTime da transação: deve ser ≥ 273100 |
| 8 | `OP_DROP` | `[]` | Remove o número do topo (não precisa mais) |
| **Resultado final** |  | `[TRUE]` | Script retorna verdadeiro — gasto autorizado por A |

---

**🔹 Caminho 2 — [FALSE] → após o bloco 273100 (assinatura de B)**

| Etapa | Operação | Pilha (topo à direita) | Descrição |
| --- | --- | --- | --- |
| 1 | `PUSH FALSE` | `[FALSE]` | Valor condicional inicial |
| 2 | `OP_IF` | `[]` | Pula o bloco `IF` e executa `ELSE` |
| 3 | `PUSH <assinatura_B>` | `[assinatura_B]` | Empilha a assinatura de B |
| 4 | `PUSH <pubkey_B>` | `[assinatura_B, pubkey_B]` | Empilha a chave pública de B |
| 5 | `OP_CHECKSIG` | `[TRUE]` | Verifica a assinatura de B |
| **Resultado final** |  | `[TRUE]` | Script retorna verdadeiro — gasto autorizado por B |

---

**Resumindo**:

| Condição | Caminho executado | Regras aplicadas | Gasto permitido |
| --- | --- | --- | --- |
| `[TRUE]` (antes do bloco 273100) | `IF` | Assinatura de **A** válida + CLTV válido | ✅ A |
| `[FALSE]` (depois do bloco 273100) | `ELSE` | Assinatura de **B** válida | ✅ B |

Esse contrato é **simples, auditável e executável em qualquer node Bitcoin**, sem precisar de Taproot ou camadas extras.

---

Os exemplos vistos ao longo deste artigo mostram que, mesmo com um conjunto reduzido de opcodes, o **Bitcoin Script** é capaz de expressar regras complexas de custódia e de confiança mínima. Multisigs, timelocks e estruturas condicionais formam a base dos chamados **contratos inteligentes nativos do Bitcoin.** São scripts verificáveis, transparentes e imutáveis, executados por cada node da rede sem depender de intermediários. Essa simplicidade é, ao mesmo tempo, o limite e a força do protocolo: ao restringir o escopo das operações, o Bitcoin garante segurança, previsibilidade e durabilidade, permitindo que contratos como o “dual script” sejam reproduzidos e validados em qualquer parte do mundo, compatíveis com o consenso da rede.
