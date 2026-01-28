# Como funciona uma carteira no Bitcoin Core: chaves, endereços e UTXOs

por Rafael Santos

Atualizado em: 08/08/2025 ∙ 30 min leitura

# Como funciona uma carteira no Bitcoin Core: chaves, endereços e UTXOs

No universo do Bitcoin, a carteira é o componente fundamental para a gestão de chaves e endereços, permitindo que o usuário envie, receba e controle seus bitcoins de forma segura. No Bitcoin Core, a carteira é um arquivo local que armazena suas chaves privadas e organiza seus saldos em UTXOs (saídas não gastas de transações), funcionando de forma diferente de carteiras online ou aplicativos que muitas pessoas estão acostumadas a usar. Neste artigo, vamos explorar de forma prática como funcionam as carteiras no Bitcoin Core, desde a criação de chaves e endereços até o gerenciamento dos UTXOs, utilizando comandos reais no terminal e scripts.

No Bitcoin Core, a carteira é representada principalmente por um arquivo chamado **wallet.dat**, que fica armazenado na pasta de dados do Bitcoin Core (por padrão ~/.bitcoin/wallets/). Esse arquivo funciona como um cofre digital, guardando com segurança todas as suas chaves privadas e informações essenciais para controlar os seus bitcoins. Vale lembrar que o arquivo não armazena as moedas em si, e sim as chaves que dão acesso aos saldos registrados na blockchain.

Você pode criar, carregar e visualizar diferentes carteiras facilmente usando comandos no terminal. Para criar uma nova carteira chamada “MinhaCarteira”, basta executar:

```bash
bitcoin-cli -datadir="." createwallet "MinhaCarteira"
```

Para ver todas as carteiras atualmente carregadas no Bitcoin Core, utilize:

```bash
bitcoin-cli -datadir="." listwallets
```

Cada carteira criada possui seu próprio **wallet.dat**, permitindo a organização separada de chaves e endereços. Assim, o Bitcoin Core oferece flexibilidade para quem deseja ter múltiplas carteiras, seja para diferentes projetos, perfis de uso ou níveis de segurança.

O wallet.dat é um arquivo de banco de dados no formato Berkeley DB (banco de dados leve e local). Ele não é apenas uma “lista de chaves”, mas um cofre que armazena tudo que o Bitcoin Core precisa para gerenciar sua carteira. Os principais elementos gravados no wallet.dat são:

### 1. **Chaves privadas**

- **Principal função do wallet.dat**: guardar suas chaves privadas.
- São essas chaves que “desbloqueiam” os bitcoins associados a endereços controlados pela carteira.

### 2. **Chaves públicas e endereços**

- As chaves públicas e endereços gerados a partir das chaves privadas também ficam armazenados para facilitar o uso e a identificação.

### 3. **Metadados das transações**

- O wallet.dat mantém informações sobre as transações recebidas, enviadas e seus respectivos status (confirmada, não confirmada, etc).
- Guarda também *labels* (etiquetas), notas e horários.

### 4. **UTXOs controlados pela carteira**

- Embora o saldo em si não fique “guardado”, o arquivo mantém uma referência aos UTXOs que pertencem à carteira, para calcular rapidamente o saldo disponível.

### 5. **Scripts e endereços usados**

- Scripts personalizados de pagamento, endereços usados anteriormente e informações auxiliares para reconstrução do histórico.

### 6. **Configurações de uso da carteira**

- Informações sobre bloqueios temporários, última vez usada, contas internas e preferências do usuário.

### 7. **Dados de segurança**

- Se a carteira estiver criptografada, o wallet.dat também armazena a chave criptográfica (protegida pela sua senha).
- Guarda também dados sobre seeds HD (quando disponível) e números de derivação de endereços (para carteiras HD).

Lembre-se que perder, corromper ou expor o arquivo wallet.dat, implica em comprometer o acesso aos seus Bitcoins. Alem disso, abrir, editar ou mover o arquivo manualmente pode corremper os dados também.

A pasta **src/wallet** no repositório oficial do Bitcoin Core contém todo o código fundamental usado para gerenciar carteiras, ou seja, para criação, carregamento, leitura, escrita, backup e restauração do arquivo wallet.dat.

Dentro dela, alguns dos arquivos mais relevantes incluem:

- **walletutil.cpp**: Onde o nome padrão do arquivo de carteira (wallet.dat) é definido, entre outras utilidades.
- **walletdb.cpp**: Responsável pelo gerenciamento do banco de dados da carteira, incluindo a abertura, leitura e escrita do wallet.dat usando Berkeley DB.
- **wallet.cpp**: Implementa a lógica principal da carteira, incluindo operações como restaurar backup e carregar a carteira no sistema.

# Chaves: Privadas, Públicas e Frase-semente

No Bitcoin, como na criptografia, tudo começa com um par de chaves: a chave privada e a chave pública.

**Chave privada**: é o segredo absoluto que permite gastar os bitcoins associados a ela.

**Chave pública**: é derivada da chave privada e, a partir dela, podemos gerar o endereço que você compartilha para receber bitcoins.

No Bitcoin Core, cada vez que você gera um novo endereço, o software cria automaticamente uma nova chave privada e sua correspondente chave pública. 

Diferente de muitas carteiras modernas, o Bitcoin Core não utiliza a **seed phrase** padrão **BIP39** (as famosas 12 ou 24 palavras). Em vez disso, todo o conjunto de chaves e metadados é armazenado no arquivo wallet.dat. Por isso, o backup desse arquivo é fundamental para manter acesso aos seus fundos.

Para criar um novo endereço na sua carteira e depois visualizar a chave privada correspondente, você pode usar:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" getnewaddress
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" dumpprivkey "endereço_gerado"
```

O primeiro comando cria um novo endereço e já o associa a uma chave privada interna da sua carteira. O segundo comando exibe a chave privada correspondente ao endereço informado.

**Observação**: só é possível usar o comando `dumpprivkey` em carteiras antigas. Por questões de segurança, em carteiras atuais isso não é permitido.

⚠ Atenção: nunca revele sua chave privada para ninguém e jamais a exponha em máquinas ou conexões não seguras. Quem tiver acesso a ela pode gastar todos os bitcoins daquele endereço.

Antigamente, no Bitcoin Core, ao criar um novo endereço, você estava automaticamente criando também um novo par de chaves (privada e pública), que eram armazenadas com segurança no wallet.dat. Posteriormente vieram as HD Wallets, que iremos falar em outro artigo.

Os principais tipos de endereços que você pode criar no Bitcoin Core são:

- **Legacy (P2PKH)** — formato mais antigo, começa com `1`.
- **SegWit (P2SH)** — formato intermediário, começa com `3`.
- **SegWit Nativo (bech32)** — formato moderno, começa com `bc1q`.
- **Taproot (bech32m)** — versão mais recente, começa com `bc1p` e habilita funcionalidades avançadas como assinaturas Schnorr.

Para criar endereços no Bitcoin Core, basta especificar o tipo ao usar o comando `getnewaddress`:

- **Legacy (P2PKH)**:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" getnewaddress "" "legacy"
```

- **SegWit (P2SH):**

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" getnewaddress "" "p2sh-segwit"
```

- **SegWit Nativo (bech32)**:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" getnewaddress "" "bech32"
```

- **Taproot (bech32m)**:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" getnewaddress "" "bech32m"
```

Se você executar os quatro comandos acima, verá que cada endereço começa com um prefixo diferente, identificando seu tipo. Esses formatos coexistem na rede Bitcoin e podem ser usados para receber transações, mas endereços SegWit e Taproot oferecem taxas mais baixas e recursos extras.

# UTXO

O Bitcoin utiliza o **modelo UTXO** (*Unspent Transaction Output*), que significa “saída de transação não gasta”. Cada vez que você recebe bitcoins, na verdade está recebendo um ou mais **UTXOs**, “moedas digitais” registradas na blockchain, associadas a um endereço que você controla. Quando você gasta, consome esses UTXOs e, se houver troco, cria novos UTXOs para si.

Para ver todos os UTXOs da sua carteira no Bitcoin Core, você pode usar:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" listunspent
```

O resultado será uma lista em formato JSON. Cada UTXO contém campos importantes, como:

- **txid** – Identificador único da transação que criou aquele UTXO.
- **vout** – Índice da saída na transação (`0`, `1`, etc.).
- **address** – Endereço que recebeu os fundos.
- **label** – Nome ou etiqueta atribuída ao endereço (se houver).
- **scriptPubKey** – Script que define como gastar aquele UTXO.
- **amount** – Quantidade de bitcoin disponível naquele UTXO.
- **confirmations** – Número de confirmações na blockchain.
- **spendable** – Indica se a carteira pode gastar aquele UTXO.

Pense em cada UTXO como uma moeda física, você pode gastar uma ou várias de uma vez para fazer um pagamento. A soma de todos os UTXOs é o saldo real da sua carteira.

---

# Na prática

Agora que entendemos chaves, endereços e UTXOs, vamos ver como tudo isso funciona na prática usando o Bitcoin Core. Para fins de teste, vamos usar a **signet**, podendo enviar e gastar bitcoins sem risco financeiro.

### **Recebendo Bitcoin**

O primeiro passo é gerar um endereço na sua carteira:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" getnewaddress
```

Esse comando cria um endereço novo (e o par de chaves correspondente) no seu `wallet.dat`.

Na **signet**, você pode usar *faucets* para receber BTC de teste.

---

### **Consultando seus UTXOs**

Depois de receber bitcoins, liste os UTXOs disponíveis:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" listunspent
```

O comando exibirá cada saída não gasta, com informações como `txid`, `vout`, `amount` e `address`.

---

### **Gastando Bitcoin**

Para gastar os BTCs, temos 2 maneiras. A primeira é criando uma transação em que o Bitcoin Core seleciona automaticamente os UTXOs (usando `sendtoaddress`):

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" sendtoaddress "endereco_destino" 0.01
```

Na segunda opção, podemos ter o controle total dos UTXOs, construindo a transação manualmente:

```bash
bitcoin-cli -datadir="." createrawtransaction \
'[{"txid":"<TXID_DO_UTXO>","vout":0}]' \
'{"endereco_destino":0.01,"endereco_troco":0.099}'
```

Após, devemos assinar a transação:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" signrawtransactionwithwallet "<hex_transacao>"
```

Por fim, enviamos para a rede:

```bash
bitcoin-cli -datadir="." sendrawtransaction "<hex_assinado>"
```

---

# Backup e Segurança das Carteiras

O arquivo `wallet.dat` é o componente principal da carteira no Bitcoin Core. Ele contém todas as chaves privadas e informações necessárias para gastar seus bitcoins. Por isso, **manter um backup atualizado é essencial**.

Para criar um backup do `wallet.dat`, utilize o comando:

```bash
bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" backupwallet "caminho/backup_wallet.dat"
```

Esse backup pode ser salvo em um pendrive, HD externo, ou até em um serviço de nuvem **com criptografia forte**.

💡 **Importante:** no Bitcoin Core, o backup do `wallet.dat` é a única forma de garantir que você poderá recuperar acesso aos seus fundos no futuro. Diferente de outras carteiras, ele não exibe uma seed phrase BIP39 para anotar — toda a informação necessária para recriar suas chaves privadas está dentro do `wallet.dat`. Perder esse arquivo (ou a senha, se a carteira estiver criptografada) significa perder permanentemente seus bitcoins.

### Restaurando uma carteira

Para restaurar, basta substituir o `wallet.dat` existente na pasta de dados do Bitcoin Core pelo arquivo de backup (com o Bitcoin Core fechado). Em seguida, abra o Bitcoin Core e carregue a carteira normalmente.

Se for uma instalação nova, basta colocar o `wallet.dat` na pasta `wallets/` e iniciar o Bitcoin Core.

### Segurança para desenvolvedores e operadores de nós

Quando desenvolvedores ou operadores mantêm o `wallet.dat` em computadores ou servidores, algumas práticas comuns de segurança incluem:

- **Criptografar a carteira** com senha forte:
    
    ```bash
    bitcoin-cli -datadir="." -rpcwallet="MinhaCarteira" encryptwallet "senha_muito_forte"
    ```
    
- **Usar discos criptografados** (LUKS no Linux, BitLocker no Windows, FileVault no macOS).
- **Nunca deixar o wallet.dat exposto** em servidores conectados à internet sem proteção adicional.
- **Controlar permissões de acesso** ao sistema, garantindo que apenas usuários autorizados possam ler o arquivo.
- **Manter backups offline** (cold storage), desconectados da rede, para evitar roubo por malware.
- **Assinaturas offline**: para grandes valores, usar um ambiente isolado (air-gapped) para assinar transações, mantendo a chave privada longe de computadores conectados.

Um **air-gapped** com o Bitcoin Core é uma configuração onde a máquina que **contém a carteira com as chaves privadas** nunca se conecta à internet, funcionando como um “cofre offline” para assinar transações com segurança máxima.

A ideia é separar as funções de **criação/assinatura de transações** e **transmissão na rede** em dois computadores:

- **Computador offline (air-gapped)** → Guarda o `wallet.dat` com as chaves privadas e assina transações. Nunca conecta à internet.
- **Computador online** → Conecta-se à rede Bitcoin para sincronizar blocos, criar transações parcialmente preenchidas e transmiti-las após assinatura.

Essas medidas são fundamentais porque **quem obtiver uma cópia do seu `wallet.dat` terá controle total sobre seus bitcoins**.

---

Entender como o Bitcoin Core organiza e protege suas chaves privadas, endereços e UTXOs é o primeiro passo para dominar o uso seguro e eficiente da rede Bitcoin. A lógica é: a **carteira** guarda suas **chaves**, as **chaves** geram **endereços** e os **endereços** controlam os **UTXOs** que representam seus fundos. Esse conhecimento básico é fundamental antes de avançar para operações mais complexas. No próximo artigo da série, vamos explorar em detalhe os **quatro tipos de endereços no Bitcoin Core**, suas características, vantagens e quando utilizar cada um. ₿🚀

---

Escrito por:  

Rafael Santos
