# O futuro das interfaces do Bitcoin Core: RPC, REST, ZMQ e IPC

Quando utilizamos um comando como:

```bash
bitcoin-cli getblockchaininfo
```

estamos interagindo com o Bitcoin Core através de uma de suas interfaces externas.

Embora o `bitcoin-cli` seja a forma mais conhecida de conversar com um node, ele está longe de ser a única. Ao longo dos anos, o Bitcoin Core acumulou diferentes mecanismos para que aplicações externas possam consultar informações, receber notificações e enviar comandos ao software.

Hoje existem interfaces como:

- JSON-RPC
- REST
- ZMQ
- notificações por shell (`blocknotify` e `walletnotify`)
- a nova IPC Interface

Durante o Bitcoin Core Dev Tech 2026, um dos painéis discutiu justamente o futuro dessas interfaces. A questão central era simples:

> O Bitcoin Core deve continuar mantendo todas essas formas diferentes de comunicação ou existe uma maneira mais simples e eficiente de fazer isso?
> 

Embora pareça um assunto interno do desenvolvimento, essa discussão afeta diretamente wallets, exploradores de blocos, indexadores, sistemas Lightning e praticamente qualquer aplicação que utilize um node Bitcoin.

### **Um node raramente trabalha sozinho**

Quando pensamos em um node Bitcoin, normalmente imaginamos apenas o processo `bitcoind` validando blocos e transações.

Na prática, porém, diversos softwares costumam funcionar ao seu redor:

- wallets
- exploradores de blocos
- indexadores
- sistemas Lightning
- processadores de pagamento
- ferramentas de monitoramento

Todos eles precisam acessar informações da blockchain, acompanhar eventos em tempo real ou solicitar operações ao node.

A pergunta é: como essas aplicações conversam com o Bitcoin Core? A resposta depende da interface utilizada.

### **JSON-RPC: a interface principal do Bitcoin Core**

A interface mais importante do Bitcoin Core atualmente é o JSON-RPC. Praticamente tudo que fazemos através do `bitcoin-cli` utiliza RPC internamente.

Por exemplo:

```bash
bitcoin-cli getblockcount
```

```bash
bitcoin-cli getmempoolinfo
```

```bash
bitcoin-cli getblockchaininfo
```

Esses comandos são, na verdade, chamadas RPC enviadas ao node.

O JSON-RPC acabou se tornando a interface canônica do Bitcoin Core porque oferece acesso a praticamente todas as funcionalidades disponíveis.

Sua documentação é extensa e grande parte do ecossistema já foi construída sobre ela.

Por outro lado, existe um custo. Toda comunicação precisa ser convertida para JSON, transmitida, processada e convertida novamente pelo outro lado.

Para seres humanos, JSON é extremamente conveniente. Para aplicações que fazem milhares de consultas por segundo, esse processo gera uma sobrecarga considerável.

### **REST: um atalho para acessar dados**

Outra interface disponível é a REST API. Ela surgiu originalmente para oferecer uma alternativa mais simples ao RPC em determinados cenários e também para permitir acesso a dados já serializados.

Por exemplo:

```bash
curl http://127.0.0.1:8332/rest/chaininfo.json
```

Também é possível solicitar blocos e transações em formatos binários ou hexadecimal.

A principal vantagem é evitar parte do trabalho de serialização realizado pelo RPC e permitir consultas mais diretas para alguns tipos específicos de dados.

O problema é que isso acaba criando duplicação. Diversas funcionalidades já existem no RPC e precisam ser mantidas novamente na interface REST. Essa duplicação foi um dos pontos levantados durante a discussão.

### **ZMQ: quando o node envia informações sozinho**

Tanto RPC quanto REST funcionam através de consultas. A aplicação pergunta. O node responde.

Mas nem sempre esse modelo é o mais eficiente. Imagine um software Lightning que precisa descobrir imediatamente quando uma nova transação chega à mempool ou quando um novo bloco é encontrado.

Ficar consultando o node continuamente seria ineficiente. Para resolver esse problema existe a interface ZMQ. Ela permite que o próprio Bitcoin Core publique notificações em tempo real.

Uma configuração típica pode incluir:

```bash
zmqpubrawblock=tcp://127.0.0.1:28332
zmqpubrawtx=tcp://127.0.0.1:28333
```

Sempre que um novo bloco ou transação aparecer, uma mensagem é enviada automaticamente para os clientes conectados.

Atualmente essa interface é amplamente utilizada por projetos como LND, Eclair e mempool.space.

Entretanto, existe uma característica importante: o ZMQ é considerado uma interface *best effort*. Isso significa que o Bitcoin Core tenta entregar as notificações, mas não oferece garantias absolutas de que nenhuma mensagem será perdida. Apesar disso, o modelo tem funcionado bem para muitos casos de uso.

### As notificações por shell

Existe ainda um mecanismo mais antigo e menos conhecido. O Bitcoin Core pode executar programas externos sempre que determinados eventos acontecem.

Por exemplo:

```bash
blocknotify=/home/user/script.sh %s
```

Nesse caso, sempre que um novo bloco for conectado à blockchain, o script será executado.

Também existe:

```bash
walletnotify=/home/user/script.sh %s
```

que dispara eventos relacionados à carteira.

Essas interfaces são extremamente simples. Embora sejam antigas, continuam sendo utilizadas porque resolvem determinados problemas com pouca complexidade.

Durante a discussão, alguns desenvolvedores comentaram que removê-las obrigaria muitos usuários a manter processos executando continuamente, algo que atualmente não é necessário.

### A chegada da IPC Interface

A grande novidade da discussão foi a IPC Interface. IPC significa *Inter Process Communication*, ou comunicação entre processos.

Para entender a ideia, imagine que o Bitcoin Core está rodando como um programa separado no computador. Do outro lado, temos uma aplicação externa: uma wallet, um indexador, um software Lightning ou qualquer outro sistema que precise conversar com o node.

Com RPC ou REST, essa comunicação passa por uma camada textual. A aplicação monta uma requisição em JSON/HTTP, envia ao Bitcoin Core, o Core interpreta essa mensagem, executa a operação e depois devolve uma resposta também serializada em algum formato externo.

De forma simplificada:

```
Aplicação -> JSON-RPC ou REST -> Bitcoin Core -> JSON-RPC ou REST -> Aplicação
```

A IPC tenta seguir outro caminho. Em vez de tratar tudo como uma chamada textual, ela permite que outro processo converse com o Bitcoin Core usando interfaces mais próximas das estruturas internas do próprio software.

No caso do Bitcoin Core, esse trabalho utiliza Cap’n Proto, uma tecnologia de serialização e chamada remota de métodos. A ideia é definir interfaces que possam ser chamadas por outro processo, como se a aplicação externa estivesse invocando métodos oferecidos pelo próprio Core.

De forma simplificada, seria algo como:

```
Aplicação -> IPC -> Interface interna -> Bitcoin Core
```

Isso não significa que a aplicação externa passa a “entrar” no Bitcoin Core ou acessar livremente qualquer parte do código. A proposta é justamente expor interfaces bem definidas, com métodos específicos, para que outros programas possam interagir com o node de forma mais eficiente e controlada.

Um exemplo conceitual seria uma aplicação pedir informações da chain, receber notificações sobre novos blocos ou consultar dados necessários para um indexador externo. Em vez de cada interface implementar sua própria lógica, essas chamadas poderiam passar por uma camada comum, reutilizada por RPC, REST ou IPC.

A principal vantagem é reduzir sobrecarga e duplicação. Como a comunicação não depende do mesmo modelo textual do JSON-RPC, ela pode ser mais eficiente para certos casos de uso. Além disso, ao aproximar as interfaces externas das classes internas em `src/interfaces/`, o Bitcoin Core pode concentrar a lógica principal em um único lugar e evitar que a mesma funcionalidade precise ser reimplementada várias vezes.

Mas a IPC também traz novos desafios. Ela exige bibliotecas específicas, como Cap’n Proto, não é tão simples de testar com ferramentas universais como `curl` ou `jq`, e seu uso pode ser mais complexo para desenvolvedores que querem apenas fazer uma chamada simples ao node.

Por isso, a IPC não deve ser vista como uma substituição imediata do RPC. Inclusive, uma das conclusões da discussão foi que a IPC provavelmente não substituirá todas as demais interfaces. A tendência parece ser utilizá-la como uma camada comum de integração, sobre a qual RPC, REST e futuras interfaces possam ser construídas. Dessa forma, a lógica principal ficaria concentrada em um único lugar, reduzindo duplicação de código e facilitando a manutenção do Bitcoin Core.

### O problema da duplicação

Grande parte da motivação para a IPC está relacionada à arquitetura atual. Hoje, uma mesma funcionalidade frequentemente precisa ser implementada em mais de uma interface.

Em muitos casos, também é necessário manter documentação separada para cada uma delas. Isso aumenta a complexidade do código e dificulta a evolução do software.

A visão discutida durante o evento é mover cada vez mais a lógica de negócio para uma camada comum, utilizada por todas as interfaces.

De forma simplificada, hoje temos algo parecido com:

```
RPC  -> lógica própria
REST -> lógica própria
ZMQ  -> lógica própria
```

Enquanto a direção desejada seria algo mais próxima de:

```
RPC  \
REST  \
IPC    -> interfaces internas -> Bitcoin Core
ZMQ   /
```

Nesse modelo, as diferentes interfaces se tornam apenas formas alternativas de acessar a mesma lógica central.

### A IPC pode substituir o ZMQ?

Uma das perguntas levantadas foi justamente essa. Já existe um trabalho em andamento chamado **IPC Chain Interface**, que fornece notificações semelhantes às atualmente oferecidas pelo ZMQ.

Porém ainda existem diferenças importantes. Hoje o IPC utiliza Unix Sockets, enquanto o ZMQ normalmente opera sobre TCP. Isso significa que aplicações remotas não conseguem utilizá-lo da mesma forma.

Além disso, nem todas as funcionalidades necessárias para substituir completamente o ZMQ já estão disponíveis. Por esse motivo, não existe qualquer plano imediato de remoção da interface.

### E se uma interface for removida no futuro?

Uma das possibilidades discutidas foi a utilização de um *shim*. Um shim é um pequeno software intermediário que traduz uma interface para outra.

Por exemplo:

```
Bitcoin Core -> IPC -> Shim -> ZMQ -> Aplicação
```

Nesse cenário, aplicações antigas continuariam recebendo notificações ZMQ sem que o Bitcoin Core precisasse manter essa funcionalidade internamente.

A ideia ainda é apenas conceitual, mas mostra uma preocupação constante dos desenvolvedores com compatibilidade e transições graduais.

### O desafio de evoluir sem quebrar o ecossistema

Apesar das discussões sobre simplificação, existe um consenso claro: qualquer mudança precisa respeitar o enorme ecossistema já construído ao redor do Bitcoin Core.

JSON-RPC é amplamente utilizado. REST possui usuários importantes. ZMQ é fundamental para diversos projetos Lightning. As notificações por shell continuam sendo úteis em muitos ambientes.

Por isso, o objetivo não parece ser remover interfaces rapidamente, mas sim encontrar formas de reduzir duplicação, simplificar a arquitetura interna e facilitar a manutenção do software a longo prazo.

---

Quando pensamos no Bitcoin Core, normalmente focamos em consenso, validação de blocos, mineração ou novas funcionalidades do protocolo.

Mas existe outra camada igualmente importante: a forma como aplicações externas interagem com o node. Wallets, exploradores, indexadores, sistemas Lightning e inúmeras outras ferramentas dependem dessas interfaces diariamente.

A discussão realizada durante o Bitcoin Core Dev Tech 2026 mostrou que os desenvolvedores estão buscando maneiras de tornar essa arquitetura mais simples, eficiente e sustentável para o futuro.

A nova IPC Interface surge como uma das candidatas a desempenhar um papel central nessa evolução. Ainda existem desafios técnicos e questões de compatibilidade a resolver, mas a direção geral parece clara: reduzir a complexidade interna sem comprometer a estabilidade que tornou o Bitcoin Core a principal implementação do protocolo Bitcoin.


Escrito por:  

Rafael Santos


[Instagram (@area.bitcoin)](https://www.instagram.com/area.bitcoin/)

[Area Bitcoin](https://www.youtube.com/c/AreaBitcoin)
