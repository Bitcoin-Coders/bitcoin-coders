# SegWit: teoria e prática na Signet

por Rafael Santos

Atualizado em: 29/08/2025 ∙ 30 min leitura

Os endereços **Legacy (P2PKH)** foram o primeiro formato amplamente utilizado no Bitcoin, representando um estágio fundamental para a usabilidade da rede. Contudo, com o crescimento do número de transações e a busca por maior escalabilidade, começaram a surgir limitações. Um dos principais problemas era a **maleabilidade das transações**, isto é, a possibilidade de alterar pequenos detalhes na assinatura sem modificar seu conteúdo, comprometendo sistemas que dependiam da identificação única de transações. É importante entender o que era esse problema de maleabilidade das transações.

Antes da introdução do SegWit, a **assinatura digital** fazia parte dos dados usados para gerar o identificador da transação (**txid**). Como assinaturas ECDSA permitem múltiplas representações equivalentes, seja pelo uso de diferentes valores aleatórios (nonce) no ato da assinatura, seja por pequenas variações na forma de codificação, era possível criar versões diferentes da mesma transação. 

- No **Legacy, o** **txid** (Transaction ID) era calculado a partir de:
    - Todos os **inputs** (referências a UTXOs anteriores, índices, scriptSig)
    - Todos os **outputs** (valores e scriptPubKey de destino)
    - **Scripts de assinatura (scriptSig)** → ou seja, as **assinaturas e chaves públicas** usadas para validar os inputs também entravam no cálculo.
- No **SegWit, o** **txid** passou a ser calculado **sem incluir as assinaturas:**
    - **Versão da transação**
    - **Inputs** (sem o scriptSig — apenas referências)
    - **Outputs** (valor + scriptPubKey)
    - **Locktime**

Por exemplo, imagine o seguinte cenário:

- **Alice envia 0,1 BTC para Bob** → a transação é criada e transmitida na rede com o identificador **txid “A”**.
- **Um participante malicioso retransmite a mesma transação**, alterando apenas a forma da assinatura (sem modificar valores ou endereços - isso era possível).
- Essa alteração gera um **novo identificador, txid “B”**, embora o conteúdo econômico da transação continue idêntico.
- **Bob ainda recebe os mesmos 0,1 BTC**, independentemente de qual versão seja confirmada.
- **O problema surge para sistemas que estavam monitorando o txid “A”**: se a rede confirmar a versão com txid “B”, esses sistemas (uma exchanges ou um protocolo de segunda camada, por exemplo) podem perder a referência e falhar no acompanhamento da transação.

Esse comportamento não roubava fundos, mas quebrava a lógica de aplicações que dependiam da imutabilidade do identificador, como carteiras, exchanges ou protocolos de segunda camada. O SegWit resolveu esse problema ao separar a assinatura (witness) do cálculo do txid, garantindo que modificações nessa parte não alterem mais o identificador da transação.

# Eficiência do espaço no bloco

Além da maleabilidade no legacy, o espaço em bloco era utilizado de maneira pouco eficiente, elevando as taxas e dificultando a adoção em larga escala.

### 🔹 Ineficiência do espaço em bloco (pré-SegWit)

Antes do SegWit, **tudo** da transação (inputs, outputs **e assinaturas**) contava no limite de **1 MB por bloco**. Só que:

- As **assinaturas** ocupam muito espaço (às vezes **mais da metade** da transação).
- Esse espaço é usado apenas **no momento da validação,** depois que a transação é validada, as assinaturas não têm relevância para o estado da blockchain (os UTXOs).
- Ou seja, uma boa parte do bloco era preenchida por dados “temporários” (assinaturas), em vez de dados “permanentes” (inputs e outputs que realmente formam o estado do sistema).

👉 Exemplo ilustrativo:

- Uma transação simples **Legacy P2PKH** (~250 bytes):
    - ~148 bytes = input (scriptSig com assinatura e chave pública)
    - ~34 bytes = output
    - ~68 bytes = outros campos (version, locktime etc.)
    - **Conclusão:** mais de **50% do espaço** é consumido por assinatura!

Isso significa que cabiam menos transações por bloco, e a competição por espaço aumentava as taxas.

### 🔹 Como o SegWit otimizou

Com o SegWit:

- As assinaturas foram movidas para o **witness**.
- O cálculo do “peso do bloco” mudou:
    - Dados “essenciais” (inputs e outputs) têm peso maior.
    - Dados de witness (assinaturas) têm peso reduzido (contam 1/4 do peso).
- Resultado: mais transações cabem no bloco sem precisar aumentar o limite de 1 MB → na prática, os blocos podem chegar a ~4 MB em “peso”, mas com eficiência real de espaço.

---

Foi nesse contexto então que surgiu o **Segregated Witness (SegWit)**, introduzindo uma evolução no formato de endereços sem quebrar a compatibilidade com o legacy. O SegWit reorganiza a forma como os dados são armazenados, separando as assinaturas da transação e permitindo tanto **maior capacidade efetiva nos blocos** quanto a resolução da maleabilidade. Importante destacar que os endereços SegWit não substituem os anteriores, mas oferecem uma opção mais eficiente, segura e preparada para novas camadas de inovação, como a Lightning Network. Dessa forma, representaram uma **evolução gradual**, garantindo que usuários e sistemas pudessem migrar de maneira compatível e sem rupturas.

# Como funciona o endereço Segwit?

Assim como nos endereços Legacy, no Segwit, tudo é gerado a partir de uma seed aleatória. Como vimos no artigo anterior, quando solicitamos um endereço, temos o caminho de derivação que indica pro Bitcoin Core como ele pode gerar os endereços. Neste caso, o caminho de derivação contém a informação de que o endereço deva ser um Segwit. Abaixo, vemos um passo-a-passo de como esse endereço é gerado.

## **🌱 Passo 0 – Seed → Chaves-mestre**

- Tudo começa com uma **seed aleatória** (gerada com 128 ou 256 bits).
- A partir dessa seed, obtemos a **chave-mestre (master private key)** e o **chain code** via BIP32.
- Esse par (master key + chain code) é a raiz da HD Wallet e, a partir dele, podemos derivar todas as outras chaves usando diferentes **caminhos de derivação**.

👉 É nesse caminho que entra a indicação de tipo de endereço: por exemplo, `m/84'/0'/0'/0/0` indica que queremos um endereço SegWit (BIP84).

## **🔑 Passo 1 – Chave privada → chave pública**

- A partir da **chave-mestre**, derivamos uma **chave privada específica** conforme o **caminho de derivação** definido (ex.: `m/84'/0'/0'/0/0`).
- Essa chave privada gera uma **chave pública** através da curva elíptica **secp256k1**.
- Cada chave derivada é única e corresponde a um endereço específico dentro da carteira.

---

## **🔑 Passo 2 – Da chave pública ao *programa SegWit***

- No SegWit **nativo P2WPKH (Pay to Witness Public Key Hash)**, um programa precisa ser construído da seguinte maneira:
    1. Fazer **hash160(pubkey)** = RIPEMD160(SHA256(pubkey)) → 20 bytes.
    2. Montar o **witness program**:
        
        ```arduino
        0x00 0x14 <20-byte pubkeyhash>
        ```
        
        - `0x00` → versão do witness (SegWit v0).
        - `0x14` → opcode push que significa “empurre 20 bytes para a pilha” (0x14 hex = 20 decimal).
        - `<20-byte pubkeyhash>` → é o `hash160(pubkey)`.

➡️ Esse programa é, na prática, o **script de bloqueio (locking script)** que define como o UTXO poderá ser gasto no futuro. No SegWit nativo P2WPKH, ele é propositalmente simples: apenas a versão, o opcode de tamanho e o hash da chave pública. Para gastar esse UTXO, o usuário precisa fornecer no campo *witness* os dados que satisfaçam esse programa — ou seja, a chave pública correspondente e uma assinatura válida.

---

## **🔑 Passo 3 – scriptPubKey no output**

- O **witness program** é inserido dentro do `scriptPubKey` do output da transação.

Forma codificada:

```arduino
scriptPubKey: 0x00 0x14 <20-byte pubkeyhash>
```

- `0x00` → versão do witness (SegWit v0).
- `0x14` → opcode que significa “empurre 20 bytes para a pilha”.
- `<20-byte pubkeyhash>` → o resultado de `hash160(pubkey)`.

Podemos comparar o scriptPubKey com o do endereço legacy:

```jsx
Legacy: OP_DUP OP_HASH160 <hash> OP_EQUALVERIFY OP_CHECKSIG
76 a9 14 79761b7d9c7dc9182d47a9b362254fa683f555d5 88 ac
```

```jsx
Segwit: 0 <hash160(pubKey)> 
				00 14 d077f556ef5942cbff67b1fef7e184ae89810917
```

- Se você rodar `decoderawtransaction` no Bitcoin Core, verá algo assim:
    
    ```json
    "asm": "0 ab6805c0...ef7f26b8",
    "type": "witness_v0_keyhash",
    "address": "bc1q..."
    ```
    
- O campo `"address"` mostra o **endereço Bech32**, que é apenas uma **codificação legível** do witness program (versão + dados).
    - Importante: o opcode `0x14` **não é incluído** na codificação Bech32.
    - O Bech32 pega só: **versão (0)** + **programa de 20 bytes**, e transforma isso no endereço `bc1q...`.

👉 Em outras palavras: o **scriptPubKey** contém a lógica em linguagem de script (com opcode), enquanto o **endereço Bech32** é a versão amigável para humanos, derivada do mesmo conteúdo mas sem carregar o opcode explícito.

---

## **🔑 Passo 4 – Gastando esse output**

Quando alguém gasta o UTXO que contém esse `scriptPubKey`, precisa provar que **conhece a chave privada** correspondente ao hash gravado ali dentro.

- O input da transação, no SegWit, fica assim:
    - **scriptSig**: vazio
    - **txinwitness**: `[assinatura, pubkey]`

**Processo de verificação:**

1. Extrair a **chave pública** fornecida no witness.
2. Calcular `hash160(pubkey)` e comparar com os 20 bytes registrados no witness program do `scriptPubKey`.
3. Validar a **assinatura** usando a pubkey e os dados da transação (hash da transação a ser assinada).
4. Se ambas as verificações forem bem-sucedidas, o nó considera que a condição foi satisfeita e o UTXO pode ser gasto.

👉 Em resumo: o `scriptPubKey` define a regra (“preciso do hash desta pubkey”), e o campo *witness* traz a prova (a pubkey e a assinatura feita com a chave privada).

---

Na prática, não precisamos calcular manualmente cada etapa. O **descriptor** da carteira já descreve toda a receita: a derivação HD fornece a chave pública no caminho correto (ex.: `m/84'/0'/0'/0/0`), e o formato SegWit define como transformá-la em um endereço Bech32 e em um `scriptPubKey`.

Em outras palavras, todo o processo que detalhamos do **Passo 0 ao Passo 4** acontece automaticamente por baixo dos panos no Bitcoin Core.

Vamos ver um exemplo na prática agora.

# Exemplo na Signet:

## 1) Iniciar o nó em Signet

```bash
bitcoind -datadir="." -daemon
```

- Lembre-se de configurar o bitcoin.conf para Signet.

## 2) Criar carteira e gerar um endereço SegWit (bech32)

```bash
bitcoin-cli -datadir="." createwallet demo-signet
//se a carteira já estiver criada, é só carregar
//bitcoin-cli -datadir="." loadwallet demo-signet
ADDR=$(bitcoin-cli -datadir="." getnewaddress "dest-signet" bech32)
echo "ADDR = $ADDR"

ADDR = tb1qyr25gtl0fczeg4vwl00ny8c7zkj0j6za5yrsnp
```

## 3) Mostrar dados do **endereço**

```bash
# ver dados do endereço (note witness_version/program e scriptPubKey)
bitcoin-cli -datadir="." getaddressinfo "$ADDR"

{
  "address": "tb1qyr25gtl0fczeg4vwl00ny8c7zkj0j6za5yrsnp",
  "scriptPubKey": "001420d5442fef4e0594558efbdf321f1e15a4f9685d",
  "ismine": true,
  "solvable": true,
  "desc": "wpkh([52733c05/84h/1h/0h/0/0]03beef807fe678ba63a34fcc0c155922a4de7971b17511129022261dc021a90010)#26x2a3h6",
  "parent_desc": "wpkh([52733c05/84h/1h/0h]tpubDD2bRH7V43iTNRhhNYEQjabRMguGUGUj44oRS12uAXaiiK8zdzsxXoLcHeVALE9qj4f1Jh4dNbea5ePT6e9TtnRntyP26vvkaPZK2hucKQJ/0/*)#7vjxgtwl",
  "iswatchonly": false,
  "isscript": false,
  "iswitness": true,
  "witness_version": 0,
  "witness_program": "20d5442fef4e0594558efbdf321f1e15a4f9685d",
  "pubkey": "03beef807fe678ba63a34fcc0c155922a4de7971b17511129022261dc021a90010",
  "ischange": false,
  "timestamp": 1756327350,
  "hdkeypath": "m/84h/1h/0h/0/0",
  "hdseedid": "0000000000000000000000000000000000000000",
  "hdmasterfingerprint": "52733c05",
  "labels": [
    "dest-signet"
  ]
}
```

No resultado acima, os campos mais importantes revelam como o Bitcoin Core gera o endereço SegWit. O `"pubkey"` mostra a chave pública derivada do caminho HD (`"hdkeypath"`) definido no descriptor. A partir dela, o Core calcula o `"witness_program"` aplicando **hash160(pubkey)**. Esse valor de 20 bytes é combinado com a `"witness_version": 0`, formando o `"scriptPubKey": "0014..."` (onde `00` representa OP_0 e `14` indica 20 bytes). Finalmente, esse script é codificado no formato Bech32 e exibido em `"address"`. 

## 4) Decodificando o **scriptPubKey**

Agora que já identificamos no `getaddressinfo` os campos principais de geração do endereço, incluindo o `scriptPubKey` em formato hexadecimal, podemos dar um próximo passo e **pedir ao Bitcoin Core que traduza esse script**. Para isso utilizamos o comando `decodescript`, que interpreta o hex e mostra em linguagem mais legível sua estrutura (`OP_0 <20-bytes>`), o tipo de saída e o endereço correspondente.

```bash
# pegue o scriptPubKey do campo "scriptPubKey" acima (ex.: 0014<...>)
SPK_HEX=$(bitcoin-cli -datadir="." getaddressinfo "$ADDR" | jq -r .scriptPubKey) 
echo "scriptPubKey = $SPK_HEX"
scriptPubKey = 001420d5442fef4e0594558efbdf321f1e15a4f9685d

# decodificar o scriptPubKey para ver "asm: 0 <20-bytes>" e o mesmo endereço
bitcoin-cli -datadir="." decodescript "$SPK_HEX"

{
  "asm": "0 20d5442fef4e0594558efbdf321f1e15a4f9685d",
  "desc": "addr(tb1qyr25gtl0fczeg4vwl00ny8c7zkj0j6za5yrsnp)#hmjdyz3n",
  "address": "tb1qyr25gtl0fczeg4vwl00ny8c7zkj0j6za5yrsnp",
  "type": "witness_v0_keyhash",
  "p2sh": "2N3xQy8mZDA9UtFE6zJM2KRj1Yw66TYaYnZ"
}

```

O comando `decodescript` serve para interpretar diretamente o **scriptPubKey** em formato hexadecimal, sem depender da carteira. Enquanto o `getaddressinfo` mostra os metadados do endereço (como pubkey, derivação HD e se pertence à sua wallet), o `decodescript` traduz o script em sua forma “legível” (`asm: 0 <20-bytes>`), identifica o tipo de saída (`witness_v0_keyhash`) e até reconstrói o endereço correspondente. Dessa forma, ele confirma de maneira independente que o endereço Bech32 exibido nada mais é do que a codificação legível do `scriptPubKey`.

Em resumo, o `decodescript` é a ponte que permite enxergar como aquele hex aparentemente obscuro (`0014...`) se traduz diretamente no endereço Bech32 que usamos no dia a dia.

## 5) Obter fundos no faucet

Peça algumas moedas para o seu `ADDR` em um faucet de **Signet** ([https://alt.signetfaucet.com](https://alt.signetfaucet.com/)).

- Espere receber os sBTC e confira:

```bash
bitcoin-cli -datadir="." getbalance
0.00500483

bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "fe7e668f5d00322a9dff5223143724f5b7b1d6002c585020c5ed5fcea32a5dbc",
    "vout": 440,
    "address": "tb1qyr25gtl0fczeg4vwl00ny8c7zkj0j6za5yrsnp",
    "label": "dest-signet",
    "scriptPubKey": "001420d5442fef4e0594558efbdf321f1e15a4f9685d",
    "amount": 0.00500483,
    "confirmations": 2,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([52733c05/84h/1h/0h/0/0]03beef807fe678ba63a34fcc0c155922a4de7971b17511129022261dc021a90010)#26x2a3h6",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4Y87BgzHBqaSDFH7Vm5zL2wBMMndVyNcMjGNAXq1dC28oRBsAdVVsQAz2oAAswgdT6D8pjCHJBi5pRejxfNL1LfFDN3UUTVt/84h/1h/0h/0/*)#926jfv2v"
    ],
    "safe": true
  }
]
```

Na saída do `listunspent`, alguns campos merecem destaque para entender melhor o que está acontecendo. O `"txid"` identifica de forma única a transação de onde saiu esse UTXO e será necessário caso queira gastá-lo. O `"vout"` indica em qual posição dentro dessa transação está o output que lhe pertence. O `"scriptPubKey"` mostra a condição que precisará ser satisfeita para gastar esse UTXO (no caso, o witness program SegWit que já analisamos). O campo `"amount"` indica o valor disponível, enquanto `"confirmations"` mostra quantos blocos já foram minerados após a transação, dando mais segurança. Por fim, `"spendable": true` confirma que a sua carteira tem a chave privada correspondente e pode usar esses fundos em uma nova transação.

## 6) Criar, assinar e enviar uma transação P2WPKH

```bash
# 1) Gerar um endereço bech32 para o destinatário (pode ser na mesma wallet)
RECIP=$(bitcoin-cli -datadir="." getnewaddress "destinatario-signet" bech32)
echo "RECIP = $RECIP"

RECIP = tb1qq5agk4x02hahsrgz3kt05kyfx8g6gjau922a02

# 2) Montar a transação crua só com o output desejado (0.0005 sBTC para RECIP)
RAW=$(bitcoin-cli -datadir="." createrawtransaction "[]" "[{\"$RECIP\":0.0005}]")

# 3) Deixar o Core completar inputs, taxa e troco
FUNDED=$(bitcoin-cli -datadir="." fundrawtransaction "$RAW" | jq -r .hex)

# 4) Assinar (gera witness [assinatura, pubkey] em cada input P2WPKH)
SIGNED=$(bitcoin-cli -datadir="." signrawtransactionwithwallet "$FUNDED" | jq -r .hex)

# 5) Enviar para a rede
TXID=$(bitcoin-cli -datadir="." sendrawtransaction "$SIGNED")
echo "TXID = $TXID"

TXID = 133477ca67385c43436488275e13598c16596bba438954e80aabd64c2d2f63a0
```

Ao rodar os códigos acima, nós enviamos uma transação para a rede. Em seguida veremos cada um dos passos, mas antes observe como ficaram os UTXOs logo após a transação ter sido enviada:

```bash
bitcoin-cli -datadir="." listunspent
[
]
```

Ao observar o resultado de `listunspent` logo após o envio da transação, é normal que a lista apareça vazia. Isso acontece porque o comando, por padrão, só mostra **UTXOs confirmados** (com pelo menos 1 bloco). No momento em que a transação é criada, os UTXOs de origem deixam de aparecer (pois já foram gastos) e os novos UTXOs de destino (incluindo o troco) só passam a aparecer depois que a transação é incluída em um bloco. Enquanto isso, eles permanecem apenas na **mempool**. Para enxergar também os UTXOs ainda não confirmados, pode-se usar `listunspent 0`. Se olharmos o `listunspent` após a confirmação veremos algo assim:

```bash
bitcoin-cli -datadir="." listunspent
[
  {
    "txid": "133477ca67385c43436488275e13598c16596bba438954e80aabd64c2d2f63a0",
    "vout": 0,
    "address": "tb1qq5agk4x02hahsrgz3kt05kyfx8g6gjau922a02",
    "label": "destinatario-signet",
    "scriptPubKey": "0014053a8b54cf55fb780d028d96fa588931d1a44bbc",
    "amount": 0.00050000,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([52733c05/84h/1h/0h/0/1]02d9d1031bebaed0eeaf953c199e3091234e1d4c0c95e6740d8e4ec6655817cb2a)#wcavwzfm",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4Y87BgzHBqaSDFH7Vm5zL2wBMMndVyNcMjGNAXq1dC28oRBsAdVVsQAz2oAAswgdT6D8pjCHJBi5pRejxfNL1LfFDN3UUTVt/84h/1h/0h/0/*)#926jfv2v"
    ],
    "safe": true
  },
  {
    "txid": "133477ca67385c43436488275e13598c16596bba438954e80aabd64c2d2f63a0",
    "vout": 1,
    "address": "tb1qag4k6y60tmugvaa8smuj79u5kgptasf65x7pzd",
    "scriptPubKey": "0014ea2b6d134f5ef88677a786f92f1794b202bec13a",
    "amount": 0.00450342,
    "confirmations": 1,
    "spendable": true,
    "solvable": true,
    "desc": "wpkh([52733c05/84h/1h/0h/1/0]03f77ed896919dd18838d1a3eddafe4bfd1ac250fa062ca967b4ee2e71d8b456a9)#swr3w9e5",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4Y87BgzHBqaSDFH7Vm5zL2wBMMndVyNcMjGNAXq1dC28oRBsAdVVsQAz2oAAswgdT6D8pjCHJBi5pRejxfNL1LfFDN3UUTVt/84h/1h/0h/1/*)#57ln5e65"
    ],
    "safe": true
  }
]
```

Veja que temos 2 UTXO, um que é o endereço pra qual enviamos a transação e o outro que é o endereço de troco, criado internamente pelo Bitcoin Core. Note que o endereço anterior não está mais como UTXO, já que ele acabou de ser gasto.

Esse comportamento ilustra bem o modelo de UTXOs do Bitcoin: cada saída só pode ser gasta uma vez, e a cada transação surgem novos UTXOs, substituindo os anteriores.

Vamos entender cada um desses passos da transação de exemplo:

**1) `getnewaddress` (destinatário)**

Gera um **novo endereço bech32** (P2WPKH) para receber os 0.0005 sBTC.

Ao pedir **bech32**, nós forçamos o **witness v0** com **programa de 20 bytes** (hash160 da pubkey). O endereço `tb1…` é a codificação legível de `OP_0 <20 bytes>`.

*Efeito SegWit*: define que os futuros **inputs** usarão **`txinwitness`** (e**`scriptSig` vazio**).

**2) `createrawtransaction "[]" "[{...}]"`**

Monta uma **transação crua** contendo apenas os **outputs desejados** (para quem e quanto vai). Aqui passamos uma **lista vazia de inputs** (`[]`) de propósito: isso diz “não selecione inputs ainda”. Assim, separarmos a etapa de seleção de UTXOs para o próximo comando. O resultado é um hex parcial, **sem inputs** e **sem troco**.

Descrevemos apenas os **scriptPubKey** de destino: em P2WPKH isso vira `0014<witness_program>`.
Efeito SegWit: a transação já nasce com saídas segwit (witness_v0_keyhash), mais baratas em vbytes.

**3) `fundrawtransaction <hex>`**

Pede ao Core para **completar a transação**: ele escolhe **UTXOs** adequados da sua wallet, **calcula a taxa**, **adiciona o troco** (normalmente para um endereço seu bech32 de troco) e devolve um novo hex. É aqui que a transação ganha **inputs** e **vout de troco**, ficando “financeiramente consistente”.

*Efeito SegWit*: como inputs/outputs são SegWit, o **peso (weight)** cai e a **`vsize`** é menor que em legacy → **fee menor** para a mesma política de taxa.

**4) `signrawtransactionwithwallet <hex>`**

O Bitcoin Core assina **cada input** com as chaves da sua wallet, produzindo as **assinaturas ECDSA** e inserindo-as no **witness** de cada input. O retorno é o hex **assinado** e pronto para broadcast.

`txinwitness = [ assinatura(ECDSA, BIP143), pubkey ]` e **`scriptSig` vazio**.

*Efeito SegWit*:

- **Maleabilidade** mitigada: o **`txid`** não inclui o witness (assinaturas), só a parte “base”.
- O que inclui witness é o **`wtxid`**.
- Assinatura usa o **digest BIP143** (versão, prevouts, sequences, scriptCode, *valor do UTXO*, outputs, locktime, sighash).

**5) `sendrawtransaction <hex>`**

Envia o hex assinado para a rede **Signet** (broadcast). Se aceito pelos nós (`hash160(pubkey)` do witness confere com o **programa** do `scriptPubKey`? A assinatura (BIP143) bate?), você recebe o **TXID**. A partir daí, dá para consultar `decoderawtransaction`, `getmempoolentry`, exploradores, etc.

*Efeito SegWit*: a rede aceita a tx com **witness separado**, e o bloco registra o **compromisso do witness** na coinbase.

---

Após a transação, podemos inspecioná-la:

```bash
bitcoin-cli -datadir="." decoderawtransaction "$SIGNED" | jq '{vin: .vin, vout: .vout}'
{
  "vin": [
    {
      "txid": "fe7e668f5d00322a9dff5223143724f5b7b1d6002c585020c5ed5fcea32a5dbc",
      "vout": 440,
      "scriptSig": {
        "asm": "",
        "hex": ""
      },
      "txinwitness": [
        "3044022008af5e5a6f51e078093fb23d6cf2c020e62af4cd2b5443ec85b0c90860fd6ebd0220401704dcd90705f2823352fa9133f5761853fdf997e46ea771a80f1b946715b401",
        "03beef807fe678ba63a34fcc0c155922a4de7971b17511129022261dc021a90010"
      ],
      "sequence": 4294967293
    }
  ],
  "vout": [
    {
      "value": 0.00050000,
      "n": 0,
      "scriptPubKey": {
        "asm": "0 053a8b54cf55fb780d028d96fa588931d1a44bbc",
        "desc": "addr(tb1qq5agk4x02hahsrgz3kt05kyfx8g6gjau922a02)#0d8dl0fr",
        "hex": "0014053a8b54cf55fb780d028d96fa588931d1a44bbc",
        "address": "tb1qq5agk4x02hahsrgz3kt05kyfx8g6gjau922a02",
        "type": "witness_v0_keyhash"
      }
    },
    {
      "value": 0.00450342,
      "n": 1,
      "scriptPubKey": {
        "asm": "0 ea2b6d134f5ef88677a786f92f1794b202bec13a",
        "desc": "addr(tb1qag4k6y60tmugvaa8smuj79u5kgptasf65x7pzd)#j7es3jpp",
        "hex": "0014ea2b6d134f5ef88677a786f92f1794b202bec13a",
        "address": "tb1qag4k6y60tmugvaa8smuj79u5kgptasf65x7pzd",
        "type": "witness_v0_keyhash"
      }
    }
  ]
}

bitcoin-cli -datadir="." gettransaction "$TXID" | jq '{txid: .txid, wtxid: .wtxid, confirmations: .confirmations}'
{
  "txid": "133477ca67385c43436488275e13598c16596bba438954e80aabd64c2d2f63a0",
  "wtxid": "491c62d1bec78b7704db7ae4d6826e9da7a784f8f5f90a3a5662300bea8a080d",
  "confirmations": 3
}
```

Ao inspecionar a transação, vemos no campo `vin` que o `scriptSig` está vazio e os dados de desbloqueio aparecem em `txinwitness`, contendo a assinatura (primeiro elemento) e a chave pública (segundo elemento). Esse é o comportamento típico de uma entrada **P2WPKH nativa**: o witness substitui o antigo papel do `scriptSig`.

Nos `vout`, os destinos aparecem como `witness_v0_keyhash`, cada um identificado pelo endereço Bech32 (`tb1...`). No exemplo acima, temos duas saídas: uma de **0.00050000 sBTC** para o endereço `tb1qq5agk4x02hahsrgz3kt05kyfx8g6gjau922a02` (destinatário) e outra de **0.00450342 sBTC** para `tb1qag4k6y60tmugvaa8smuj79u5kgptasf65x7pzd` (endereço de troco gerado automaticamente pela carteira).

Além disso, ao comparar `txid` e `wtxid` no resultado do `gettransaction`, vemos que os dois valores são diferentes:

- `txid = 133477ca...f63a0`
- `wtxid = 491c62d1...a080d`

Isso acontece porque o **txid não inclui o witness**, enquanto o **wtxid inclui**. Essa distinção é justamente o que torna o SegWit resistente à maleabilidade de transações.

👉 Em resumo: no SegWit nativo, o `scriptSig` permanece vazio, as assinaturas e chaves públicas ficam no campo `witness`, os outputs são `witness_v0_keyhash`, e a rede diferencia `txid` e `wtxid`. Esse exemplo mostra na prática como o SegWit reorganizou as transações, tornando-as mais seguras e eficientes.

---

Com esses passos, conseguimos enxergar como o SegWit funciona de ponta a ponta: desde a derivação da chave pública e a construção do `witness program`, passando pela codificação em endereço Bech32 e pelo `scriptPubKey`, até a validação prática de uma transação na rede Signet. O SegWit não apenas resolveu o problema da maleabilidade e aumentou a eficiência do espaço em bloco, como também **introduziu uma nova forma de estruturar assinaturas e chaves públicas**, movendo-as do `scriptSig` para o campo *witness*. Essa separação tornou as transações mais leves e robustas, e abriu caminho para inovações futuras como a Lightning Network e o Taproot.

---

![IMG-20250722-WA0010.jpg](SegWit%20teoria%20e%20pr%C3%A1tica%20na%20Signet/7d12c3ef-1d0d-4c45-8cf9-96c904b1cb21.png)

Escrito por:  

Rafael Santos

[A Maior Escola de Bitcoin do Mundo | Area Bitcoin](https://www.areabitcoin.com.br/)

[Instagram (@area.bitcoin)](https://www.instagram.com/area.bitcoin/)

[Area Bitcoin](https://www.youtube.com/c/AreaBitcoin)
