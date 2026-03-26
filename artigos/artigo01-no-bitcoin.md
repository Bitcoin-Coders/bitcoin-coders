# Nó Bitcoin com Bitcoin Core: instalação, bitcoind e bitcoin-cli (primeiros passos)

por Rafael Santos

Esse é o primeiro de uma série de artigos que começo a escrever sobre o Bitcoin, do ponto de vista técnico.  Um importante detalhe que precisamos lembrar é que o Bitcoin é um protocolo, ou seja, um conjunto de regras a serem seguidas. Essas regras são seguidas por diversos entes que se comunicam e formam uma rede.

Cada um desses entes que faz parte dessa rede pode ser visto como um Nó. Em resumo, um Nó é um **software rodando em um dispositivo eletrônico** (computador, por exemplo), que tem como função principal **fazer cumprir as regras do protocolo Bitcoin**.

O Nó pode atuar de diversas maneiras:

- Recebendo blocos e transações;
- Validando bloco e transações de forma independente;
- Repassando e transmitindo blocos e transações para outros Nós;
- Mantendo uma cópia da blockchain;
- Minerando;
- Oferecendo APIs para desenvolvedores, aplicativos e serviços.

Podemos classificar os Nós em 3 tipos (embora outras classificações possam ser feitas):

**🟢 Full Node (Nó Completo)**

- Baixa **toda a blockchain** e **valida todas as regras** do Bitcoin (como tamanhos de bloco, regras de assinatura, número de satoshis, etc).
- Usa a versão completa do protocolo.
- Autonomia total: não confia em terceiros.
- Contribui com a rede ao retransmitir transações e blocos.

**🟡 Light Node (SPV - Simplified Payment Verification)**

- Não baixa toda a blockchain, apenas os **headers dos blocos**.
- Verifica as transações via **prova de inclusão** (Merkle Tree).
- Usa um full node como intermediário para acessar dados.
- Mais leve, ideal para dispositivos móveis.
- **Menor privacidade e confiança**.

**🔵 Miner Node (Nó Minerador)**

- É um full node com software adicional de mineração.
- Valida blocos e tenta encontrar um hash que satisfaça a dificuldade atual (prova de trabalho).
- Propaga blocos encontrados para a rede.

# Instalação e configuração

Bitcoin Core

Qualquer software que implemente as regras do protocolo, pode fazer parte da rede Bitcoin. O Bitcoin Core é o software mais antigo e visto como maior referência, já que foi criado em 2009 por Satoshi Nakamoto. Desde então passou por diversas atualizações, feitas por muitos programadores que se juntaram a equipe de desenvolvimento. O processo de desenvolvimento, por ser um sistema realmente descentralizado, é muito particular, no entanto, foge do escopo desse artigo.

A instalação e a configuração do Bitcoin Core é simples. Para os exemplos deste artigo estarei usando o Sistema Operacional Ubuntu 22.04.5 LTS. A seguir um passo-a-passo:

```bash
**#Baixe e instale o Bitcoin Core**
https://bitcoincore.org/en/download/
https://bitcoincore.org/bin/bitcoin-core-29.0/bitcoin-29.0-x86_64-linux-gnu.tar.gz

**#Extraia e mova para /opt:**
tar -xvf bitcoin-29.0-x86_64-linux-gnu.tar.gz
sudo mv bitcoin-29.0 /opt/bitcoin

**#Adicione o executável ao PATH (opcional):**
gedit ~/.bashrc
**#Colocar no final do arquivo:**
export PATH="/opt/bitcoin/bitcoin-29.0/bin:$PATH"
**#Atualizar:**
source ~/.bashrc

**#Verifique a instalação:**
bitcoind --version
bitcoin-cli --version
```

Perceba que verificamos a instalação de 2 softwares: **bitcoind** e **bitcoin-cli**. Eles fazem parte do Bitcoin Core e tem funções diferentes.

- **bitcoind** é o serviço principal, chamado de daemon. É quem de fato põe o Nó em execução. Fica rodando normalmente em background, validando transações e blocos, mantendo a blockchain, repassando os dados, etc.
- **bitcoin-cli** é o cliente de linha de comando. Serve para se comunicar com o bitcoind através de comandos via RPC (Remote Procedure Call). Alguns comandos possíveis: consultar saldo, enviar bitcoin, criar transações, etc.

O **bitcoin.conf** é o principal arquivo de configuração do Bitcoin Core. Nele, podemos definir opções importantes como o modo de rede (mainnet, testnet ou regtest), usuário e senha para comunicação RPC, permissões de acesso, taxas, entre outros parâmetros. Abaixo podemos ver um exemplo:

```bash
**#bitcoin.conf**
regtest=1
rpcuser=usuario
rpcpassword=senha123
txindex=1
rpcallowip=127.0.0.1
fallbackfee=0.0001
```

Já podemos colocar o **bitcoind** a rodar:

```bash
**#Criar uma pasta para os dados do Nó**
mkdir -p /home/user/bitcoin-regtest-node1

**#Editar o arquivo de configuração do Nó**
gedit /home/user/bitcoin-regtest-node1/bitcoin.conf
regtest=1
rpcuser=teste
rpcpassword=teste
rpcallowip=127.0.0.1
fallbackfee=0.0001
[regtest]
rpcport=18443
port=18444

#**Iniciar o Nó**
bitcoind -datadir=/home/user/bitcoin-regtest-node1 -daemon

**#Para parar o Nó**
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 stop
```

# Rodando o                  bitcoind

Vamos entender algumas configurações feitas no arquivo **bitcoin.conf**. Podemos configurar em qual rede o Nó irá atuar.

**🌐 Modos de operação**

- **mainnet**: rede principal real (transações valem dinheiro).
- **testnet**: rede de teste pública.
- **signet:** rede de teste pública.
- **regtest**: rede de teste local, controlada pelo desenvolvedor (ideal para experimentação).

Para escolher, basta setar a variável corresponder à rede para 1. Em nossos testes geralmente utilizaremos a rede de teste local, que roda somente em nosso próprio computador (regtest=1).

📬 **Remote Procedure Call (RPC)**

O Bitcoin Core disponibiliza uma **API RPC** (Remote Procedure Call) que permite desenvolvedores interagirem com o Nó. Essa interface expõe comandos como consultar o saldo, enviar transações, gerar blocos (em regtest), verificar status da rede, entre outros. O RPC funciona por meio de requisições HTTP autenticadas e retorna respostas em formato JSON. Com isso, é possível integrar o Nó Bitcoin a scripts, sistemas web, carteiras, exploradores de bloco e diversas outras aplicações. Vamos entender as configurações no bitcoin.conf relacionadas a RPC.

- **rpcuser=teste**, define um nome de usuário para acessar as chamadas da API.
- **rpcpassword=teste**, define uma senha para acessar as chamadas da API.
- **rpcallowip=127.0.0.1**, permite acesso RPC somente para a máquina local.

Além dessas configurações, existe uma seção para as configurações do **modo regtest**.

- **[regtest]**, indica que abaixo virão configurações que serão utilizadas somente quando o Nó estiver rodando em modo regtest.
- **rpcport=18443**, define a porta que o bitcoind vai usar para aceitar conexões RPC.
- **port=18444**, define a porta de rede peer-to-peer (porta que o bitcoind irá se conectar a outros nós, receber conexões de outros nós, repassar blocos e transações válidas).

**Uma vez que o bitcoind esteja rodando, o Nó:**

- Começa a se **conectar** a outros Nós da rede (via protocolo P2P);
- Passa a **receber**, **verificar** e **propagar** transações e blocos;
- Mantém e atualiza uma cópia local da **blockchain** (se for um full node);
- Disponibiliza a **API RPC**, permitindo o uso de comandos através do **bitcoin-cli** ou outros clientes.

Podemos fazer uma serie de testes para entender essas atuações do Nó rodando.  Para isso utilizaremos o **bitcoin-cli**. Começamos com a blockchain:

```bash
bitcoin-cli -regtest -datadir=/home/user/bitcoin-regtest-node1 getblockchaininfo

{
  "chain": "regtest",
  "blocks": 0,
  "headers": 0,
  "bestblockhash": "0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206",
  "bits": "207fffff",
  "target": "7fffff0000000000000000000000000000000000000000000000000000000000",
  "difficulty": 4.656542373906925e-10,
  "time": 1296688602,
  "mediantime": 1296688602,
  "verificationprogress": 1,
  "initialblockdownload": true,
  "chainwork": "0000000000000000000000000000000000000000000000000000000000000002",
  "size_on_disk": 293,
  "pruned": false,
  "warnings": [
  ]
}
```

Vemos que o Nó já tem a estrutura da blockchain carregada, mesmo que ainda sem blocos (além do gênesis). Podemos ver também as conexões com outros Nós:

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 getpeerinfo

[ 
]
```

Nesse primeiro momento, só existe esse Nó criado, por isso não há conexões com outros Nós na rede. Podemos criar uma carteira associada ao Nó:

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 createwallet "NovaCarteira"

{
  "name": "NovaCarteira"
}
```

Criamos então um novo endereço para essa carteira:

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 -rpcwallet=NovaCarteira getnewaddress

bcrt1q5wa3jgkuqvut2rayz0kj77j7lzg5609rmhqw3a
```

Solicitamos a criação de um novo bloco (mineração na regtest) e podemos ver o Nó gerando e validando o bloco (utilize o seu endereço criado no comando acima):

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 generatetoaddress 1 bcrt1q5wa3jgkuqvut2rayz0kj77j7lzg5609rmhqw3a

[
"3a75f53d88efdf652fcbcd8ceec51413cca488163641fe5eba6e38a5ce937fc7"
]

bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 getblockcount

1
```

O comando **generatetoaddress** do exemplo, minera 1 bloco e envia a recompensa (50 BTCs) para o endereço indicado (o que criamos no exemplo anterior). Após vemos o comando **getblockcount** mostrando que a blockchain já possui 1 bloco. Podemos ver também as transações validadas e associadas ao Nó:

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 listtransactions

[
  {
    "address": "bcrt1q5wa3jgkuqvut2rayz0kj77j7lzg5609rmhqw3a",
    "parent_descs": [
      "wpkh(tpubD6NzVbkrYhZ4YiDDQ216BaJirHX5JYaKFTytSSDo9HL4jpc5y4iSRiKs4hYpugz669CCytpd3epKmgg169KfrfUGpgeA1WywNUqUpeuNwxj/84h/1h/0h/0/*)#sjlzentj"
    ],
    "category": "immature",
    "amount": 50.00000000,
    "label": "",
    "vout": 0,
    "abandoned": false,
    "confirmations": 1,
    "generated": true,
    "blockhash": "3a75f53d88efdf652fcbcd8ceec51413cca488163641fe5eba6e38a5ce937fc7",
    "blockheight": 1,
    "blockindex": 0,
    "blocktime": 1750012465,
    "txid": "1434fd00768a896b5bf3d2b6015b21cb20edff129512b82d1552775c6b88221b",
    "wtxid": "1ce6c144dc2641c84fcd99f4204b261317a28c6bb8a94c84e3afda1416246c06",
    "walletconflicts": [
    ],
    "mempoolconflicts": [
    ],
    "time": 1750012465,
    "timereceived": 1750012465,
    "bip125-replaceable": "no"
  }
]
```

Através desses testes podemos ver que, assim que o **bitcoind** é iniciado, o Nó já está funcional. Ele começa a validar blocos e transações, se conectar com outros Nós, etc. Além disso expõe a API RPC, e responde a comandos imediatamente. A seguir veremos alguns outros comandos do **bitcoin-cli**. Para listar todos comandos podemos utilizar:

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 help
```

⌨️ **bitcoin-cli (linha de comando)**

O **bitcoin-cli** envia comandos RPC ao seu node. Ele é a forma mais prática e segura de interagir com um Nó local. A seguir veremos alguns outros exemplos de comandos que podem ser enviados:

```bash
**# Status da rede e conexões**
bitcoin-cli -datadir=/home/user1/bitcoin-regtest-node1 getnetworkinfo

**# Mostra o saldo da carteira**
bitcoin-cli -datadir=/home/user1/bitcoin-regtest-node1 -rpcwallet=NovaCarteira getbalance

**# Retorna o hash do bloco na altura 0 (bloco gênese)**
bitcoin-cli -datadir=/home/user1/bitcoin-regtest-node1 getblockhash 0

**# Mostra informações detalhadas de um bloco (pelo hash)**
bitcoin-cli -datadir=/home/user1/bitcoin-regtest-node1 getblock <hash_do_bloco>

**# Lista UTXOs da carteira (saídas não gastas)**
bitcoin-cli -datadir=/home/user1/bitcoin-regtest-node1 -rpcwallet=NovaCarteira listunspent
```

Ao longo dos próximos artigos usaremos vários comandos do bitcoin-cli para interagir com o Nó. Cabe ressaltar que é possível também interagir diretamente com o Nó usando ferramentas como curl, bastando fazer requisições HTTP:

```bash
curl --user teste:teste \
  --data-binary '{"jsonrpc":"1.0","id":"exemplo","method":"getblockcount","params":[]}' \
  -H 'content-type:text/plain;' http://127.0.0.1:18443/
```

Também é importante entender que as configurações passadas no arquivo **bitcoin.conf** podem ser indicadas alternativamente através de argumentos na linha de comando do **bitcoin-cli** e do **bitcoind**:

```bash
bitcoin-cli -regtest -rpcport=18443 -datadir=/home/user1/bitcoin-regtest-node1 getblockhash 0
```

📝 Para finalizar este artigo iremos fazer um exemplo mais completo. Neste teste, vamos simular a comunicação entre dois Nós Bitcoin rodando em modo regtest. A ideia é demonstrar, na prática, que os Nós se conectam, sincronizam blocos e propagam transações. Também vamos criar carteiras, minerar blocos, gerar saldo e enviar uma transação de um Nó para outro, observando sua presença na mempool antes da confirmação. Abaixo vemos as etapas que serão feitas:

```bash
#Exemplo Avançado

1. Criar duas pastas de dados separadas para os dois nós (node1 e node2);

2. Configurar o arquivo bitcoin.conf de cada nó, definindo portas e credenciais;

3. Iniciar os dois nós (bitcoind) em modo regtest;

4. Conectar manualmente os dois nós;

5. Verificar que os nós estão realmente conectados;

6. Criar uma carteira em cada Nó;

7. Gerar endereços;

8. Minerar 101 blocos no Nó 1 para liberar saldo;

9. Enviar 1 BTC do Nó 1 para o Nó 2;

10. Verificar a transação pendente no Nó 2;

11. Consultar a mempool dos dois Nós para confirmar que a transação foi propagada;

12. Minerar mais um bloco no Nó 1 para confirmar a transação;

13. Confirmar que a transação foi incluída no bloco.
```

## Etapa 1 - Criar as pastas de dados separadas para os 2 Nós

```bash
mkdir -p /home/user/bitcoin-regtest-node1
mkdir -p /home/user/bitcoin-regtest-node2
```

## Etapa 2 - Configurar o arquivo bitcoin.conf de cada Nó

```bash
#Criar arquivo /home/user/bitcoin-regtest-node1/bitcoin.conf

regtest=1
rpcuser=teste
rpcpassword=teste
rpcallowip=127.0.0.1
fallbackfee=0.0001
[regtest]
rpcport=18443
port=18444
```

```bash
#Criar arquivo /home/user/bitcoin-regtest-node2/bitcoin.conf

regtest=1
rpcuser=teste
rpcpassword=teste
rpcallowip=127.0.0.1
fallbackfee=0.0001
[regtest]
rpcport=18453
port=18454
```

## Etapa 3 - Iniciar os 2 Nós em modo regtest

```bash
bitcoind -regtest -datadir=/home/user/bitcoin-regtest-node1 -daemon
bitcoind -regtest -datadir=/home/user/bitcoin-regtest-node2 -daemon
```

## Etapa 4 - Conectar os dois Nós

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node2 addnode 127.0.0.1:18444 add
```

## Etapa 5 - Verificar que os Nós estão realmente conectados

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 getpeerinfo
```

## Etapa 6 - Criar uma carteira em cada Nó

```bash
#Nó 1
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 createwallet "minerador"

#Nó 2
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node2 createwallet "recebedor"
```

## Etapa 7 - Gerar endereços

```bash
#Nó 1
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 -rpcwallet=minerador getnewaddress

#Nó 2
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node2 -rpcwallet=recebedor getnewaddress
```

Anote os endereços gerados.

## Etapa 8 - Minerar 101 blocos no Nó 1 para liberar saldo

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 -rpcwallet=minerador generatetoaddress 101 <endereco_minerador>
```

Observação: os bitcoins gerados na **coinbase** (primeira transação de um bloco, que cria novos bitcoins) só podem ser gastos após 100 confirmações — por isso mineramos 101 blocos.

## Etapa 9 - Enviar 1 BTC do Nó 1 para o Nó 2

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 -rpcwallet=minerador sendtoaddress <endereco_recebedor> 1
```

## Etapa 10 - Verificar a transação pendente no Nó 2

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node2 listtransactions
```

A transação deve aparecer com "confirmations": 0

## Etapa 11 - Consultar a mempool dos dois Nós para confirmar que a transação foi propagada

```bash
#Nó 1
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 getrawmempool

#Nó 2
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node2 getrawmempool
```

Ambos devem retornar o mesmo txid (hash da transação)

## Etapa 12 - Minerar mais um bloco no Nó 1 para confirmar a transação

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node1 -rpcwallet=minerador generatetoaddress 1 <endereco_minerador>
```

## Etapa 13 - Confirmar que a transação foi incluída no bloco

```bash
bitcoin-cli -datadir=/home/user/bitcoin-regtest-node2 listtransactions
```

A transação agora deve ter "confirmations": 1 ou mais

Neste artigo, vimos na prática como os Nós Bitcoin funcionam. Com exemplos em regtest, foi possível observar a propagação de blocos, a criação de transações e a sincronização entre Nós. Compreender esses mecanismos é fundamental para desenvolvedores que desejam se aprofundar no funcionamento interno do Bitcoin e contribuir diretamente com o ecossistema.

Em breve será publicada a Parte 2 deste artigo sobre Nós Bitcoin, abordando temas complementares que ficaram de fora desta primeira introdução prática. Esta próxima etapa trará uma abordagem mais profunda e voltada a desenvolvedores que desejam entender o funcionamento interno dos Nós do Bitcoin Core. Essa continuação visa aprofundar o entendimento de como um Nó Bitcoin opera por dentro, revelando os mecanismos que garantem sua segurança, conectividade e papel fundamental na rede.

---
Escrito por:  

Rafael Santos
