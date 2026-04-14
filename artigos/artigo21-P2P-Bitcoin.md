# P2P Bitcoin: como nodes conversam

O Bitcoin não funciona como uma aplicação cliente–servidor tradicional.

Não existe:

- servidor central,
- API global,
- endpoint oficial,
- nó mestre,
- nem “backend do Bitcoin”.

O que existe é uma **rede peer-to-peer (P2P)** formada por milhares de nodes independentes, que se conectam diretamente uns aos outros via **TCP**, trocando mensagens seguindo um protocolo bem definido.

Cada node Bitcoin é, ao mesmo tempo:

- **cliente** (quando solicita dados),
- **servidor** (quando responde pedidos),
- **validador** (quando verifica blocos e transações),
- **retransmissor** (quando propaga informações pela rede).

Essa simetria é fundamental: **não há hierarquia na rede Bitcoin**.

---

**RPC não é rede**

Antes de avançar, é importante eliminar uma confusão comum.

O `bitcoin-cli` usa **RPC (Remote Procedure Call)**, mas isso **não é o protocolo da rede Bitcoin**.

O RPC serve para:

- administrar o node local,
- consultar estado interno,
- enviar comandos,
- construir transações,
- inspecionar blocos, UTXOs e mempool.

Ele funciona **apenas entre você e o seu node**.

Quando você executa:

```bash
bitcoin-cli sendrawtransaction
```

Você **não está enviando a transação para a rede**.

Você está dizendo ao seu node:

> “Inclua essa transação no seu mempool e cuide da propagação.”
> 

A partir daí, **quem conversa com a rede é o próprio node**, usando o protocolo P2P, não o RPC.

---

**O que realmente trafega na rede Bitcoin**

Na rede P2P do Bitcoin trafegam apenas **mensagens de protocolo**, como:

- `version`
- `verack`
- `inv`
- `getdata`
- `tx`
- `block`
- `headers`
- `ping`
- `pong`

Essas mensagens são:

- binárias,
- estruturadas,
- transmitidas diretamente via TCP,
- independentes de qualquer interface RPC.

Ou seja:

> nodes não “chamam funções” uns dos outros, eles trocam mensagens.
> 

---

**Topologia da rede: um grafo dinâmico**

A rede Bitcoin não é uma malha totalmente conectada.

Cada node mantém apenas um **conjunto limitado de conexões**, tipicamente:

- algumas conexões **outbound** (iniciadas por ele),
- possivelmente conexões **inbound** (aceitas de outros peers).

O conjunto de peers muda o tempo todo:

- nodes entram,
- nodes saem,
- conexões caem,
- novas conexões são abertas.

O resultado é um **grafo dinâmico**, constantemente se reorganizando.

Mesmo assim, graças à propagação por *gossip*, informações importantes (transações e blocos) **se espalham rapidamente por toda a rede**.

---

**Propagação por anúncio, não por envio direto**

Um ponto central do modelo P2P do Bitcoin é que:

> nodes não empurram dados grandes automaticamente.
> 

Eles seguem um processo em etapas:

1. **anunciam que têm algo** (`inv`)
2. aguardam interesse do peer
3. **só então enviam o dado completo** (`tx` ou `block`)

Isso traz várias vantagens:

- economia de banda,
- resistência a spam,
- melhor controle de fluxo,
- escalabilidade da rede.

Esse padrão vai aparecer repetidamente quando analisarmos as mensagens P2P.

---

**Confiança zero, verificação total**

Talvez o aspecto mais importante do modelo P2P do Bitcoin seja este:

> nodes não confiam uns nos outros.
> 

Mesmo após estabelecer uma conexão P2P:

- blocos são verificados integralmente,
- transações passam por todas as regras de consenso,
- scripts são executados,
- UTXOs são checados,
- Proof of Work é validada.

Um peer pode:

- anunciar um bloco inválido,
- propagar uma transação inválida,
- mentir sobre sua altura,
- se comportar mal.

E o node simplesmente:

- rejeita os dados,
- penaliza o peer,
- e segue conversando com outros.

Essa desconfiança estrutural é o que permite que a rede funcione **sem coordenação central**.

---

### Estabelecendo conexões P2P entre nodes

Agora que entendemos o **modelo P2P do Bitcoin**, vamos observar **como uma conexão entre dois nodes realmente acontece** na prática.

Quando um node Bitcoin Core inicia, ele precisa descobrir peers para se conectar. Isso pode acontecer de várias formas:

- **DNS seeds** (nomes DNS que retornam IPs de nodes públicos),
- **endereços conhecidos** armazenados localmente (`peers.dat`),
- **endereços recebidos de outros peers** (mensagens `addr`),
- **configuração manual** via linha de comando ou `bitcoin.conf`.

Uma vez que o node conhece possíveis peers, ele tenta estabelecer conexões TCP com alguns deles.

Por padrão, um node mantém:

- conexões **outbound** (iniciadas por ele),
- e pode aceitar conexões **inbound** (iniciadas por outros nodes).

---

**Adicionando um peer manualmente (`addnode`)**

Primeiro vamos iniciar 2 nós em regtest em portas diferentes. Seguem as configurações do arquivo bitcoin.conf de cada um:

```bash
#bitcoin.conf 1
regtest=1
server=1
fallbackfee=0.0001

[regtest]
port=18444

rpcbind=127.0.0.1
rpcallowip=127.0.0.1
rpcport=18443

rpcuser=teste
rpcpassword=teste
```

```bash
#bitcoin.conf 2
regtest=1
server=1
fallbackfee=0.0001

[regtest]
port=28445

rpcbind=127.0.0.1
rpcallowip=127.0.0.1
rpcport=28448

rpcuser=teste
rpcpassword=teste

```

Agora, podemos instruir o node a se conectar explicitamente a outro peer usando o comando addnode. 

```bash
bitcoin-cli -datadir="." addnode"<ip>:<porta>" add
```

Exemplo (regtest no nó 1):

```bash
bitcoin-cli -datadir="." addnode 127.0.0.1:28445 add
```

Esse comando:

- abre uma conexão TCP com o peer indicado,
- inicia o handshake P2P,
- mantém a conexão ativa enquanto ambos os lados aceitarem.

⚠️ Importante:

`addnode` **não envia transações nem blocos**.

Ele apenas **cria a conexão**. O tráfego real depende das mensagens P2P trocadas depois.

---

**Observando peers conectados (`getpeerinfo`)**

Depois que a conexão é estabelecida, podemos inspecionar os peers ativos:

```bash
bitcoin-cli -datadir="." getpeerinfo
```

A saída é uma lista de peers conectados:

```bash
[
  {
    "id": 0,
    "addr": "127.0.0.1:28445",
    "addrbind": "127.0.0.1:58898",
    "network": "not_publicly_routable",
    "services": "0000000000000c09",
    "servicesnames": [
      "NETWORK",
      "WITNESS",
      "NETWORK_LIMITED",
      "P2P_V2"
    ],
    "relaytxes": true,
    "lastsend": 1765914232,
    "lastrecv": 1765914232,
    "last_transaction": 0,
    "last_block": 0,
    "bytessent": 561085,
    "bytesrecv": 90913,
    "conntime": 1765914231,
    "timeoffset": 0,
    "pingtime": 0.000482,
    "minping": 0.000482,
    "version": 70016,
    "subver": "/Satoshi:29.0.0/",
    "inbound": false,
    "bip152_hb_to": false,
    "bip152_hb_from": true,
    "startingheight": 0,
    "presynced_headers": -1,
    "synced_headers": -1,
    "synced_blocks": -1,
    "inflight": [
    ],
    "addr_relay_enabled": true,
    "addr_processed": 0,
    "addr_rate_limited": 0,
    "permissions": [
    ],
    "minfeefilter": 0.00001000,
    "bytessent_per_msg": {
      "addrv2": 49,
      "block": 434084,
      "feefilter": 29,
      "getaddr": 33,
      "getheaders": 762,
      "headers": 125574,
      "ping": 29,
      "pong": 29,
      "sendaddrv2": 33,
      "sendcmpct": 30,
      "verack": 33,
      "version": 135,
      "wtxidrelay": 33
    },
    "bytesrecv_per_msg": {
      "feefilter": 58,
      "getdata": 89570,
      "getheaders": 90,
      "headers": 22,
      "ping": 29,
      "pong": 29,
      "sendaddrv2": 33,
      "sendcmpct": 60,
      "sendheaders": 33,
      "verack": 33,
      "version": 135,
      "wtxidrelay": 33
    },
    "connection_type": "manual",
    "transport_protocol_type": "v2",
    "session_id": "0d72d07379c39090174714fcdcd25875ac58e02ec1443c4f864302aeba392d43"
  }
]
```

Campos importantes para entender a conexão:

- `addr` — endereço do peer
- `connection_type` — inbound ou outbound
- `services` — capacidades anunciadas pelo peer
- `version` — versão do protocolo P2P
- `subver` — software do peer
- `startingheight` — altura anunciada no handshake
- `synced_blocks` / `synced_headers` — estado de sincronização
- `pingtime` — latência medida

Esse comando é essencial para **debugar comportamento de rede**.

---

**O handshake P2P: `version` e `verack`**

Toda conexão P2P no Bitcoin começa com um **handshake obrigatório**, composto por duas mensagens principais:

1. `version`
2. `verack`

O fluxo básico é:

```
NodeA → version → NodeB
NodeB → version → NodeA
NodeA → verack → NodeB
NodeB → verack → NodeA
```

A mensagem `version` anuncia:

- versão do protocolo,
- serviços suportados,
- altura atual da blockchain,
- nonce aleatório (para evitar conexões consigo mesmo),
- identificador do software (`subver`).

Somente **após a troca de `verack`** os nodes passam a:

- anunciar inventário (`inv`),
- solicitar dados (`getdata`),
- trocar transações e blocos.

Se o handshake falhar, a conexão é encerrada.

---

**Verificando conectividade e latência (`ping`)**

Depois que o peer está conectado, podemos medir a latência usando:

```bash
bitcoin-cli -datadir="." ping
```

Esse comando:

- envia mensagens `ping` para todos os peers,
- aguarda os respectivos `pong`,
- atualiza os campos `pingtime` e `minping` em `getpeerinfo`.

O `ping` **não é ICMP** (como o `ping` do sistema operacional).

Ele é uma **mensagem do protocolo Bitcoin P2P**.

---

### Propagação de dados na rede Bitcoin

Conectar nodes é apenas o primeiro passo. O que realmente faz o Bitcoin funcionar como uma rede descentralizada é **como dados se propagam entre esses peers**.

Esses dados são, essencialmente:

- **transações** (gastos ainda não confirmados),
- **blocos** (novos estados da blockchain).

Mas eles **não são enviados de forma automática ou indiscriminada**.

A rede Bitcoin segue um modelo explícito e controlado de propagação, baseado em anúncios e solicitações.

---

**Por que nodes não enviam dados automaticamente?**

Um erro comum é imaginar que, ao surgir uma nova transação ou bloco, o node simplesmente “empurra” esse dado para todos os peers conectados.

Isso **não acontece**.

O Bitcoin evita esse comportamento por vários motivos:

- **economia de banda** — blocos e transações podem ser grandes;
- **proteção contra spam** — peers maliciosos não conseguem forçar envio de dados;
- **controle de fluxo** — cada node decide o que quer receber;
- **escalabilidade** — a rede cresce sem explodir tráfego.

O modelo adotado é:

> anunciar primeiro, enviar depois, e só se o peer pedir.
> 

Esse padrão aparece em praticamente toda a comunicação P2P do Bitcoin.

---

**A mensagem `inv`: “eu tenho isso”**

Quando um node aprende sobre uma nova transação ou um novo bloco válido, ele **não envia o dado completo**. Em vez disso, ele envia uma mensagem `inv` (*inventory*), que contém apenas:

- o **tipo do objeto** (transação ou bloco),
- o **hash do objeto** (`txid` ou `blockhash`).

Exemplo conceitual:

```
NodeA → inv(txid) → NodeB
NodeA → inv(blockhash) → NodeB
```

Ou seja, o node está dizendo:

> “Eu tenho esse objeto. Você se interessa?”
> 

A mensagem `inv` **não carrega dados pesados**, apenas identificadores.

---

**A mensagem `getdata`: “me manda”**

Ao receber um `inv`, o peer decide se quer ou não aquele objeto.

Se quiser, ele responde com uma mensagem `getdata`, solicitando explicitamente o conteúdo completo:

```
NodeB → getdata(txid) → NodeA
```

Esse passo é crucial:

- o peer **tem controle total** sobre o que recebe;
- objetos já conhecidos são ignorados;
- evita retransmissões desnecessárias.

Só após esse pedido explícito o envio real acontece.

---

**As mensagens `tx` e `block`: envio do dado completo**

Quando um node recebe um `getdata`, ele então envia o objeto solicitado:

- `tx` → para transações
- `block` → para blocos

Exemplo:

```
NodeA → tx → NodeB
NodeA → block → NodeB
```

Ao receber esses dados, o node **não confia automaticamente**. Ele executa uma série de verificações locais:

- validação estrutural,
- verificação de regras de consenso,
- execução de scripts,
- checagem de UTXOs,
- validação da Proof of Work (no caso de blocos).

Somente se **todas as verificações passarem** o dado é aceito.

---

**Propagação em cascata (gossip)**

Uma vez aceito, o processo se repete:

1. o node adiciona a transação ao mempool **ou** o bloco à chain;
2. ele anuncia esse novo objeto aos seus peers com `inv`;
3. cada peer decide se quer solicitar o dado;
4. o objeto se espalha pela rede.

Esse mecanismo cria um efeito de **propagação em cascata**, conhecido como *gossip protocol*.

Importante notar:

- não existe “broadcast global”;
- não existe ordem garantida;
- não existe sincronização central.

Mesmo assim, a rede converge rapidamente para um estado comum.

---

**Blocos concorrentes, latência e forks temporários**

Como a propagação não é instantânea, é perfeitamente possível que:

- dois mineradores encontrem blocos diferentes quase ao mesmo tempo;
- partes da rede vejam blocos distintos primeiro.

Nesse cenário:

- ambos os blocos são válidos,
- ambos são propagados via `inv` / `getdata` / `block`,
- a rede fica temporariamente dividida.

Esse é o ponto onde surgem:

- **forks temporários**,
- **blocos órfãos**,
- **reorganizações de cadeia (reorgs)**.

Nada disso é erro, é **comportamento esperado** em uma rede distribuída.

---

**O papel da propagação na segurança do Bitcoin**

A forma como dados se propagam impacta diretamente:

- segurança,
- descentralização,
- resistência a ataques,
- tempo de confirmação percebido.

Mineração, consenso e validação **dependem diretamente** desse fluxo P2P.

É por isso que entender `inv`, `getdata`, `tx` e `block` não é opcional para quem desenvolve sobre Bitcoin, é fundamental.

### Observando o P2P de verdade (tcpdump)

Até aqui, usamos apenas o `bitcoin-cli`. Agora, vamos **olhar o Bitcoin no fio**. Quando um node se conecta a outro, a conversa acontece **via TCP**, usando o **protocolo P2P do Bitcoin**.

**Capturando o handshake**

Em regtest, com P2P v1 habilitado (usar no bitcoin.conf `v2transport=0`), execute:

```bash
sudo tcpdump -l -i lo -A -s 0 port 28445 | egrep -a "version|verack"
```

---

**Observação**:

Por padrão, versões recentes do Bitcoin Core utilizam **P2P v2 (BIP324)**, que **criptografa e ofusca o tráfego de rede** logo após o estabelecimento da conexão TCP.

Nesse modo, as mensagens `version`, `verack`, `inv`, etc.:

- **não aparecem em texto claro**,
- não podem ser identificadas com `tcpdump -A`,
- exigem ferramentas ou instrumentação específica para decodificação.

Ao definir no `bitcoin.conf v2transport=0`, forçamos o uso do **P2P v1 (legado)**, onde:

- as mensagens trafegam **sem criptografia**,
- o conteúdo pode ser inspecionado diretamente,
- o handshake `version` / `verack` torna-se visível no `tcpdump`.

👉 Isso **não é recomendado para produção**, mas é **ideal para fins educacionais**, pois permite observar claramente como o protocolo P2P do Bitcoin funciona no nível de bytes.

---

Ao fazer uma conexão com:

```bash
bitcoin-cli -datadir="." addnode 127.0.0.1:28445 add
```

Você verá algo como:

```
...version ... /Satoshi:29.0.0/ ...
...version ... /Satoshi:29.0.0/ ...
...verack ...
...verack ...
```

**O que está acontecendo aqui**

Esse é o **handshake P2P do Bitcoin**, em tempo real:

1. **version**
    
    Cada node anuncia:
    
    - versão do protocolo,
    - serviços suportados,
    - altura da blockchain,
    - user agent (`/Satoshi:29.0.0/`).
2. **version (resposta)**
    
    O peer responde com sua própria mensagem `version`.
    
3. **verack**
    
    Cada lado confirma:
    
    *“Recebi sua version e aceito falar esse protocolo.”*
    
4. **Conexão estabelecida**
    
    A partir daqui, os nodes podem trocar:
    
    - `inv`,
    - `getdata`,
    - `tx`,
    - `block`,
    - `headers`.

Ver o `version` e o `verack` no `tcpdump` expande a forma como você entende o Bitcoin:

- você percebe que nodes **não confiam** uns nos outros,
- tudo começa com negociação explícita,
- o protocolo é simples, binário e direto,
- é assim que milhares de nodes se coordenam sem autoridade central.

---

Entender o P2P do Bitcoin é entender **o Bitcoin de verdade**. Não existe API global, servidor central ou backend escondido, existem apenas nodes independentes, trocando mensagens simples, explícitas e verificáveis. Quando observamos um `version`, um `verack`, um `inv` ou um `block` passando no fio, fica claro que o Bitcoin não depende de confiança, coordenação central ou permissões: ele depende de **protocolo, validação e consenso local**. A partir daqui, mineração, mempool, consenso, reorgs e até a Lightning Network deixam de ser abstrações e passam a ser consequências diretas desse modelo P2P elegante, resiliente e profundamente descentralizado.

Escrito por: Rafael Santos

