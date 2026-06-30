# O futuro do Package Relay

Uma das ideias mais discutidas nos últimos anos dentro do desenvolvimento do Bitcoin é o **Package Relay**. A proposta parece simples: em vez de transmitir transações isoladamente pela rede, permitir que um node envie um conjunto de transações relacionadas como um único pacote.

Na prática, isso resolve diversos problemas envolvendo **CPFP (Child Pays For Parent)**, fee bumping e protocolos como a Lightning Network.

Nos últimos anos, as discussões tomaram um rumo interessante. O assunto deixou de ser "como implementar Package Relay" e passou a ser uma pergunta mais importante:

> Será que faz sentido tentar suportar qualquer tipo de pacote de transações?
> 

A resposta parece caminhar para um "talvez não".

### O sonho do Package Relay

Durante bastante tempo, a ideia era relativamente ambiciosa.

Depois da chegada do Cluster Mempool, esperava-se que seria possível validar praticamente qualquer conjunto de transações relacionadas. Um node poderia receber um pacote contendo várias transações, analisá-las em conjunto e decidir se aquele conjunto deveria entrar na mempool.

Na teoria isso parecia elegante. Na prática, porém, surgiram problemas muito mais difíceis do que o esperado.

### O problema não é validar. O problema é substituir.

Validar um conjunto arbitrário de transações já é complicado. Mas existe um problema ainda maior: o Replace-by-Fee (RBF).

Imagine um pacote que substitui parcialmente outro, possui conflitos internos e diferentes dependências entre suas transações. Dependendo da ordem em que essas transações são analisadas, o resultado pode mudar completamente.

Uma determinada sequência pode ser aceita. Outra sequência, contendo exatamente as mesmas transações, pode ser rejeitada.

Pior ainda: nem sempre existe uma definição objetiva de qual resultado seria "melhor". Mesmo que um node pudesse testar todas as combinações possíveis, ainda seria difícil definir qual delas deveria vencer.

Os desenvolvedores comentam que é muito fácil construir exemplos onde simplesmente não existe uma resposta correta.

Isso levou a uma conclusão importante:

> talvez o objetivo de suportar pacotes completamente arbitrários nunca seja realmente alcançável.
> 

### Talvez o caminho seja outro

Em vez de tentar resolver todos os casos possíveis, a discussão atual propõe algo bem mais pragmático:

> suportar muito bem os casos que realmente importam.
> 

Hoje o Bitcoin Core já consegue lidar razoavelmente bem com o caso chamado **1 Parent 1 Child (1p1c)**.

Nesse cenário existe apenas uma transação pai e uma transação filha, exatamente o formato utilizado por diversos mecanismos de CPFP.

Essa topologia cobre boa parte dos casos encontrados na Lightning Network e permite resolver conflitos de forma previsível.

Em vez de expandir rapidamente para estruturas extremamente complexas, talvez seja mais interessante tornar esse caso cada vez mais robusto.

### Ainda existem melhorias importantes

Mesmo deixando de lado os pacotes completamente arbitrários, ainda há bastante trabalho pela frente. Uma das propostas discutidas é eliminar o antigo relay baseado em TXIDs.

Hoje praticamente toda a rede utiliza **WTXIDs**, que identificam de forma única uma transação completa, incluindo sua witness. Já o TXID pode gerar ambiguidades, fazendo com que um node solicite repetidamente versões diferentes da mesma transação para vários peers.

A proposta conhecida como **BIP 331** tenta justamente modernizar esse processo, permitindo que um node solicite informações sobre ancestrais e baixe um pacote inteiro de transações relacionadas quando necessário.

Apesar das vantagens, os próprios desenvolvedores reconhecem que o ganho prático talvez não compense a complexidade de implementação neste momento.

Outra ideia é permitir que o próprio remetente tome a iniciativa de anunciar um pacote inteiro de transações quando souber que elas dependem umas das outras. Em vez de esperar que outro node descubra uma transação órfã e solicite seus pais, o pacote completo poderia ser enviado desde o início.

Isso reduz atrasos em alguns cenários, embora aumente um pouco o consumo de banda.

Também continua aberta a discussão sobre suportar novas topologias além do modelo 1 Parent 1 Child. Protocolos como Lightning e Ark possuem situações que envolvem cadeias maiores ou estruturas mais complexas de dependências entre transações. A dúvida é se isso realmente exigirá um novo protocolo de relay ou se melhorias na própria lógica da mempool e do tratamento de transações órfãs já serão suficientes.

### Prática: simulando um pacote pai + filho

Podemos visualizar a intuição do Package Relay com um experimento simples em `regtest`.

A ideia é criar duas transações relacionadas: A primeira será a transação **pai**. Ela terá uma taxa baixa. A segunda será a transação **filha**. Ela gastará uma saída da transação pai e pagará uma taxa maior.

Separadamente, a transação pai pode parecer pouco atrativa para entrar em um bloco. Mas, analisadas em conjunto, pai e filha podem formar um pacote interessante para mineradores. Esse é exatamente o princípio por trás do **CPFP**, ou **Child Pays For Parent**.

Primeiro, criamos uma carteira e mineramos alguns blocos:

```bash
bitcoin-cli -datadir="." createwallet "package"
ADDR=$(bitcoin-cli -datadir="." -rpcwallet=package getnewaddress)
bitcoin-cli -datadir="." generatetoaddress 101 $ADDR
```

Agora criamos um endereço de destino:

```bash
DEST=$(bitcoin-cli -datadir="." -rpcwallet=package getnewaddress)
```

Em seguida, criamos uma transação pai enviando uma pequena quantidade de bitcoin para esse endereço:

```bash
PARENT_TXID=$(bitcoin-cli -datadir="." -rpcwallet=package sendtoaddress $DEST 1)
```

Podemos consultar a transação na mempool:

```bash
bitcoin-cli -datadir="." getmempoolentry $PARENT_TXID
```

O ponto importante aqui é observar que essa transação ainda não foi minerada. Ela está apenas na mempool.

Agora vamos criar uma transação filha, gastando a saída recebida pela transação pai. Para isso, precisamos descobrir qual saída da transação pai pertence ao endereço `DEST`:

```bash
bitcoin-cli -datadir="." gettransaction $PARENT_TXID true
```

A saída mostra duas coisas importantes:

```json
"txid": "d1607e55c4a800a1251eca77208bdc90384826dc80ed77c2337be1766e8d25ff",
"wtxid": "09df0e87b74b633d6a787fa3a4d976af26441b45e3a51a103ca0eda6ede13f72",
"confirmations": 0,
"bip125-replaceable": "yes"
```

A transação ainda tem `0` confirmações, ou seja, está na mempool. Ela também é sinalizada como substituível por RBF.

Mais abaixo, vemos a saída recebida pela própria carteira:

```json
{
  "address": "bcrt1q79y3wrherl6a7mcq6xh5jy5eq88ak6l0md7tth",
  "category": "receive",
  "amount": 1.00000000,
  "vout": 1
}
```

Esse é o ponto que nos interessa. A transação pai criou uma saída de `1 BTC` no índice `vout: 1`. Agora podemos criar uma transação filha gastando exatamente essa saída ainda não confirmada.

Primeiro, criamos um novo endereço de destino:

```bash
CHILD_DEST=$(bitcoin-cli -datadir="." -rpcwallet=package getnewaddress)
```

Agora criamos a transação filha manualmente. Ela gastará o output `1` da transação pai:

```bash
CHILD_RAW=$(bitcoin-cli -datadir="." createrawtransaction \
  "[{\"txid\":\"$PARENT_TXID\",\"vout\":1}]" \
  "[{\"$CHILD_DEST\":0.9999}]")
```

Repare que estamos gastando `1 BTC`, mas enviando apenas `0.9999 BTC`. A diferença fica como taxa da transação filha:

```
1.0000 BTC - 0.9999 BTC = 0.0001 BTC
```

Agora assinamos a transação:

```bash
CHILD_SIGNED=$(bitcoin-cli -datadir="." -rpcwallet=package signrawtransactionwithwallet $CHILD_RAW | jq -r '.hex')
```

E transmitimos para a rede regtest:

```bash
CHILD_TXID=$(bitcoin-cli -datadir="." sendrawtransaction $CHILD_SIGNED)
```

Podemos consultar a transação filha na mempool:

```bash
bitcoin-cli -datadir="." getmempoolentry $CHILD_TXID
```

Agora temos duas transações não confirmadas relacionadas entre si:

```
Transação pai
d1607e55c4a800a1251eca77208bdc90384826dc80ed77c2337be1766e8d25ff
        ↓
Transação filha
$CHILD_TXID
```

A filha só pode ser minerada se a pai também for minerada. Para um minerador, portanto, a decisão relevante não é olhar apenas a taxa da transação pai ou apenas a taxa da transação filha, mas sim o conjunto formado pelas duas.

É exatamente essa a intuição por trás do Package Relay.

Em vez de tratar transações dependentes como eventos isolados, o node passa a conseguir raciocinar sobre um pacote:

```
pai + filha
```

Esse caso simples é chamado de **1 Parent 1 Child**, ou **1p1c**. Ele não cobre todos os formatos possíveis de pacotes, mas cobre um caso extremamente importante: uma transação filha pagando taxa suficiente para carregar uma transação pai junto com ela.

### Uma mudança de mentalidade

Talvez o aspecto mais interessante dessa discussão seja perceber como o desenvolvimento do Bitcoin costuma evoluir.

Em vez de perseguir uma solução extremamente genérica e elegante, os desenvolvedores parecem cada vez mais inclinados a construir mecanismos simples, previsíveis e voltados para casos reais.

O objetivo deixou de ser criar um Package Relay capaz de resolver qualquer combinação imaginável de transações.

Agora a prioridade parece ser garantir que os cenários utilizados diariamente por Lightning, CPFP e outros protocolos funcionem de maneira eficiente, segura e previsível.

Esse pode ser o caminho que permitirá ao Package Relay finalmente sair do papel e se tornar uma parte importante da infraestrutura do Bitcoin.

por: Rafael Santos
