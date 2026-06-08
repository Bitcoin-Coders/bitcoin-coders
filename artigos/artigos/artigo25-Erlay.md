# Erlay: a proposta que pode tornar a rede Bitcoin mais eficiente

Quando pensamos na escalabilidade do Bitcoin, normalmente imaginamos blocos, taxas, Lightning Network ou capacidade de processamento. Porém, existe outra camada igualmente importante: a comunicação entre os nodes.

Antes que uma transação seja incluída em um bloco, ela precisa percorrer a rede. Da mesma forma, antes que um bloco seja validado globalmente, ele precisa chegar aos demais participantes. Tudo isso depende do protocolo P2P do Bitcoin.

Embora esse mecanismo funcione muito bem há mais de quinze anos, ele possui um custo: uma quantidade significativa de tráfego é gerada apenas para anunciar a existência de novas transações.

Para reduzir esse custo surgiu o Erlay, uma proposta que busca tornar a propagação de transações muito mais eficiente sem alterar nenhuma regra de consenso do Bitcoin.

Neste artigo vamos entender como a propagação funciona atualmente, quais são suas limitações e como o Erlay pretende melhorar a situação.

### Como os nodes anunciam novas transações

Quando um node recebe uma transação válida, ele não envia imediatamente a transação completa para todos os seus peers. O primeiro passo é enviar uma mensagem chamada `inv` (inventory). Essa mensagem contém apenas o identificador da transação (txid) e funciona como um aviso:

> "Eu conheço uma nova transação."
> 

Se o peer ainda não possuir essa transação em sua mempool, ele responde com uma mensagem `getdata`. Somente então a transação completa é transmitida através de uma mensagem `tx`.

O fluxo simplificado é:

```
Node A recebe uma nova transação

A → inv → B
A → inv → C
A → inv → D

B → getdata → A
C → getdata → A
D → getdata → A

A → tx → B
A → tx → C
A → tx → D
```

Esse mecanismo é extremamente robusto. Mesmo que alguns peers estejam lentos ou desconectados, a informação encontra diversos caminhos alternativos para percorrer a rede.

**Onde está o problema?**

À primeira vista, esse modelo parece perfeito. O detalhe é que a rede Bitcoin possui milhares de nodes e um fluxo constante de novas transações. Sempre que uma nova transação aparece, ela é anunciada para diversos peers. Muitos desses peers provavelmente receberão a mesma informação por outros caminhos também.

Imagine uma rede simplificada:

```
      B
      |
D --- A --- C
      |
      E
```

Uma nova transação chega ao Node A. Ele anuncia essa transação para B, C, D e E. Mas talvez B também receba a mesma transação através de outro node conectado. O mesmo vale para C, D e E.

Essa redundância é intencional e ajuda a tornar a rede resiliente. O problema é que ela gera um volume significativo de mensagens. Quanto mais conexões um node mantém, maior tende a ser o tráfego necessário para anunciar novas transações.

### A observação por trás do Erlay

Os desenvolvedores perceberam algo interessante. Embora novas transações apareçam continuamente, as mempools dos nodes honestos costumam ser extremamente parecidas.

Imagine dois nodes:

**Node 1**

```
100.000 transações
```

**Node 2**

```
99.998 transações
```

Na prática, ambos já conhecem quase tudo o que existe na rede naquele momento. Talvez o Node 1 tenha recebido primeiro duas transações que ainda não chegaram ao Node 2. Ou talvez o Node 2 conheça algumas transações que ainda não foram vistas pelo Node 1. Mas, no geral, os conjuntos são quase idênticos.

Essa observação levou à seguinte pergunta:

> Se as mempools já são quase iguais, precisamos continuar dependendo apenas de anúncios individuais para mantê-las sincronizadas?
> 

É justamente essa pergunta que o Erlay tenta responder.

**Como o Erlay funciona**

A ideia central do Erlay não é transmitir mempools completas. Isso seria inviável. Também não significa que as novas transações deixarão de ser propagadas normalmente. O que muda é a forma como os nodes verificam se estão sincronizados.

Imagine a seguinte situação.

**Node 1**

```
tx1
tx2
tx3
tx4
tx5
tx6
```

**Node 2**

```
tx1
tx2
tx3
tx4
tx5
tx7
```

As transações `tx6` e `tx7` chegaram por caminhos diferentes na rede. Talvez `tx6` tenha sido recebida primeiro por um peer conectado ao Node 1, enquanto `tx7` chegou primeiro ao Node 2. Nesse cenário:

```
Node 1 não possui tx7
Node 2 não possui tx6
```

Todo o restante já é conhecido por ambos. Com o protocolo atual, a sincronização depende principalmente dos anúncios individuais das novas transações.

O Erlay introduz um mecanismo complementar chamado **Set Reconciliation**. Em vez de depender exclusivamente desses anúncios, os nodes podem comparar periodicamente resumos matemáticos compactos de suas mempools.

Ao fazer essa comparação, eles descobrem rapidamente quais transações estão faltando em cada lado. Após a reconciliação:

```
Node 1:
tx1 tx2 tx3 tx4 tx5 tx6 tx7

Node 2:
tx1 tx2 tx3 tx4 tx5 tx6 tx7
```

Agora ambos possuem exatamente o mesmo conjunto.

Quando esses nodes realizarem novas reconciliações com outros peers da rede, não será necessário transmitir novamente `tx6` ou `tx7`, pois elas já estarão presentes em suas mempools.

Em outras palavras, conforme os nodes vão trocando apenas as diferenças, as mempools convergem rapidamente para o mesmo estado, reduzindo a necessidade de novos anúncios e sincronizações futuras.

### Minisketch e Set Reconciliation

Para realizar essa comparação eficiente, a proposta utiliza uma técnica chamada Set Reconciliation. A implementação é baseada em uma estrutura conhecida como Minisketch.

A ideia é elegante. Em vez de enviar listas enormes de txids, cada node gera um pequeno resumo matemático de sua mempool. Vamos imaginar um exemplo simplificado.

**Node 1**

```
10
20
30
40
50
60
```

**Node 2**

```
10
20
30
40
50
70
```

A diferença entre os conjuntos é:

```
60
70
```

Uma solução simples seria transmitir toda a lista de elementos de cada lado. Porém, conforme o conjunto cresce, isso rapidamente se torna inviável.

O Minisketch utiliza uma abordagem diferente. Cada node gera um resumo matemático compacto do conjunto que possui. Esse resumo não contém a lista completa dos elementos, mas preserva informações suficientes para que as diferenças possam ser recuperadas posteriormente.

Quando os resumos são comparados, o algoritmo consegue reconstruir apenas os elementos que diferem entre os conjuntos:

```
60
70
```

sem que seja necessário transmitir todos os demais elementos.

O importante é perceber que o Minisketch não tenta reconstruir o conjunto inteiro. Ele foi projetado especificamente para recuperar apenas as diferenças. Por isso ele funciona tão bem quando os conjuntos são quase iguais, como costuma acontecer com as mempools dos nodes Bitcoin.

Tecnicamente, o Minisketch utiliza técnicas de codificação de erro semelhantes às usadas em telecomunicações para reconstruir apenas as diferenças entre conjuntos, mas os detalhes matemáticos estão além do escopo deste artigo.

### Laboratório: observando a propagação atual

Vamos visualizar o modelo atual utilizando quatro nodes em regtest.

**Passo 1 — Conectando os nodes**

Considere quatro instâncias do Bitcoin Core rodando em regtest:

```
Node A (port=28441)
Node B (port=28542)
Node C (port=28643)
Node D (port=28744)
```

No **Node A**, conecte os demais peers:

```bash
bitcoin-cli -datadir="." addnode 127.0.0.1:28542 onetry
bitcoin-cli -datadir="." addnode 127.0.0.1:28643 onetry
bitcoin-cli -datadir="." addnode 127.0.0.1:28744 onetry
```

Ainda no **Node A**, confirme as conexões:

```bash
bitcoin-cli -datadir="." getpeerinfo
[
  {
    "id": 0,
    "addr": "127.0.0.1:28542",...  
  },
  {
    "id": 1,
    "addr": "127.0.0.1:28643",...
  },
  {
    "id": 2,
    "addr": "127.0.0.1:28744",...
  }
]

```

**Passo 2 — Gerando moedas**

No **Node A**, crie uma carteira e um endereço:

```bash
bitcoin-cli -datadir="." createwallet CarteiraA

bitcoin-cli -datadir="." getnewaddress
bcrt1q8haacpalx68njrff0znzj35m0u6r73n3qv62dl
```

Gere 101 blocos:

```bash
bitcoin-cli -datadir="." generatetoaddress 101 bcrt1q8haacpalx68njrff0znzj35m0u6r73n3qv62dl
```

Agora o Node A possui moedas maduras para gastar.

**Passo 3 — Criando uma transação**

Ainda no **Node A**, gere um endereço de destino:

```bash
bitcoin-cli -datadir="." getnewaddress
bcrt1qn84ejc5cfzg2qfx8rmtv6p74expjlaem4apreg
```

Em seguida:

```bash
bitcoin-cli -datadir="." sendtoaddress bcrt1qn84ejc5cfzg2qfx8rmtv6p74expjlaem4apreg 1
8ee1b4dd410a94be754cef5ba796defb15cc952b710fbea25a10b6d6b94f2802
```

A transação será inserida na mempool e anunciada aos peers conectados.

**Passo 4 — Verificando a propagação**

No **Node A**:

```bash
bitcoin-cli -datadir="." getrawmempool
[
  "8ee1b4dd410a94be754cef5ba796defb15cc952b710fbea25a10b6d6b94f2802"
]
```

No **Node B**:

```bash
bitcoin-cli -datadir="." getrawmempool
[
  "8ee1b4dd410a94be754cef5ba796defb15cc952b710fbea25a10b6d6b94f2802"
]
```

No **Node C**:

```bash
bitcoin-cli -datadir="." getrawmempool
[
  "8ee1b4dd410a94be754cef5ba796defb15cc952b710fbea25a10b6d6b94f2802"
]
```

No **Node D**:

```bash
bitcoin-cli -datadir="." getrawmempool
[
  "8ee1b4dd410a94be754cef5ba796defb15cc952b710fbea25a10b6d6b94f2802"
]
```

Após alguns instantes, o mesmo txid deverá aparecer nos quatro nodes. Essa é justamente a propagação tradicional da rede Bitcoin.

**Passo 5 — Observando o tráfego**

No **Node A**:

```bash
bitcoin-cli -datadir="." getpeerinfo
```

O Node A está conectado a três peers. Após criar uma transação, o `getpeerinfo` mostrou estatísticas de tráfego para cada conexão.

Em cada peer apareceu algo semelhante a:

```bash
"bytessent_per_msg": {
  "inv":122,
  "tx":246
},
"bytesrecv_per_msg": {
  "getdata":266
}
```

Esses três campos mostram exatamente o fluxo descrito anteriormente:

```
Node A → inv → peer
peer → getdata → Node A
Node A → tx → peer
```

No experimento, o Node A enviou mensagens `inv` para anunciar a nova transação, recebeu mensagens `getdata` dos peers que solicitaram o conteúdo e, em seguida, enviou a transação completa através de mensagens `tx`.

Como o Node A estava conectado a três peers, esse processo aconteceu em três conexões diferentes. Por isso os mesmos tipos de mensagem aparecem repetidos nas estatísticas de cada peer.

Esse é o ponto central do modelo atual: uma nova transação é anunciada individualmente aos peers conectados. O mecanismo é robusto, mas gera tráfego redundante quando muitos nodes acabam recebendo a mesma transação por caminhos diferentes.

**Passo 6 — Relacionando com o Erlay**

No experimento acima observamos apenas uma transação. Mas imagine uma situação mais próxima da rede real. Suponha que cada node possua uma mempool contendo:

```
100.000 transações
```

e que apenas:

```
3 transações
```

sejam diferentes entre eles.

Hoje a sincronização depende principalmente dos anúncios individuais das novas transações.

O Erlay utilizaria Minisketch para descobrir algo equivalente a:

```
Node B precisa de txA
Node C precisa de txB
Node D precisa de txC
```

Sem precisar comunicar informações sobre as outras 99.997 transações que todos já conhecem. Essa é a principal ideia por trás da proposta: quanto mais parecidas forem as mempools, maior será a economia de banda obtida pela reconciliação dos conjuntos.

### Experimentando o Minisketch na prática

Até agora vimos o conceito de Set Reconciliation de forma abstrata. Mas o Minisketch já é uma biblioteca real, desenvolvida por Pieter Wuille, que pode ser utilizada para comparar conjuntos e recuperar apenas suas diferenças.

O exemplo abaixo cria dois conjuntos com aproximadamente 100.000 elementos cada. O primeiro conjunto não possui o elemento `50000` e contém o elemento adicional `999999`. O segundo conjunto não possui o elemento `70000` e contém o elemento adicional `888888`.

O objetivo é descobrir apenas as diferenças entre os conjuntos.

```c
#include <stdio.h>
#include <stdint.h>
#include <sys/types.h>
#include <minisketch.h>

int main() {

    /* Esperamos recuperar no máximo 4 diferenças. */
    minisketch* sketch1 = minisketch_create(32, 0, 4);
    minisketch* sketch2 = minisketch_create(32, 0, 4);

    /* Simula dois conjuntos com 100.000 elementos. */
    for (uint64_t i = 1; i <= 100000; i++) {
        if (i != 50000) {
            minisketch_add_uint64(sketch1, i);
        }
        if (i != 70000) {
            minisketch_add_uint64(sketch2, i);
        }
    }

    /* Elementos exclusivos de cada conjunto. */
    minisketch_add_uint64(sketch1, 999999);
    minisketch_add_uint64(sketch2, 888888);

    /* Combina os sketches. Elementos comuns se cancelam. */
    minisketch_merge(sketch1, sketch2);

    uint64_t output[4];

    /* Recupera as diferenças. */
    ssize_t count = minisketch_decode(sketch1, 4, output);

    printf("Diferenças encontradas:\n");

    for (int i = 0; i < count; i++) {
        printf("%lu\n", output[i]);
    }

    minisketch_destroy(sketch1);
    minisketch_destroy(sketch2);

    return 0;
}
```

Ao executar o programa, o resultado é:

```
50000
70000
888888
999999
```

Nenhum dos 99.998 elementos compartilhados entre os conjuntos aparece na saída. Observe o que aconteceu. Os dois conjuntos continham 100.000 elementos cada, mas o algoritmo retornou apenas os quatro elementos que diferiam entre eles. Mais interessante ainda: o custo da reconciliação depende principalmente da quantidade de diferenças e não do tamanho total dos conjuntos.

Em outras palavras, recuperar quatro diferenças entre conjuntos com cem elementos ou entre conjuntos com cem mil elementos é essencialmente o mesmo tipo de problema para o Minisketch.

Essa é justamente a propriedade explorada pelo Erlay. Na rede Bitcoin, cada node possui uma mempool contendo dezenas ou centenas de milhares de transações. Como as mempools dos nodes honestos costumam ser muito parecidas, a quantidade de diferenças entre elas tende a ser pequena. Em vez de transmitir informações sobre todas as transações conhecidas, os nodes podem trocar sketches compactos e recuperar apenas aquilo que está faltando.

Na prática, ninguém sabe antecipadamente quantas diferenças existem entre duas mempools. Por isso, os sketches são criados com uma capacidade estimada. Caso a quantidade real de diferenças seja maior do que a capacidade escolhida, a decodificação falha e os nodes precisam utilizar um sketch maior ou outro mecanismo de sincronização.

Essa combinação entre sketches compactos e mempools quase idênticas é o que torna o Erlay uma proposta tão promissora para reduzir o tráfego da rede Bitcoin.

### Por que o Erlay importa?

O Erlay não aumenta o tamanho dos blocos. Não altera a mineração. Não muda o mecanismo de consenso. Ainda assim, seu impacto pode ser significativo.

Ao reduzir o custo da propagação de transações, torna-se mais barato manter muitas conexões simultâneas. Isso permite uma rede mais conectada, mais robusta e potencialmente mais descentralizada. Por esse motivo, muitos desenvolvedores consideram o Erlay uma das melhorias mais importantes já propostas para a camada P2P do Bitcoin.

Embora a ideia do Erlay exista há alguns anos, ela continua sendo tema de discussão entre os desenvolvedores do Bitcoin Core. Durante o encontro de desenvolvedores em Barcelona, uma das sessões foi justamente dedicada ao tema **"Erlay Redesign"**.

O foco atual não é mais provar que a ideia funciona, mas sim discutir detalhes de implementação, simplificação da arquitetura e integração com o protocolo P2P existente. Isso mostra que o assunto continua ativo e relevante para o futuro da rede Bitcoin.

---

Grande parte das discussões sobre escalabilidade do Bitcoin gira em torno de blocos, transações e soluções de segunda camada. O Erlay olha para um problema diferente: a eficiência da comunicação entre os nodes.

A proposta parte de uma observação simples: as mempools dos nodes honestos já são quase idênticas. Em vez de depender exclusivamente de anúncios individuais para sincronizá-las, os nodes podem comparar resumos compactos de seus conjuntos de transações e trocar apenas aquilo que realmente está faltando.

Se implementado, o Erlay poderá reduzir significativamente o tráfego da rede, permitindo que os nodes mantenham mais conexões e fortalecendo ainda mais a descentralização do Bitcoin.

por: Rafael Santos
