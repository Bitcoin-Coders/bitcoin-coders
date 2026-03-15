# Introdução a Scripts e Assinaturas

por Rafael Santos

O Bitcoin foi projetado para funcionar sem intermediários de confiança. Em vez de depender de bancos, governos ou autoridades centrais para validar transações, ele se apoia em mecanismos matemáticos verificáveis por qualquer computador conectado à rede. Nesse contexto, **scripts e assinaturas digitais** desempenham um papel central: são eles que estabelecem e comprovam as regras de quem pode gastar cada unidade de bitcoin.

Ao longo deste artigo, vamos entender como esses dois elementos se complementam: os **scripts**, que funcionam como cadeados programáveis para proteger os fundos, e as **assinaturas**, que são as chaves criptográficas capazes de abrir esses cadeados. Juntos, eles criam um sistema de segurança robusto, transparente e auditável, que permite que qualquer node da rede valide as transações de forma independente, sem precisar confiar em ninguém além do próprio código do Bitcoin.

---

### O que é o Bitcoin Script

O **Bitcoin Script** é uma linguagem mínima, **baseada em pilha**, onde cada instrução (opcode) pode: 

- Empilhar dados
- Desempilhar dados
- Comparar dados
- Verificar condições.

Não há variáveis, funções ou loops. Essa simplicidade reduz superfícies de ataque e torna a execução **determinística e previsível,** qualidade essencial para consenso entre milhares de nós.

Os scripts aparecem em **dois papéis complementares**. No **output** de uma transação, vem o **scriptPubKey** (*locking script*), que define **as regras de gasto** daquele valor: por exemplo, “apresente uma assinatura válida dessa chave pública hash160 X”. Esse “cadeado” pode ser simples (P2PKH), encapsulado (P2SH/P2WSH) ou mais moderno (Taproot/P2TR), mas a ideia é sempre: “o que precisa ser provado para gastar?”.

Quando alguém tenta gastar aquele output, no **input** da nova transação ele fornece o **scriptSig** (*unlocking script*), isto é, **os dados que satisfazem as regras** do cadeado: tipicamente, **assinatura + chave pública**. Em SegWit, esses dados vão no **witness**, mas o papel é o mesmo: fornecer as provas. Pense nele como a **chave** que se encaixa no cadeado.

Na validação, o nó executa “**scriptSig seguido de scriptPubKey**” (conceitualmente, concatena). Primeiro, os dados do scriptSig entram na pilha; depois, o scriptPubKey aplica operações como `OP_DUP`, `OP_HASH160`, `OP_EQUALVERIFY`, `OP_CHECKSIG`, consumindo e comparando elementos do topo da pilha. Se nenhuma operação falhar e, ao final, **restar um valor verdadeiro (não-zero)**, o gasto é considerado válido. Caso contrário, a execução falha e a transação é rejeitada.

### Chaves Públicas e Privadas e Assinaturas

Para que o *cadeado* do `scriptPubKey` seja aberto, o Bitcoin precisa de uma prova inequívoca de que o dono daquelas moedas realmente possui o direito de gastá-las. Essa prova vem da **criptografia de chave pública**, que liga de forma matemática uma chave privada, sua correspondente chave pública e a assinatura gerada a partir delas.

A **chave privada** é o segredo absoluto do usuário, uma sequência aleatória de números que concede controle sobre os fundos. É com ela que se “assina” uma transação, produzindo uma **assinatura digital** exclusiva. Já a **chave pública** é derivada da privada através de operações matemáticas unidirecionais (no caso do Bitcoin, usando a curva elíptica *secp256k1*). Essa chave pública pode ser compartilhada livremente, pois não revela a privada.

Quando uma transação é criada, o `scriptSig` inclui a **assinatura** e a **chave pública**. O node, ao validar, insere esses dados na pilha e executa o `scriptPubKey`, que contém instruções como `OP_HASH160` e `OP_CHECKSIG`. É justamente o `OP_CHECKSIG` que usa a assinatura e a chave pública para confirmar que a mensagem (a transação) foi realmente assinada pelo dono da chave privada.

Essa relação cria o elo perfeito entre criptografia e execução de scripts: a assinatura **prova** a posse da chave, e o script **verifica** essa prova de forma autônoma e determinística. A segurança de todo o sistema está no fato de que, embora qualquer pessoa possa verificar uma assinatura com a chave pública, **ninguém consegue derivar a chave privada a partir dela.** Essa assimetria é o que sustenta a confiança matemática do Bitcoin.

---

## Validação da Transação

Quando um node recebe uma transação, ele não confia em quem enviou, ele **reproduz as provas matemáticas** e executa o script de verificação localmente. A ideia é simples: a transação só é válida se o conjunto de instruções do `scriptSig` (a chave) **satisfizer** as condições do `scriptPubKey` (o cadeado).

O processo segue três etapas fundamentais:

1. **O node localiza o output que está sendo gasto**, lendo o `scriptPubKey` daquele output anterior (as condições de gasto).
2. **Lê o input da nova transação**, onde está o `scriptSig` (assinatura e chave pública).
3. **Executa ambos em sequência,** primeiro o `scriptSig`, depois o `scriptPubKey`. Os dados e operações são empilhados e avaliados de forma determinística.

Se, ao final, o valor no topo da pilha for **TRUE**, a transação é considerada válida, caso contrário, é rejeitada.

### 🧩 Exemplo de uma transação simples P2PKH

A forma mais clássica de script é a *Pay to Public Key Hash* (P2PKH).

O **scriptPubKey** de um output desse tipo é:

```bash
OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

Ele diz:

> “Para gastar este output, apresente uma chave pública que produza este pubKeyHash, e uma assinatura válida para essa chave.”
> 

---

O **scriptSig**, no momento de gastar esse output, traz:

```bash
<assinatura> <chave_publica>
```

### 🔍 Execução passo a passo

1. O node **concatena** os dois scripts, formando uma sequência de execução:

```bash
<assinatura> <chave_publica> OP_DUP OP_HASH160 <pubKeyHash> OP_EQUALVERIFY OP_CHECKSIG
```

1. Agora ele executa **da esquerda para a direita**, manipulando a pilha:

| Etapa | Operação | Pilha após execução |
| --- | --- | --- |
| 1 | Empilha `<assinatura>` | `[assinatura]` |
| 2 | Empilha `<chave_publica>` | `[assinatura, chave_publica]` |
| 3 | `OP_DUP` duplica o topo | `[assinatura, chave_publica, chave_publica]` |
| 4 | `OP_HASH160` aplica hash no topo | `[assinatura, chave_publica, hash(chave_publica)]` |
| 5 | Empilha `<pubKeyHash>` (o destino esperado) | `[assinatura, chave_publica, hash(chave_publica), pubKeyHash]` |
| 6 | `OP_EQUALVERIFY` compara os dois últimos elementos → se iguais, remove ambos e continua | `[assinatura, chave_publica]` |
| 7 | `OP_CHECKSIG` verifica os dois últimos elementos da pilha, a assinatura e a chave pública, confirmando se a assinatura é válida para aquela chave pública e para o conteúdo da transação. | `[TRUE]` |

✅ Resultado final: **TRUE** → o node aceita a transação.

Se qualquer etapa falhar (por exemplo, `OP_EQUALVERIFY` der falso ou a assinatura não corresponder à chave pública), o resultado final será **FALSE** e o node rejeitará a transação.

O Bitcoin não “confia” em ninguém. Ele simplesmente **executa scripts determinísticos**

sobre dados públicos e decide, de forma matemática, se as condições foram atendidas.

A beleza do sistema está nesse design minimalista: o mesmo conjunto de operações, rodado por milhares de nodes no mundo, chega sempre ao mesmo resultado.

---

## Exemplo Prático com bitcoin-cli

Vamos fazer um exemplo prático no Bitcoin Core (signet) para entender melhor.

**✍️ Passo 1 — Obtenha a Transação**
Pegue o HEX de uma transação criada e assinada. Caso não tenha, crie e assine uma transação usando os comandos `createrawtransaction` e `signrawtransactionwithwallet`

```bash
"hex": "0200000001d49df01aae855b7da49b33ca2e5b9ac821ab948f129b57fe4653a548dcd19c16000000006a473044022051b11fb2c1e2b81099b09cb4410e1379612abfff5ee419467850dd8269c687dc02204bebd83e2d32ad268a9f4976e2b43364e62f0805acecc57b0f6cade86665650c0121022cb7fcfb1377e85e3c5ac300028890059ff84e9d8e1b6f35a808ebf3e477e7f1fdffffff0194110000000000001976a914aa0420f7f934bce88e817ccaa33f06208f10681588ac00000000"
```

**🔍 Passo 2 — Decodificar a transação**
Decodifique a transação com o comando `decoderawtransaction`.

```bash
bitcoin-cli -datadir="." -rpcwallet=signetwallet decoderawtransaction 0200000001d49df01aae855b7da49b33ca2e5b9ac821ab948f129b57fe4653a548dcd19c16000000006a473044022051b11fb2c1e2b81099b09cb4410e1379612abfff5ee419467850dd8269c687dc02204bebd83e2d32ad268a9f4976e2b43364e62f0805acecc57b0f6cade86665650c0121022cb7fcfb1377e85e3c5ac300028890059ff84e9d8e1b6f35a808ebf3e477e7f1fdffffff0194110000000000001976a914aa0420f7f934bce88e817ccaa33f06208f10681588ac00000000
{
  "txid": "2480b538f0f9c63b9cf072d2d0761d8b49a8fbdb1a2e95eb8838dec1f901f3ea",
  "hash": "2480b538f0f9c63b9cf072d2d0761d8b49a8fbdb1a2e95eb8838dec1f901f3ea",
  "version": 2,
  "size": 191,
  "vsize": 191,
  "weight": 764,
  "locktime": 0,
  "vin": [
    {
      "txid": "169cd1dc48a55346fe579b128f94ab21c89a5b2eca339ba47d5b85ae1af09dd4",
      "vout": 0,
      "scriptSig": {
        "asm": "3044022051b11fb2c1e2b81099b09cb4410e1379612abfff5ee419467850dd8269c687dc02204bebd83e2d32ad268a9f4976e2b43364e62f0805acecc57b0f6cade86665650c[ALL] 022cb7fcfb1377e85e3c5ac300028890059ff84e9d8e1b6f35a808ebf3e477e7f1",
        "hex": "473044022051b11fb2c1e2b81099b09cb4410e1379612abfff5ee419467850dd8269c687dc02204bebd83e2d32ad268a9f4976e2b43364e62f0805acecc57b0f6cade86665650c0121022cb7fcfb1377e85e3c5ac300028890059ff84e9d8e1b6f35a808ebf3e477e7f1"
      },
      "sequence": 4294967293
    }
  ],
  "vout": [
    {
      "value": 0.00004500,
      "n": 0,
      "scriptPubKey": {
        "asm": "OP_DUP OP_HASH160 aa0420f7f934bce88e817ccaa33f06208f106815 OP_EQUALVERIFY OP_CHECKSIG",
        "desc": "addr(mw1v7YAUzMdCpWHjNm6He56SkFc2NabyGx)#58mccn42",
        "hex": "76a914aa0420f7f934bce88e817ccaa33f06208f10681588ac",
        "address": "mw1v7YAUzMdCpWHjNm6He56SkFc2NabyGx",
        "type": "pubkeyhash"
      }
    }
  ]
}

```

Abaixo, vemos como os **scripts** aparecem na prática dentro de uma transação Bitcoin.

`vin.scriptSig` — o *unlocking script* (a “chave que abre o cadeado”)

No campo `vin`, o `scriptSig` contém a **assinatura digital** e a **chave pública** que provam a posse dos fundos.

No exemplo:

```
"scriptSig": {
  "asm": "3044022051b11fb2c1e2b81099b09cb4410e1379612abfff5ee419467850dd8269c687dc02204bebd83e2d32ad268a9f4976e2b43364e62f0805acecc57b0f6cade86665650c[ALL] 022cb7fcfb1377e85e3c5ac300028890059ff84e9d8e1b6f35a808ebf3e477e7f1"
}

```

- O **primeiro elemento** é a **assinatura**:
    
    ```
    3044022051b11fb2c1e2b81099b09cb4410e1379612abfff5ee419467850dd8269c687dc02204bebd83e2d32ad268a9f4976e2b43364e62f0805acecc57b0f6cade86665650c[ALL]
    ```
    
    → Essa assinatura segue o formato **DER** e inclui o sufixo `[ALL]`, que indica o tipo de verificação (`SIGHASH_ALL`).
    
- O **segundo elemento** é a **chave pública**:
    
    ```
    022cb7fcfb1377e85e3c5ac300028890059ff84e9d8e1b6f35a808ebf3e477e7f1
    ```
    
    → É a versão comprimida da chave pública (33 bytes), derivada da chave privada que assinou a transação.
    

💡 Em resumo:

O `scriptSig` **empilha** primeiro a assinatura e depois a chave pública, que serão usadas pelo `scriptPubKey` para validar a transação.

---

`vout.scriptPubKey` — o *locking script* (o “cadeado”)

Já o `scriptPubKey`, no campo `vout`, define **as condições necessárias para gastar esse output no futuro**:

```
"scriptPubKey": {
  "asm": "OP_DUP OP_HASH160 aa0420f7f934bce88e817ccaa33f06208f106815 OP_EQUALVERIFY OP_CHECKSIG",
  "type": "pubkeyhash"
}
```

- O `asm` mostra o **script legível**, composto pelos **opcodes** e pelo **pubKeyHash** (20 bytes):
    - `OP_DUP` → duplica a chave pública.
    - `OP_HASH160` → aplica SHA256 + RIPEMD160 sobre a chave pública.
    - `aa0420f7f9...6815` → é o **hash160** da chave pública do destinatário (o endereço).
    - `OP_EQUALVERIFY` → compara se o hash gerado é igual ao destino esperado.
    - `OP_CHECKSIG` → verifica se a assinatura é válida para essa chave pública.

💡 Em resumo:

O `scriptPubKey` define o “cadeado”. Ele **espera uma chave pública que gere o hash `aa0420f7...6815` e uma assinatura válida** dessa chave. O `scriptSig`, por sua vez, **fornece exatamente esses dois elementos**. Quando o node executa ambos os scripts e o resultado final é `TRUE`, a transação é considerada válida.

---

Os **scripts e assinaturas** formam o núcleo da segurança no Bitcoin. Cada transação que circula na rede é, essencialmente, uma **prova matemática** de que o emissor possui a chave privada correspondente ao endereço de origem. Essa arquitetura elimina a necessidade de confiança entre as partes e garante que qualquer node possa verificar, de forma independente, a autenticidade de cada gasto.

O Bitcoin Script, embora simples, é poderoso: ele define *como* os fundos podem ser movimentados e permite a criação de regras de gasto auditáveis e automáticas.

As assinaturas, por sua vez, são o elo que conecta o controle criptográfico à execução desses scripts, garantindo que somente o detentor legítimo da chave privada possa autorizar a transação.

No próximo artigo, vamos **mergulhar mais fundo na execução dos scripts**, entendendo como cada opcode atua na pilha e reproduzindo, passo a passo, o processo de validação que resulta no esperado `TRUE`.
