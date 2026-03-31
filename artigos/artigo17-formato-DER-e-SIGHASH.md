# O formato DER e o SIGHASH nas assinaturas Bitcoin

Como vimos no artigo anterior, quando uma assinatura ECDSA é produzida, o resultado bruto é apenas um par de números inteiros (**r** e **s)**. Esses valores representam a prova matemática de que a chave privada foi usada para autorizar uma transação, mas, por si só, eles **não têm forma definida**: podem ter tamanhos variáveis, precisarem de bytes extras para evitar sinal negativo, ou não ter separação clara entre os dois componentes.

Para que essa assinatura possa circular entre nós, ser armazenada em blocos e interpretada de maneira consistente por implementações diferentes, ela precisa ser **serializada** em um formato padronizado e rígido. Esse é exatamente o papel do **DER (Distinguished Encoding Rules)**, um subconjunto estrito de codificação ASN.1 amplamente utilizado em criptografia e especificado por normas RFC.

Ao adotar o formato DER, o Bitcoin ganha três propriedades fundamentais:

1. **Interoperabilidade**
    
    Qualquer software que implemente ASN.1 DER é capaz de interpretar a assinatura sem ambiguidade.
    
2. **Validação binária rígida**
    
    A estrutura DER impõe limites claros sobre o tamanho permitido dos campos, evita inteiros com bytes extras e impede variações de formato que poderiam causar vulnerabilidades.
    
3. **Padronização no protocolo**
    
    Todos os nós da rede veem a assinatura exatamente da mesma forma, byte por byte, o que é essencial para o consenso.
    

Em outras palavras, o DER transforma o par `(r, s)` em um **pacote binário canônico**, garantindo que a assinatura seja representada sempre da mesma maneira, independentemente da implementação. É esse pacote estruturado que, mais tarde, será anexado ao `scriptSig` (ou ao `witness`) junto com o byte de **SIGHASH**, formando a assinatura final usada pelo Bitcoin para validar o gasto de um UTXO.

### Estrutura do DER

Uma assinatura ECDSA bruta é o par de inteiros `(r, s)`.

No Bitcoin, esses dois valores são empacotados em **ASN.1 DER** com a seguinte estrutura:

```
30 <len_total>
   02 <len_r> <r_em_big_endian>
   02 <len_s> <s_em_big_endian>
```

- `30` → indica que vem uma **SEQUENCE**.
- cada `02` → indica um **INTEGER**.
- os bytes `<len_*>` → dizem quantos bytes vêm a seguir para aquele campo.

Vamos usar um exemplo real de assinatura extraída de um `scriptSig` P2PKH (retirando os opcodes de push e o byte de SIGHASH no final):

```
30 44 02 20
59 00 c1 0f 73 c2 39 b7 d7 31 ec 70 4d c1 19 37
bf f3 bc bb 56 09 42 14 c8 0c 5e 6d 73 fe 8f 70
02 20
30 75 6b ad 8a 00 a9 e1 f2 b9 71 d6 85 1e ab f3
cf 06 89 c2 7b 55 d3 ef b8 b1 94 1b 0d 59 da fb
```

Vamos linha por linha.

**Cabeçalho da SEQUENCE**

```
30 44
```

- `30` → tipo **SEQUENCE** (estrutura composta em ASN.1).
- `44` (decimal 68) → comprimento total, em bytes, da sequência que vem depois:
    - `02 20 <32 bytes de r>` (1 + 1 + 32 = 34)
    - `02 20 <32 bytes de s>` (1 + 1 + 32 = 34)
        
        → 34 + 34 = 68 (`0x44`).
        

Ou seja, o DER está dizendo:

> “Vou te entregar uma sequência de 68 bytes, contendo dois inteiros.”
> 

---

**Primeiro INTEGER: o valor r**

Logo após o cabeçalho, vem o primeiro inteiro:

```
02 20
59 00 c1 0f 73 c2 39 b7 d7 31 ec 70 4d c1 19 37
bf f3 bc bb 56 09 42 14 c8 0c 5e 6d 73 fe 8f 70
```

- `02` → tipo **INTEGER**.
- `20` → comprimento do inteiro: 32 bytes.
- os 32 bytes seguintes são o valor de **r**, em **big-endian** (mais significativo primeiro).

Esse bloco inteiro, quando interpretado como um número sem sinal, é exatamente o `r_int` que vimos no código Python do artigo anterior (`sigdecode_der`).

---

**Segundo INTEGER: o valor s**

Em seguida, vem o segundo inteiro:

```
02 20
30 75 6b ad 8a 00 a9 e1 f2 b9 71 d6 85 1e ab f3
cf 06 89 c2 7b 55 d3 ef b8 b1 94 1b 0d 59 da fb
```

- `02` → novamente, tipo **INTEGER**.
- `20` → mais 32 bytes de comprimento.
- os 32 bytes seguintes são o valor de **s**, também em **big-endian**.

Novamente, esse bloco corresponde ao `s_int` do script em Python do artigo anterior.

---

**Por que às vezes aparece um `00` no começo?**

Como o ASN.1 DER usa inteiros **assinados**, o bit mais significativo do primeiro byte indica o sinal:

- se o primeiro byte começa com bit 0 (valor < 0x80), o número é considerado positivo;
- se o primeiro byte começa com bit 1 (valor ≥ 0x80), ele poderia ser interpretado como negativo.

Para garantir que `r` e `s` sejam sempre positivos, o DER permite (e às vezes exige) prefixar um byte `00`:

```
02 21 00 8f ...
```

- `02` → INTEGER
- `21` → 33 bytes de comprimento
- `00` → byte extra apenas para garantir “positivo”
- `8f ...` → 32 bytes reais do número

Regra importante do DER (e que o Bitcoin **exige**):

- **não pode** haver zeros à esquerda desnecessários;
- **pode** existir **um único** zero à esquerda, se for necessário para evitar que o número pareça negativo.

Assinaturas que violam essas regras (por exemplo, com dois zeros à esquerda) são rejeitadas como **não canônicas**.

---

**Lembrando: no script, ainda existe o SIGHASH**

Na transação Bitcoin, o que aparece dentro do `scriptSig` não é só o DER.

É:

```
<push_len> 30 ... <DER> <sighash_byte>
```

Exemplo típico em hex:

```
47
  30 44 02 20 ... 02 20 ...
  01
```

- `47` → opcode de *push* (71 bytes)
- `30 44 ...` → DER com `r` e `s`
- `01` → `SIGHASH_ALL`

No `decoderawtransaction`, isso costuma aparecer assim no campo `asm`:

```
3044...dafb[ALL]
```

O `[ALL]` é justamente a interpretação do byte final `01`.

O **SIGHASH** é responsável por indicar **qual parte da transação foi assinada**.

Os valores mais comuns são:

- `01` → **SIGHASH_ALL**
- `02` → **SIGHASH_NONE**
- `03` → **SIGHASH_SINGLE**
- `81`, `82`, `83` → mesmas três variantes, mas com **ANYONECANPAY** ativado

| SIGHASH | O que protege? | O que pode mudar? | Analogia |
| --- | --- | --- | --- |

| **ALL** | Todos os inputs e outputs | Nada | “Assino o documento inteiro.” |
| --- | --- | --- | --- |

| **NONE** | Inputs apenas | Todos os outputs | “Autorizo gastar, não me importo para onde vai.” |
| --- | --- | --- | --- |

| **SINGLE** | Inputs + apenas *meu* output | Outros outputs | “Assino só **meu** pedaço do contrato.” |
| --- | --- | --- | --- |

Esse byte é essencial porque o ECDSA, por si só, não sabe *o que está sendo assinado,* ele apenas assina um número. O SIGHASH define **como** o Bitcoin monta o *preimage* da transação antes de hasheá-la e enviá-la para o ECDSA.

### Como o Bitcoin calcula o hash que será assinado (preimage)

A assinatura ECDSA não é gerada diretamente sobre a transação em formato hex. O Bitcoin primeiro constrói uma **preimage,** um bloco de dados cuidadosamente montado a partir da estrutura da transação, e só depois aplica **SHA256d** sobre esse conjunto. O resultado desse hash final (`z`) é o número que será assinado pelo ECDSA.

A preimage é a parte mais crítica do processo: **ela define exatamente o que está sendo protegido pela assinatura**.

A preimage é uma **representação interna da transação**, construída com regras específicas:

- alguns campos podem aparecer completos;
- outros podem ser substituídos por zero;
- alguns são omitidos dependendo do tipo de SIGHASH;
- a estrutura muda entre transações legacy, segwit e taproot.

**Preimage no modelo legacy (antes do SegWit)**

O modelo legacy usa um algoritmo irregular e verboso:

- cada input é processado separadamente;
- os scripts dos outros inputs são **removidos**;
- o script do input que está sendo assinado é **inserido inteiro**;
- dependendo do SIGHASH, os outputs podem ser completos, vazios, ou parcialmente zerados.

Esse algoritmo é o mais suscetível à **malleabilidade**, pois pequenas mudanças no `scriptSig` alteram o preimage e mudam o txid.

Caso clássico: **SIGHASH_ALL (01)**

A preimage contém:

- versão
- todos os inputs
- todos os outputs
- locktime
- tipo de sighash

Mas:

- apenas o input atual recebe o **scriptPubKey completo** (do UTXO sendo gasto)
- os outros inputs têm `scriptSig = ""`
- quantidade e sequência são preservadas

Resumo:

```
version
input_count
  input1: prevtxid, vout, scriptPubKeyDoUTXO, sequence
  input2: prevtxid, vout, "",                 sequence
  inputN: ...
output_count
  output1
  output2
  outputN
locktime
sighash_type
```

### Regras de consenso: assinaturas canônicas (low-S)

O Bitcoin não aceita qualquer assinatura válida do ponto de vista puramente matemático. Desde 2015, com o **BIP66**, a rede exige que todas as assinaturas ECDSA sejam **canônicas**, ou seja, sigam regras rígidas de formatação DER. E desde o **BIP62**, passou-se a exigir também a forma **low-S**, eliminando boa parte dos ataques de maleabilidade.

Essas regras não mudam a matemática do ECDSA, elas moldam **como as assinaturas são representadas em bytes**. Em um sistema baseado em consenso, isso é crucial: se versões diferentes da assinatura pudessem existir para a mesma transação, nós diferentes poderiam chegar a *txids* diferentes.

---

**O problema da maleabilidade**

A assinatura ECDSA contém dois inteiros, `r` e `s`.

Matematicamente, **se (r, s) é válido, então (r, n − s) também é**.

Isso significa que existem **duas assinaturas diferentes** para a mesma mensagem.

E, como o `scriptSig` (ou o witness) contém a assinatura *inteira*, mudar `s` para `n − s`:

- altera o DER,
- altera os bytes do input,
- altera o *preimage*,
- altera o txid.

Ou seja:

> A maleabilidade permite que alguém, sem a chave privada, mude o txid da sua transação.
> 

Não é possível roubar fundos assim, mas cria problemas sérios para:

- contratos que dependem do txid,
- transações encadeadas,
- LN (antes do SegWit),
- mempool tracking.

---

**A solução: exigir “low-S”**

Para eliminar essa ambiguidade, o Bitcoin determinou uma regra:

$$
s \le \frac{n}{2}
$$

Se `s` for maior que `n/2`, ele deve ser substituído por `n − s`.

Esse processo é chamado de **normalização low-S**.

Depois disso, só existe **uma única forma canônica** para a assinatura daquela mensagem.

### Exemplo real completo: desmontando um `scriptSig` real

Considere o trecho de `scriptSig` de uma transação P2PKH (Signet/Testnet), visto no `decoderawtransaction`:

```bash
bitcoin-cli -datadir="." decoderawtransaction "02000000010fa9052f266861c4496b81d695dbda14693ff0c525206ad05536df48a3acf575010000006a47304402207e9a79a13fe534bf3c0f319748801ed4c9c3e9c75545f68eaf84d899428abee80220076b60df6fa63dfe8b5411753ef093afa3c3ad6b0918559ae093561b660b61cc012103d6d18224c3648a5a3d74367df185738bf02c82a92b2e7f7c84eb71a59530dda8fdffffff0125030000000000001976a9144e073e0dc8a9b26ae890b503d9c600e914c059d888ac00000000"
```

```bash
"scriptSig": {
  "asm": "304402207e9a79a13fe534bf3c0f319748801ed4c9c3e9c75545f68eaf84d899428abee80220076b60df6fa63dfe8b5411753ef093afa3c3ad6b0918559ae093561b660b61cc[ALL] 03d6d18224c3648a5a3d74367df185738bf02c82a92b2e7f7c84eb71a59530dda8",
  "hex": "47304402207e9a79a13fe534bf3c0f319748801ed4c9c3e9c75545f68eaf84d899428abee80220076b60df6fa63dfe8b5411753ef093afa3c3ad6b0918559ae093561b660b61cc012103d6d18224c3648a5a3d74367df185738bf02c82a92b2e7f7c84eb71a59530dda8"
}
```

Estrutura geral do `scriptSig` em Hex:

```bash
47
  30 44 02 20 7e 9a 79 a1 3f e5 34 bf 3c 0f 31 97 48 80 1e d4 c9 c3 e9 c7 55 45 f6 8e af 84 d8 99 42 8a be e8 02 20 07 6b 60 df 6f a6 3d fe 8b 54 11 75 3e f0 93 af a3 c3 ad 6b 09 18 55 9a e0 93 56 1b 66 0b 61 cc 
01

21
03 d6 d1 82 24 c3 64 8a 5a 3d 74 36 7d f1 85 73 8b f0 2c 82 a9 2b 2e 7f 7c 84 eb 71 a5 95 30  dd a8
```

Interpretando:

- `47` → push de 71 bytes (assinatura DER + SIGHASH)
- `30 44 ... cc` → assinatura em **DER** (`r` e `s`)
- `01` → **SIGHASH_ALL**
- `21` → push de 33 bytes (tamanho da chave pública)
- `03 d6 d1 82 ... dd a8` → chave pública **comprimida**

Ou seja, o `scriptSig` dessa P2PKH é:

```
<assinatura_der + sighash> <chave_publica_comprimida>
```

**Separando DER e SIGHASH**

Focando na parte da assinatura (sem o `47`):

```bash
30 44 02 20 7e 9a 79 a1 3f e5 34 bf 3c 0f 31 97 48 80 1e d4 c9 c3 e9 c7 55 45 f6 8e af 84 d8 99 42 8a be e8 02 20 07 6b 60 df 6f a6 3d fe 8b 54 11 75 3e f0 93 af a3 c3 ad 6b 09 18 55 9a e0 93 56 1b 66 0b 61 cc 
01
```

- de `30` até `cc` → **DER** da assinatura (contendo `r` e `s`)
- o byte final `01` → **SIGHASH_ALL**

Então:

- **DER**:
    
    ```
    304402207e9a79a13fe534bf3c0f319748801ed4c9c3e9c75545f68eaf84d899428abee80220076b60df6fa63dfe8b5411753ef093afa3c3ad6b0918559ae093561b660b61cc
    ```
    
- **SIGHASH**:
    
    ```
    01  → SIGHASH_ALL
    ```
    

É exatamente isso que o `decoderawtransaction` mostra como:

```
...660b61cc[ALL]
```

O `[ALL]` é a interpretação do byte `01`.

**Lendo `r` e `s` da assinatura com Python**

Para confirmar que aquela linha enorme de hex do `scriptSig` é, de fato, apenas uma assinatura ECDSA codificada em DER, basta usar um pequeno script em Python:

```python
from ecdsa import SECP256k1, util

sig_der_hex = "304402207e9a79a13fe534bf3c0f319748801ed4c9c3e9c75545f68eaf84d899428abee80220076b60df6fa63dfe8b5411753ef093afa3c3ad6b0918559ae093561b660b61cc"
sig_der = bytes.fromhex(sig_der_hex)

r, s = util.sigdecode_der(sig_der, SECP256k1.order)

print("r =", r)
print("s =", s)
print("Tamanho DER (bytes):", len(sig_der))
```

A execução desse código produz, por exemplo:

```
r = 57264352828055775463469084268137320939948896127493837674683254542600927624936
s = 3355911167489602945954490478345422070531500107788198649661466549951065186764
Tamanho DER (bytes): 70
```

Ou seja:

- o DER está codificando **dois inteiros grandes**: `r` e `s`;
- o tamanho total do objeto DER é **70 bytes**.

Esse valor de 70 bytes bate com a estrutura do próprio DER:

- `30` → indica uma **SEQUENCE**
- `44` → indica que a SEQUENCE tem **0x44 = 68 bytes de conteúdo**
- total = 2 bytes de cabeçalho (`30 44`) + 68 bytes de conteúdo (`02 20 <r> 02 20 <s>`)
- resultado: `70` bytes, exatamente o que `len(sig_der)` mostrou.

Com isso, fica claro que:

> aquela sequência `“30 44 02 20 ... 02 20 ...”` que aparece no `scriptSig` nada mais é do que o par `(r, s)` empacotado em DER, seguido pelo byte 01 do `SIGHASH_ALL` e pela chave pública comprimida.
> 

---

Ao olharmos uma assinatura DER real dentro de um `scriptSig`, fica evidente que nada no Bitcoin é “mágica em hexadecimal”: tudo segue regras rígidas, padronizadas e verificáveis. A combinação entre o formato DER, o byte de SIGHASH e a chave pública comprimida forma uma estrutura clara, determinística e compatível entre qualquer nó da rede, exatamente o que o consenso exige. Com isso, já possuímos uma compreensão completa de como uma assinatura ECDSA é representada dentro de uma transação. No próximo artigo, avançaremos para entender como essa assinatura é verificada pelo Bitcoin, como o `OP_CHECKSIG` usa o preimage e por que mudanças no algoritmo com o SegWit e o Taproot tornaram o processo mais seguro, eficiente e previsível.


por: Rafael Santos
