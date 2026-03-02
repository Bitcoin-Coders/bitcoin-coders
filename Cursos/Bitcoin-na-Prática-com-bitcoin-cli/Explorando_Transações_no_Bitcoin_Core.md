# Explorando Transações no Bitcoin Core

por Rafael Santos

Uma transação no Bitcoin é a maneira pela qual podemos transferir Bitcoins entre diferentes endereços. Existe uma série de componentes que fazem parte de uma transação.  Podemos destacar os principais:

### 🔑 **Componentes de uma Transação Bitcoin**

1. **Identificação**
    - **TXID**: identificador único da transação (hash).
    - **Versão**: número que indica o formato da transação.
2. **Inputs (entradas)**
    - **TXID anterior**: aponta para a transação de onde vem o valor.
    - **Índice (vout)**: posição do output dentro da transação anterior.
    - **ScriptSig / Witness**: dados de desbloqueio que provam a posse do UTXO.
    - **Sequence**: usado para controle de tempo (nLockTime, RBF).
3. **Outputs (saídas)**
    - **Valor (satoshis)**: quantidade de BTC enviada.
    - **ScriptPubKey**: regras de gasto do output.
4. **Metadados**
    - **nLockTime**: define quando a transação pode ser incluída em um bloco.
    - **Size / vSize**: tamanho da transação em bytes / peso virtual (impacta na taxa).
5. **Taxa (Fee)**
    - Calculada implicitamente:
        
        ```bash
        Fee = Soma(inputs) – Soma(outputs)
        ```
        

Dentre esses componentes, as **Outputs** são as principais. O **modelo de UTXO (Unspent Transaction Output)** é a base do funcionamento do Bitcoin. Diferente de sistemas de contas tradicionais, onde cada endereço possui um saldo acumulado, no Bitcoin cada transação cria saídas (*outputs*) que podem ou não ter sido gastas. Um **UTXO** é justamente uma saída ainda não gasta, que funciona como uma “nota de dinheiro digital” com valor definido. Para realizar um pagamento, o usuário seleciona um ou mais UTXOs como entrada (*inputs*) e gera novas saídas que transferem os valores desejados. Caso o total dos UTXOs utilizados seja maior que o valor a ser enviado, o excedente volta ao próprio usuário como “troco” em um novo UTXO, e a diferença entre entradas e saídas corresponde à taxa de mineração (*fee*).

Em termos técnicos, cada UTXO é identificado de forma única por um **par `(txid, vout)`**, onde `txid` é o identificador da transação que o criou e `vout` é o índice da saída dentro dessa transação. Além desse identificador, um UTXO possui dois atributos principais: o **valor** em satoshis (quantidade de bitcoin representada) e o **scriptPubKey**, que define as condições de gasto, normalmente exigindo a assinatura digital correspondente a uma chave pública. Quando um UTXO é utilizado como entrada em uma nova transação, ele deixa de existir, dando origem a novos outputs que se tornam UTXOs disponíveis para o futuro. Esse mecanismo garante a rastreabilidade de todos os bitcoins na rede e evita gastos duplos, já que cada UTXO só pode ser gasto uma vez.

Assim, o chamado **saldo** de uma pessoa em Bitcoin não existe de forma explícita na blockchain como em uma conta bancária. O que se entende como saldo é, na verdade, a **soma de todos os UTXOs que pertencem a um usuário e que ele consegue desbloquear** com suas chaves privadas. Cada carteira de Bitcoin mantém essa lista de UTXOs associados aos endereços do usuário, e sempre que ele realiza uma transação, alguns desses UTXOs são consumidos e substituídos por novos, refletindo a movimentação de valores.

A imagem abaixo mostra o fluxo das transações com seus componentes.

![Transaçoes.png](../../assets/Artigo07-Transacoes.webp)

Na imagem, observamos a relação entre três transações encadeadas. A **Transação 1** consome um UTXO de 1 BTC e o divide em duas saídas: 0,4 BTC e 0,5 BTC, com uma taxa de 0,1 BTC. Já a **Transação 2** utiliza um UTXO de 0,5 BTC, gerando duas novas saídas de 0,3 BTC e 0,15 BTC, pagando 0,05 BTC de taxa. A **Transação 3** mostra o princípio da composição de UTXOs: ela reúne como entrada a saída de 0,5 BTC da Transação 1 e a saída de 0,3 BTC da Transação 2, totalizando 0,8 BTC de inputs. A partir disso, cria duas saídas de 0,6 BTC e 0,1 BTC, resultando em uma taxa de 0,1 BTC. Esse encadeamento ilustra claramente como os UTXOs fluem entre transações, sendo consumidos e recriados continuamente, mantendo a coerência do modelo do Bitcoin.

De forma didática, podemos rodar um script que simule o cenário da imagem. Utilizaremos a rede `regtest`, já que precisamos ter um controle dos UTXO iniciais (com 1.0 BTC e 0.5 BTC).

```bash
BASE_CLI='bitcoin-cli -datadir=.'
if ! $BASE_CLI listwallets | grep -q '"w"'; then
  $BASE_CLI createwallet "w" >/dev/null
fi
cli='bitcoin-cli -datadir=. -rpcwallet=w'
SEND_MAXFEERATE=0.9   # abaixo de 1 BTC/kvB para não ser rejeitado

# Minerar saldo base
MINER=$($cli getnewaddress)
$cli generatetoaddress 101 "$MINER" >/dev/null

# Criar UTXOs iniciais: 1.0 BTC e 0.5 BTC
ADDR_1=$($cli getnewaddress)
ADDR_05=$($cli getnewaddress)
TXFUND1=$($cli sendtoaddress "$ADDR_1" 1.0)
TXFUND2=$($cli sendtoaddress "$ADDR_05" 0.5)
$cli generatetoaddress 1 "$MINER" >/dev/null

VOUT1=$($cli gettransaction "$TXFUND1" | jq -r --arg a "$ADDR_1" '.details[] | select(.address==$a and .category=="receive") | .vout' | head -n1)
VOUT05=$($cli gettransaction "$TXFUND2" | jq -r --arg a "$ADDR_05" '.details[] | select(.address==$a and .category=="receive") | .vout' | head -n1)

echo "== UTXOs iniciais =="
echo "1.0 BTC  -> $TXFUND1:$VOUT1"
echo "0.5 BTC  -> $TXFUND2:$VOUT05"
echo

# Endereços de destino
C=$($cli getnewaddress)   # 0.4
D=$($cli getnewaddress)   # 0.5
E=$($cli getnewaddress)   # 0.3
F=$($cli getnewaddress)   # 0.15
G=$($cli getnewaddress)   # 0.6
H=$($cli getnewaddress)   # 0.1

########################################
# Tx1: 1.0 -> 0.4 + 0.5  (fee = 0.1)
########################################
RAW1=$($cli createrawtransaction "[{\"txid\":\"$TXFUND1\",\"vout\":$VOUT1}]" "{\"$C\":0.4, \"$D\":0.5}")
HEX1=$($cli signrawtransactionwithwallet "$RAW1" | jq -r .hex)
TX1=$($cli sendrawtransaction "$HEX1" $SEND_MAXFEERATE)
$cli generatetoaddress 1 "$MINER" >/dev/null
echo "Tx1: $TX1"

VOUT_04=$($cli gettransaction "$TX1" | jq -r --arg a "$C" '.details[] | select(.address==$a and .category=="receive") | .vout' | head -n1)
VOUT_05_FROM_TX1=$($cli gettransaction "$TX1" | jq -r --arg a "$D" '.details[] | select(.address==$a and .category=="receive") | .vout' | head -n1)

########################################
# Tx2: 0.5 -> 0.3 + 0.15  (fee = 0.05)
########################################
RAW2=$($cli createrawtransaction "[{\"txid\":\"$TXFUND2\",\"vout\":$VOUT05}]" "{\"$E\":0.3, \"$F\":0.15}")
HEX2=$($cli signrawtransactionwithwallet "$RAW2" | jq -r .hex)
TX2=$($cli sendrawtransaction "$HEX2" $SEND_MAXFEERATE)
$cli generatetoaddress 1 "$MINER" >/dev/null
echo "Tx2: $TX2"

VOUT_03=$($cli gettransaction "$TX2" | jq -r --arg a "$E" '.details[] | select(.address==$a and .category=="receive") | .vout' | head -n1)

########################################
# Tx3: (0.5 da Tx1) + (0.3 da Tx2) -> 0.6 + 0.1 (fee = 0.1)
########################################
RAW3=$($cli createrawtransaction \
  "[{\"txid\":\"$TX1\",\"vout\":$VOUT_05_FROM_TX1},{\"txid\":\"$TX2\",\"vout\":$VOUT_03}]" \
  "{\"$G\":0.6, \"$H\":0.1}")
HEX3=$($cli signrawtransactionwithwallet "$RAW3" | jq -r .hex)
TX3=$($cli sendrawtransaction "$HEX3" $SEND_MAXFEERATE)
$cli generatetoaddress 1 "$MINER" >/dev/null
echo "Tx3: $TX3"
echo

########################################
# Resumo simples das transações
########################################
echo
echo "==================== RESUMO ===================="

echo "-- Tx1 ($TX1)"
echo "Inputs:"
$cli decoderawtransaction "$HEX1" | jq -r '.vin[] | "  - \(.txid):\(.vout)"'
echo "Outputs:"
$cli decoderawtransaction "$HEX1" | jq -r '.vout[] | "  - \(.value) BTC -> \(.scriptPubKey.address)"'
echo -n "Fee: "
$cli gettransaction "$TX1" | jq -r '.fee'
echo

echo "-- Tx2 ($TX2)"
echo "Inputs:"
$cli decoderawtransaction "$HEX2" | jq -r '.vin[] | "  - \(.txid):\(.vout)"'
echo "Outputs:"
$cli decoderawtransaction "$HEX2" | jq -r '.vout[] | "  - \(.value) BTC -> \(.scriptPubKey.address)"'
echo -n "Fee: "
$cli gettransaction "$TX2" | jq -r '.fee'
echo

echo "-- Tx3 ($TX3)"
echo "Inputs:"
$cli decoderawtransaction "$HEX3" | jq -r '.vin[] | "  - \(.txid):\(.vout)"'
echo "Outputs:"
$cli decoderawtransaction "$HEX3" | jq -r '.vout[] | "  - \(.value) BTC -> \(.scriptPubKey.address)"'
echo -n "Fee: "
$cli gettransaction "$TX3" | jq -r '.fee'
echo "==============================================="
```

Explicando cada trecho do código…

### 1. Preparação do ambiente

Antes de criar as transações, o script configura um ambiente de testes no Bitcoin Core (`regtest`), cria uma carteira e gera saldo inicial.

```bash
BASE_CLI='bitcoin-cli -datadir=.'
if ! $BASE_CLI listwallets | grep -q '"w"'; then
  $BASE_CLI createwallet "w" >/dev/null
fi

cli='bitcoin-cli -datadir=. -rpcwallet=w'
SEND_MAXFEERATE=0.9   # abaixo de 1 BTC/kvB para não ser rejeitado

# Minerar saldo base
MINER=$($cli getnewaddress)
$cli generatetoaddress 101 "$MINER" >/dev/null
```

👉 Aqui garantimos que existe uma carteira chamada `w`, conectamos a ela e mineramos blocos para ter saldo disponível.

### 2. Criação dos UTXOs iniciais

O próximo passo é criar duas saídas (UTXOs): uma de 1.0 BTC e outra de 0.5 BTC.

```bash
# Criar UTXOs iniciais: 1.0 BTC e 0.5 BTC
ADDR_1=$($cli getnewaddress)
ADDR_05=$($cli getnewaddress)
TXFUND1=$($cli sendtoaddress "$ADDR_1" 1.0)
TXFUND2=$($cli sendtoaddress "$ADDR_05" 0.5)
$cli generatetoaddress 1 "$MINER" >/dev/null
```

👉 É como se o usuário tivesse recebido duas “notas de dinheiro digital”, que depois serão gastas nas transações.

### 3. Transação 1 (Tx1)

Nesta transação, gastamos o UTXO de 1.0 BTC e criamos duas saídas: 0.4 e 0.5 BTC, pagando 0.1 BTC de taxa.

```bash
# Tx1: 1.0 -> 0.4 + 0.5  (fee = 0.1)
RAW1=$($cli createrawtransaction "[{\"txid\":\"$TXFUND1\",\"vout\":$VOUT1}]" "{\"$C\":0.4, \"$D\":0.5}")
HEX1=$($cli signrawtransactionwithwallet "$RAW1" | jq -r .hex)
TX1=$($cli sendrawtransaction "$HEX1" $SEND_MAXFEERATE)
$cli generatetoaddress 1 "$MINER" >/dev/null
```

👉 Essa parte demonstra como um único UTXO pode ser dividido em dois novos UTXOs menores.

### 4. Transação 2 (Tx2)

Aqui, pegamos o UTXO de 0.5 BTC criado no início e o dividimos em 0.3 e 0.15 BTC, pagando 0.05 BTC de taxa.

```bash
# Tx2: 0.5 -> 0.3 + 0.15  (fee = 0.05)
RAW2=$($cli createrawtransaction "[{\"txid\":\"$TXFUND2\",\"vout\":$VOUT05}]" "{\"$E\":0.3, \"$F\":0.15}")
HEX2=$($cli signrawtransactionwithwallet "$RAW2" | jq -r .hex)
TX2=$($cli sendrawtransaction "$HEX2" $SEND_MAXFEERATE)
$cli generatetoaddress 1 "$MINER" >/dev/null
```

### 5. Transação 3 (Tx3)

Finalmente, combinamos dois UTXOs diferentes (0.5 BTC da Tx1 e 0.3 BTC da Tx2) para criar uma transação com múltiplos inputs. O total (0.8 BTC) é gasto em duas saídas (0.6 + 0.1), com 0.1 BTC de taxa.

```bash
# Tx3: (0.5 da Tx1) + (0.3 da Tx2) -> 0.6 + 0.1 (fee = 0.1)
RAW3=$($cli createrawtransaction \
  "[{\"txid\":\"$TX1\",\"vout\":$VOUT_05_FROM_TX1},{\"txid\":\"$TX2\",\"vout\":$VOUT_03}]" \
  "{\"$G\":0.6, \"$H\":0.1}")
HEX3=$($cli signrawtransactionwithwallet "$RAW3" | jq -r .hex)
TX3=$($cli sendrawtransaction "$HEX3" $SEND_MAXFEERATE)
$cli generatetoaddress 1 "$MINER" >/dev/null
```

👉 Esse exemplo evidencia o funcionamento do modelo UTXO: múltiplos inputs podem ser combinados em uma única transação.

### 6. Resumo final

No fim, o script imprime um resumo de cada transação, mostrando inputs, outputs e taxas.

```bash
echo "-- Tx1 ($TX1)"
echo "Inputs:"
$cli decoderawtransaction "$HEX1" | jq -r '.vin[] | "  - \(.txid):\(.vout)"'
echo "Outputs:"
$cli decoderawtransaction "$HEX1" | jq -r '.vout[] | "  - \(.value) BTC -> \(.scriptPubKey.address)"'
echo -n "Fee: "
$cli gettransaction "$TX1" | jq -r '.fee'
```

👉 Esse resumo facilita visualizar o **fluxo dos valores** e como as taxas são a diferença entre total de inputs e total de outputs.

Podemos finalizar com as diferentes maneiras que o Bitcoin Core possui para fazer transações.

## Formas de criar transações no Bitcoin Core

No Bitcoin Core, existem diferentes níveis de abstração para criar uma transação, que vão desde comandos mais simples e automáticos até fluxos totalmente manuais.

### 1. Enviando BTCs de forma simples

A maneira **mais simples** é através de comandos de alto nível como `sendtoaddress` ou `sendmany`. Nesses casos, o usuário informa apenas o endereço de destino e o valor a ser enviado (ou vários destinos no caso do `sendmany`), e o Core se encarrega de todo o resto: seleciona automaticamente os UTXOs disponíveis na carteira, calcula o troco, define a taxa adequada e transmite a transação para a rede. Esse é o método mais prático para usuários comuns e para o uso cotidiano de uma carteira, como pode ser visto abaixo.

```bash
bitcoin-cli -datadir="." -rpcwallet=w   sendtoaddress bcrt1qszaegaf7drfa9kfql057jle78yd8ukhrhfr9lx 0.1
44e204c91a032e05b075960977ef79219e706ef720096d86dc562f86ec775244
```

```bash
bitcoin-cli -datadir="." -rpcwallet=w \
  sendmany "" '{"bcrt1qrpruxdtawnxtqtugsar2yglvr2xf50kd7rkau2":0.2, "bcrt1qxt6ujulks2es4wcfz5emdeklyj23ccrdqwagx5":0.3}'
896f5d684cabe6ee28ef78d0d97d0f5deaa88471df563f4223fcef206a4bdd96
```

Tanto no `sendtoaddress` quanto no `sendmany`, o **resultado do comando é o TXID da transação criada e transmitida**.

### 2. Enviando BTCs de forma bruta

Já no **nível mais baixo**, temos a criação de **raw transactions**, como mostrado neste artigo. Nesse fluxo, a responsabilidade é totalmente do usuário: indicar exatamente quais UTXOs serão usados como inputs, quais endereços receberão os valores de saída, quanto ficará de troco e, por consequência, qual será a taxa de mineração. A transação é montada com `createrawtransaction`, assinada com `signrawtransactionwithwallet` e, por fim, transmitida com `sendrawtransaction`. Embora mais trabalhosa, essa abordagem oferece controle total e é fundamental em cenários de estudo, auditoria ou em usos avançados, como transações multisig e scripts personalizados.

O exemplo abaixo mostra esse processo usando um UTXO de **0.15 BTC** como entrada, para enviar **0.14 BTC** a um endereço específico, deixando a diferença (0.01 BTC) como taxa de mineração.

**a. Montar a transação**

Selecionamos o `txid` e o `vout` do UTXO que queremos gastar e definimos o endereço de destino com o valor:

```bash
bitcoin-cli -datadir=. -rpcwallet=w createrawtransaction \
  '[{"txid":"ac6c1f851d4e669dcb3d6fceddbc6e4a5b38e4905887d5dc98a14e9b2c6bccf7","vout":1}]' \
  '{"bcrt1qqjj4dkz96a68fuwhr7uwstjm5w67lgzdag9yvq":0.14}'
0200000001f7cc6b2c9b4ea198dcd5875890e4385b4a6ebcddce6f3dcb9d664e1d851f6cac0100000000fdffffff01809fd5000000000016001404a556d845d77474f1d71fb8e82e5ba3b5efa04d00000000
```

Esse comando retorna um **hexadecimal bruto** (sem assinatura), que representa a transação em formato binário.

---

**b. Assinar a transação**

Em seguida, passamos esse hex para o comando de assinatura, que insere as assinaturas digitais necessárias:

```bash
bitcoin-cli -datadir=. -rpcwallet=w signrawtransactionwithwallet "0200000001f7cc6b2c9b4ea198dcd5875890e4385b4a6ebcddce6f3dcb9d664e1d851f6cac0100000000fdffffff01809fd5000000000016001404a556d845d77474f1d71fb8e82e5ba3b5efa04d00000000"
{
  "hex": "02000000000101f7cc6b2c9b4ea198dcd5875890e4385b4a6ebcddce6f3dcb9d664e1d851f6cac0100000000fdffffff01809fd5000000000016001404a556d845d77474f1d71fb8e82e5ba3b5efa04d02473044022046247b465a431eff64eee143d9d730ef58189d940fad575ff1809d72c00657a102205f22a7951bfa7ab690cf8cdbaf67fddef32402be39fd3a06b1f6e58a59f4e1e60121033be379dcb5d80de0c7c64fa09845497aee5c5489603bd727a4f5670d13e39d8200000000",
  "complete": true
}
```

O resultado inclui um novo **hex assinado** (campo `"hex"`) e a indicação `"complete": true`, mostrando que a transação está pronta para ser transmitida.

---

**c. Transmitir a transação**

Por fim, enviamos o hex assinado para a rede:

```bash
bitcoin-cli -datadir=. -rpcwallet=w sendrawtransaction "02000000000101f7cc6b2c9b4ea198dcd5875890e4385b4a6ebcddce6f3dcb9d664e1d851f6cac0100000000fdffffff01809fd5000000000016001404a556d845d77474f1d71fb8e82e5ba3b5efa04d02473044022046247b465a431eff64eee143d9d730ef58189d940fad575ff1809d72c00657a102205f22a7951bfa7ab690cf8cdbaf67fddef32402be39fd3a06b1f6e58a59f4e1e60121033be379dcb5d80de0c7c64fa09845497aee5c5489603bd727a4f5670d13e39d8200000000"
c3768db0ffcaa902539e8e4a9498de0588cefce865510c54aa4502da6aa18461
```

O comando retorna o **TXID** da transação enviada.

⚠️ **Observação importante**: os comandos acima devem ser executados usando os **hexadecimais resultantes do seu próprio ambiente**. Cada execução de `createrawtransaction` e `signrawtransactionwithwallet` gera valores diferentes de hex, dependendo dos UTXOs e endereços em uso.

### 3. Enviando BTCs de forma semi-automática

Existe também o caminho “intermediário”:

**Montar a transação SEM inputs (só o(s) destinatário(s) e valores).**

```bash
bitcoin-cli -datadir=. -rpcwallet=w \
  createrawtransaction '[]' \
  '{"bcrt1qva34k0dzqwsaezxxhk2dzt2gqh9mh7rff9djda":0.42}'
02000000000180de80020000000016001467635b3da203a1dc88c6bd94d12d4805cbbbf86900000000
```

O comando retorna um **hex bruto** (sem assinatura), que será usado na próxima etapa.

**Deixar o Core completar (selecionar UTXOs, criar troco, calcular taxa)**

```bash
bitcoin-cli -datadir=. -rpcwallet=w \
  fundrawtransaction 02000000000180de80020000000016001467635b3da203a1dc88c6bd94d12d4805cbbbf86900000000
{
  "hex": "02000000023d94159e98322b8c910a11b417c60b32baf9d937962c14b077414a6af2deb2870000000000fdffffff136595a2f0ddb78ce8cf87015794fc493f4f20c53080109a932ab95a1f18b8ee0100000000fdffffff0280de80020000000016001467635b3da203a1dc88c6bd94d12d4805cbbbf8692055c600000000001600142fc983585f862be671f4718497b9f95445afac9100000000",
  "fee": 0.00002080,
  "changepos": 1
}
```

A saída traz um JSON com:

- `"hex"` → o **hex já “preenchido”** (com inputs/troco);
- `"fee"` → taxa estimada;
- `"changepos"` → posição do output de troco (ou -1 se não houver).

O campo "hex" dessa resposta será usado no próximo comando.

**Assinar com as chaves da carteira**

```bash
bitcoin-cli -datadir=. -rpcwallet=w \
  signrawtransactionwithwallet 02000000023d94159e98322b8c910a11b417c60b32baf9d937962c14b077414a6af2deb2870000000000fdffffff136595a2f0ddb78ce8cf87015794fc493f4f20c53080109a932ab95a1f18b8ee0100000000fdffffff0280de80020000000016001467635b3da203a1dc88c6bd94d12d4805cbbbf8692055c600000000001600142fc983585f862be671f4718497b9f95445afac9100000000
{
  "hex": "020000000001023d94159e98322b8c910a11b417c60b32baf9d937962c14b077414a6af2deb2870000000000fdffffff136595a2f0ddb78ce8cf87015794fc493f4f20c53080109a932ab95a1f18b8ee0100000000fdffffff0280de80020000000016001467635b3da203a1dc88c6bd94d12d4805cbbbf8692055c600000000001600142fc983585f862be671f4718497b9f95445afac9102473044022015c881a9f666221593e0b01f134ee231bed33d45ad4fe100da0e8c694c69d8eb02207ec43229fb1932b7f2ae1a59fb241f4d6f9a525e36a51744600cb96aea98466101210229b43fc50701cfabbe3db369a715ee63156eaa2036c9b9d3f452310c751ffec202473044022020d22099a9e0a398313b562c631e1378c0398500cec3281d70f11ef44ce9024602200ce77f7d3c1e7bc84ea52611098b882feed948cf77b0c5fc54db619a94f6bdc8012102e03cddcc5d13d4a5e906d1a21710d0945b01296f343e77125fe4bd7f46c8149700000000",
  "complete": true
}
```

O campo “hex” representa a transação assinada e será usado no comando a seguir para transmitir.

**Transmitir para a rede**

```bash
bitcoin-cli -datadir=. -rpcwallet=w \
  sendrawtransaction 020000000001023d94159e98322b8c910a11b417c60b32baf9d937962c14b077414a6af2deb2870000000000fdffffff136595a2f0ddb78ce8cf87015794fc493f4f20c53080109a932ab95a1f18b8ee0100000000fdffffff0280de80020000000016001467635b3da203a1dc88c6bd94d12d4805cbbbf8692055c600000000001600142fc983585f862be671f4718497b9f95445afac9102473044022015c881a9f666221593e0b01f134ee231bed33d45ad4fe100da0e8c694c69d8eb02207ec43229fb1932b7f2ae1a59fb241f4d6f9a525e36a51744600cb96aea98466101210229b43fc50701cfabbe3db369a715ee63156eaa2036c9b9d3f452310c751ffec202473044022020d22099a9e0a398313b562c631e1378c0398500cec3281d70f11ef44ce9024602200ce77f7d3c1e7bc84ea52611098b882feed948cf77b0c5fc54db619a94f6bdc8012102e03cddcc5d13d4a5e906d1a21710d0945b01296f343e77125fe4bd7f46c8149700000000
200e8803b8e081e6ef96d546af2d943f457720b3dd973fe25421b24cecbb1104
```

O comando `sendrawtransaction` transmite a transação e retorna seu **TXID**.

---

Neste artigo vimos, na prática, como uma transação Bitcoin é construída, desde o modelo de UTXOs até a criação de transações simples e compostas no **Bitcoin Core**. Exploramos tanto o envio automático com comandos de alto nível quanto a forma mais manual e controlada de criar transações brutas, onde o usuário define cada detalhe, inputs, outputs e taxas.

Esse exercício mostra como o modelo de UTXO dá ao Bitcoin sua transparência e segurança, permitindo rastrear cada satoshi desde sua origem. Ao mesmo tempo, ilustra que por trás de uma simples transferência existe um conjunto de componentes técnicos que garantem a validade e a imutabilidade das transações.

Nos próximos artigos, vamos aprofundar em pontos fundamentais como:

- O funcionamento do **ScriptPubKey** e do **ScriptSig/Witness**, que formam a base do sistema de validação de gastos no Bitcoin.
- O **acompanhamento de transações na mempool**, analisando como elas circulam pela rede antes de serem incluídas em blocos.

Esses tópicos vão nos permitir entender, em nível ainda mais profundo, como o Bitcoin garante a segurança das transações e como cada nó da rede participa do processo de validação.
