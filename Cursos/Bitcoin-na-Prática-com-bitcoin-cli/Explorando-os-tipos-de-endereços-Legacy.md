# Explorando os tipos de endereços no Bitcoin Core (Parte 1): Legacy

por Rafael Santos

Atualizado em: 15/08/2025 ∙ 30 min leitura

Entender sobre os diferentes tipos de endereços do Bitcoin exige conhecer um pouco da história da blockchain. Nesse artigo, irei apresentar uma parte mais teórica, para entender porque existem diferentes formatos de endereços e como eles funcionam. Posteriormente utilizaremos o `bitcoin-cli` do Bitcoin Core, `bash` e `python` para ver na prática exemplos e scripts funcionando na Signet.

No Bitcoin, **endereços não surgem do nada,** eles são derivados de uma **chave pública**, que por sua vez é gerada a partir de uma **chave privada**, como vimos no artigo anterior. Esse encadeamento é o que garante que apenas quem possui a chave privada pode gastar os bitcoins enviados para um determinado endereço. 

No início da rede, durante aproximadamente os 200 primeiros blocos, a maioria dos bitcoins minerados era paga diretamente para uma chave pública. Por isso era chamado de **P2PK** (*Pay to Public Key* ou “pague para uma chave pública”).

Pouco depois, o modelo P2PK foi substituído pelo **P2PKH** (*Pay to Public Key Hash*), no qual o pagamento é feito para o *hash* da chave pública. Essa mudança trouxe duas vantagens importantes:

1. **Privacidade** – a chave pública só é revelada quando o output é gasto, e não no momento em que é criado.
2. **Segurança futura** – caso algum dia a criptografia da curva elíptica seja quebrada, os bitcoins enviados para P2PKH permanecerão protegidos até serem gastos, ao contrário dos P2PK.

📜 **Importante:** desde o início, cada transação no Bitcoin sempre envolveu executar um script para definir as regras de como ele pode ser gasto. Nos primeiros formatos, como o P2PK, o script era extremamente simples, algo como “pague para esta chave pública”. Com o tempo, ele foi ficando mais sofisticado, permitindo pagar para o hash de uma chave pública, esconder condições mais complexas e até combinar várias regras de gasto.

No Bitcoin, cada **output** contém um `scriptPubKey`, o “contrato” que define como ele pode ser gasto. Para gastar esse output, quem o recebeu precisa fornecer um `scriptSig` (ou, em SegWit, os *witness data*) que satisfaça esse contrato. Esses dois scripts são concatenados e executados pela **máquina de script** do Bitcoin, que valida se as condições de gasto foram cumpridas. Mais adiante, em outro artigo, veremos como essa máquina de script funciona, por hora, podemos abstrair essa questão.

➡️ **Esse avanço do P2PK para o P2PKH** marcou a adoção do formato de endereço **Legacy** com prefixo `1`(na mainnet) . O processo para criar um endereço P2PKH segue um fluxo bem definido:

1. **`Gera-se uma chave privada** aleatória (256 bits).`
2. **`Calcula-se a chave pública** via ECDSA (*secp256k1*).`
3. `Aplica-se **SHA-256** e depois **RIPEMD-160** na chave pública, obtendo um **hash160** (20 bytes).`
4. `Prefixa-se esse hash com o **version byte** 0x00 (para mainnet) e calcula-se um **checksum** (SHA-256 duplo, 4 bytes).`
5. `Codifica-se tudo em **Base58Check**, resultando em um endereço que começa com 1.`
6. `Esse hash é colocado no scriptPubKey do UTXO:`
    
    ```
    OP_DUP OP_HASH160 <hash160(pubkey)> OP_EQUALVERIFY OP_CHECKSIG
    ```
    
    Assim, só quem tiver a chave privada capaz de gerar aquela chave pública poderá gastar os fundos.
    
    ℹ️ **Observação 1:**  para as outras redes (testnet, signet e regtest), apenas o prefixo é trocado, resultando em endereços que começam com `m` ou `n`.
    
    ℹ️ **Observação 2:** Embora possamos abstrair a implementação desses algoritmos para entender o processo como um todo, vale saber em linhas gerais o papel de cada um:
    
    - **ECDSA (secp256k1):** gera chaves públicas a partir de chaves privadas usando curvas elípticas.
    - **SHA-256:** função de hash criptográfica que produz 256 bits de saída.
    - **RIPEMD-160:** função de hash de 160 bits usada junto ao SHA-256 para compor o identificador da chave pública.
    - **Base58Check:** esquema de codificação com alfabeto reduzido e checksum, evitando erros de digitação.
    
    Didaticamente, podemos comparar o endereço gerado pronto pelo Bitcoin Core com esse processo de criação de endereços. No Bitcoin Core, podemos criar um endereço em uma carteira e obter a chave privada facilmente com o script abaixo:
    
    ```bash
    # cria/carrega wallet LEGACY (BDB), gera endereço P2PKH e mostra WIF
    # Wallet: se já estiver carregada, segue; senão tenta carregar; se não existir, cria (LEGACY)
    if ! bitcoin-cli -datadir="." -signet -rpcwallet=demo-legacy getwalletinfo >/dev/null 2>&1; then
      if ! bitcoin-cli -datadir="." -signet loadwallet "demo-legacy" >/dev/null 2>&1; then
        bitcoin-cli -datadir="." -signet createwallet "demo-legacy" false false "" false false true false >/dev/null
      fi
    fi
    # Endereço
    ADDR=$(bitcoin-cli -datadir="." -signet -rpcwallet=demo-legacy getnewaddress "" legacy)
    echo "🏠 Endereço       	= ${ADDR}"
    # Info
    INFO=$(bitcoin-cli -datadir="." -signet -rpcwallet=demo-legacy getaddressinfo "${ADDR}")
    #echo "spk=$(echo "$INFO" | jq -r .scriptPubKey)"
    echo "🔑 Chave pública 	= $(echo "$INFO" | jq -r .pubkey)"
    # WIF
    WIF=$(bitcoin-cli -datadir="." -signet -rpcwallet=demo-legacy dumpprivkey "${ADDR}")
    echo "🗝️  Chave privada (wif) 	= ${WIF}"
    ```
    
    ⚠️ Importante: no **Bitcoin Core** atual (desde a versão 0.21), aconteceu uma mudança grande:
    
    ### Antes (anterior a 0.21)
    
    - As wallets eram baseadas em **Berkeley DB (BDB)**.
    - Essas são as chamadas **legacy wallets** (não usam *descriptors*).
    - Permitem `dumpprivkey` para obter facilmente a chave privada.
    
    ### Agora (desde a 0.21)
    
    - O Bitcoin Core migrou para **Descriptor Wallets** (SQLite).
    - São mais seguras, organizadas e permitem múltiplos scripts (SegWit, Taproot, etc).
    - Mas **não têm suporte direto** a alguns RPCs antigos, como `dumpprivkey`.
    
    Para criar wallet legacy BDB, o `bitcoind` precisa ser iniciado com `-deprecatedrpc=create_bdb` :
    
    ```bash
    bitcoind -datadir="." -daemon -deprecatedrpc=create_bdb
    ```
    
    Rodando o script anterior, obtemos:
    
    ```bash
    ./cria_endereco_e_pega_chave_privada.sh
    🏠 Endereço       	      = mz4fq4uwAaHQjGszvtV65DxuMLk8bWXafD
    🔑 Chave pública 	        = 03bfd3218ca0a09183062a8f0ef0b238f726e88fc78b19846e150d065f104a3e03
    🗝️ Chave privada (wif)  	= cV5dB3YUbKfuuRbmp7yKbf6sM4cDQE5jTk96kSfvEeS6obdDJean
    ```
    
    Explicando o código: após criar ou carregar a carteira, foi usado o comando `getnewaddress` do bitcoin-cli para gerar um novo endereço legacy na carteira. No fim, basta utilizar o comando `dumpprivkey` do bitcoin-cli para obter a chave privada correspondente ao endereço. 
    
    Agora, a partir da chave privada obtida, podemos reconstruir o endereço “na mão” e compará-lo com o endereço fornecido pelo Bitcoin Core. O primeiro passo é **`Calcular a chave pública** via ECDSA (*secp256k1*).` O script abaixo faz este cálculo e mostra a chave pública correspondente:
    
    ```bash
    # Uso:
    #   ./calcular_chave_publica.sh <WIF>
    #   ./calcular_chave_publica.sh --hex <priv_hex32>
    
    if [[ $# -lt 1 ]]; then
      echo "Uso: $0 <WIF> | --hex <priv_hex32>" >&2
      exit 1
    fi
    
    MODE="wif"; INPUT="$1"; shift || true
    if [[ "$INPUT" == "--hex" ]]; then
      MODE="hex"; INPUT="${1:-}"; shift || true
    fi
    
    python3 - "$MODE" "$INPUT" <<'PY'
    import sys, hashlib
    
    # --- Base58Check (decode) ---
    ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    def b58decode(s: str) -> bytes:
        n = 0
        for c in s.encode():
            n = n*58 + ALPHABET.index(c)
        full = n.to_bytes((n.bit_length()+7)//8, 'big')
        z = len(s) - len(s.lstrip('1'))
        return b'\x00'*z + full
    def b58decode_check(s: str) -> bytes:
        full = b58decode(s)
        if len(full) < 4: raise ValueError('b58 too short')
        payload, checksum = full[:-4], full[-4:]
        chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        if chk != checksum: raise ValueError('bad checksum')
        return payload
    
    mode, val = sys.argv[1], sys.argv[2]
    
    # --- chave privada (32 bytes) ---
    if mode == 'wif':
        payload = b58decode_check(val)
        version = payload[0]
        compressed_flag = (len(payload) == 34 and payload[33] == 0x01)
        priv = payload[1:33]
        net = 'mainnet' if version == 0x80 else ('testnet/signet' if version == 0xEF else f'0x{version:02x}')
    else:
        priv = bytes.fromhex(val)
        if len(priv) != 32:
            raise SystemExit('[fail] --hex precisa ter 32 bytes (64 hex)')
        compressed_flag = True
        net = '(hex)'
    
    try:
        from ecdsa import SigningKey, SECP256k1
    except Exception:
        raise SystemExit("[fail] 'ecdsa' ausente. Instale: pip install ecdsa")
    
    sk = SigningKey.from_string(priv, curve=SECP256k1)
    vk = sk.verifying_key
    x, y = vk.pubkey.point.x(), vk.pubkey.point.y()
    
    pub_c = (b"\x02" if (y % 2 == 0) else b"\x03") + x.to_bytes(32, 'big')
    pub_u = b"\x04" + x.to_bytes(32, 'big') + y.to_bytes(32, 'big')
    
    print(f"🗝️  PrivKey (hex) : {priv.hex()}")
    print(f"🔑 PubKey (compr): {pub_c.hex()}")
    print(f"🔓 PubKey (full) : {pub_u.hex()}")
    PY
    
    ```
    
    Perceba que não utilizamos o Bitcoin Core nesse script, apenas  o bash e python. Não precisamos entender a fundo os algorítmos usados nesse momento, mas abstraindo um pouco, o que esse script faz é:
    
    ```bash
    1. Entrada → interpreta os parâmetros (formato WIF ou --hex).
    2. Decodificação → transforma WIF/hex em chave privada crua (32 bytes).
    3. Cálculo (ECDSA) → a partir da chave privada, gera o ponto público (x, y).
    4. Formatação → monta chave pública comprimida e não comprimida.
    5. Saída → imprime chave privada (hex) e as chaves públicas.
    ```
    
    Abaixo vemos o script rodando e os resultados:
    
    ```bash
    ./calcula_chave_publica.sh cV5dB3YUbKfuuRbmp7yKbf6sM4cDQE5jTk96kSfvEeS6obdDJean
    🗝️ PrivKey (hex) : dfbda42d8bf50677dcd9e2e689ac6aec9247e81e674d62116bc4c3ce3af57036
    🔑 PubKey (compr): 03bfd3218ca0a09183062a8f0ef0b238f726e88fc78b19846e150d065f104a3e03
    🔓 PubKey (full) : 04bfd3218ca0a09183062a8f0ef0b238f726e88fc78b19846e150d065f104a3e039d1a05c776bdf79540d7f095bd7d8a05464d8a1699ef8d311805a748a25f2f7f
    ```
    
    Observe que o script mostra tanto a chave pública comprimida (a padão) e a não comprimida (full). Após a chave pública ser calculada, podemos passar para a etapa final: reconstrução do endereço:
    
    ```bash
    # Uso:
    #   ./reconstruir_endereco_p2pkh_clean.sh <pubkey_hex>
    # Saída: PubKey, hash160, scriptPubKey, Address (testnet/signet)
    
    if [[ $# -lt 1 ]]; then
      echo "Uso: $0 <pubkey_hex>" >&2
      exit 1
    fi
    
    PUBHEX="$1"
    VERSION_HEX="6f"   # testnet/signet
    
    python3 - <<PY
    import sys, hashlib
    
    PUBHEX = "${PUBHEX}"
    VERSION = bytes.fromhex("${VERSION_HEX}")
    
    # Base58Check (encode) - sem dependências externas
    ALPHABET = b'123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    def b58encode(b: bytes) -> str:
        n = int.from_bytes(b, 'big')
        out = bytearray()
        while n > 0:
            n, r = divmod(n, 58)
            out.append(ALPHABET[r])
        # preserva zeros à esquerda
        z = 0
        for byte in b:
            if byte == 0: z += 1
            else: break
        return (ALPHABET[:1]*z + out[::-1]).decode()
    
    # RIPEMD-160 com fallback para pycryptodome
    try:
        _ = hashlib.new('ripemd160')
        def ripemd160(data: bytes) -> bytes:
            h = hashlib.new('ripemd160'); h.update(data); return h.digest()
    except ValueError:
        try:
            from Crypto.Hash import RIPEMD160
            def ripemd160(data: bytes) -> bytes:
                h = RIPEMD160.new(); h.update(data); return h.digest()
        except Exception:
            sys.exit('[fail] RIPEMD160 indisponível. Instale: pip install --user pycryptodome')
    
    # Inputs
    try:
        pub = bytes.fromhex(PUBHEX)
    except ValueError:
        sys.exit('[fail] pubkey inválida: hex contínuo, sem espaços')
    
    # Cálculos
    sha = hashlib.sha256(pub).digest()
    h160 = ripemd160(sha)
    spk = bytes.fromhex('76a914') + h160 + bytes.fromhex('88ac')
    payload = VERSION + h160
    chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    addr = b58encode(payload + chk)
    
    # Saída
    print(f"🔑 PubKey        : {PUBHEX}")
    print(f"🧮 hash160       : {h160.hex()}")
    print(f"🧾 scriptPubKey  : {spk.hex()}")
    print(f"🏠 Address       : {addr}")
    PY
    ```
    
    Explicando o código:
    
    ```bash
    1. Entrada → recebe a chave pública em hex (comprimida).
    2. Conversão → transforma a pubkey em bytes e prepara versão de rede (testnet/signet).
    3. Hashing → aplica SHA-256 seguido de RIPEMD-160 → obtém o hash160.
    4. Script → monta o scriptPubKey padrão P2PKH.
    5. Endereço → adiciona versão + checksum → codifica em Base58Check.
    6. Saída → imprime pubkey, hash160, scriptPubKey e endereço final.
    ```
    
    E sua execução:
    
    ```bash
    ./reconstruir_endereco_p2pkh.sh 03bfd3218ca0a09183062a8f0ef0b238f726e88fc78b19846e150d065f104a3e03
    🔑 PubKey        : 03bfd3218ca0a09183062a8f0ef0b238f726e88fc78b19846e150d065f104a3e03
    🧮 hash160       : cb71d4930cd0527b3d01d59761c44f3cabe56ce2
    🧾 scriptPubKey  : 76a914cb71d4930cd0527b3d01d59761c44f3cabe56ce288ac
    🏠 Address       : mz4fq4uwAaHQjGszvtV65DxuMLk8bWXafD
    ```
    
    Perceba que o endereço (mz4fq4uwAaHQjGszvtV65DxuMLk8bWXafD) é o mesmo fornecido pelo Bitcoin Core lá no início.
    
    Lembrando que o Bitcoin Core usa atualmente **Descriptor Wallets**, que é mais complexo e seguro e abordaremos em artigos no futuro. Também é importante perceber que esses exemplos e script vistos até aqui lidaram com os endereços Legacy. Com o passar do tempo os tipos de endereço foram evoluindo. 
    

## 🕒 Evolução dos formatos de endereço no Bitcoin

A evolução dos endereços no Bitcoin acompanhou a busca por **mais segurança, eficiência, privacidade e escalabilidade**.

Podemos resumir essa trajetória assim:

1. **P2PK (Pay to Public Key)** — pagamentos diretos para a chave pública.
2. **P2PKH (Pay to Public Key Hash)** — pagamentos para o *hash* da chave pública, ocultando-a até o gasto.
3. **P2SH (Pay to Script Hash)** — pagamentos para o *hash* de um script arbitrário, permitindo condições mais complexas.
4. **SegWit (P2WPKH e P2WSH)** — separa assinaturas dos dados principais da transação, reduzindo custos e aumentando a capacidade de blocos.
5. **Taproot (P2TR)** — combina a eficiência do Schnorr com a possibilidade de esconder scripts complexos atrás de uma única chave.

## Por que existem diferentes tipos de endereço?

No começo, os endereços P2PKH dominaram o Bitcoin: simples, fáceis de usar e aceitos em qualquer serviço. Mas, à medida que a rede cresceu, ficaram claros os limites: transações caras, blocos cheios e pouca flexibilidade. Daí vieram novas formas: P2SH para compatibilidade, SegWit (P2WPKH e P2WSH) para reduzir taxas e corrigir problemas de maleabilidade, e, mais recentemente, Taproot, que combina assinaturas Schnorr com árvores Merkle. Cada evolução foi um passo para resolver gargalos sem quebrar a retrocompatibilidade.

Quanto ao `bitcoin-cli`, isso significa que o mesmo comando `getnewaddress` pode gerar endereços de diferentes gerações (legacy, segwit, bech32, taproot). Cada tipo reflete objetivos práticos: compatibilidade com carteiras antigas, eficiência no uso de espaço em bloco, melhor escalabilidade e mais privacidade. No fim, entender esses formatos não é só teoria, é escolher o endereço certo para economizar em taxas, ter mais flexibilidade em scripts e garantir que sua transação seja aceita em qualquer lugar da rede.

Como vimos no artigo anterior, podemos criar os diferentes tipos de endereço com bitcoin-cli:

```bash
bitcoin-cli -signet -rpcwallet=CarteiraDemo getnewaddress "" legacy
bitcoin-cli -signet -rpcwallet=CarteiraDemo getnewaddress "" p2sh-segwit
bitcoin-cli -signet -rpcwallet=CarteiraDemo getnewaddress "" bech32
bitcoin-cli -signet -rpcwallet=CarteiraDemo getnewaddress "" bech32m
```

---

## Próximo…

Os endereços **Legacy** foram o ponto de partida para todo o ecossistema do Bitcoin, mas a rede evoluiu bastante desde então. Novos formatos, como **SegWit** e **Taproot**, trazem ganhos importantes em **eficiência, privacidade e escalabilidade**. Entender o histórico ajuda a enxergar o porquê de coexistirem tantos tipos de endereços e como cada um resolve limitações do anterior.

No próximo artigo, vamos sair da teoria e mergulhar mais fundo nos **endereços modernos** e nas **Descriptor Wallets**, que representam a forma atual do Bitcoin Core lidar com chaves e scripts. Isso vai nos permitir explorar, na prática, como gerar endereços SegWit e Taproot, além de entender o papel dos *descriptors* na organização e segurança das carteiras.

---

![IMG-20250722-WA0010.jpg](Explorando%20os%20tipos%20de%20endere%C3%A7os%20no%20Bitcoin%20Core%20(/7d12c3ef-1d0d-4c45-8cf9-96c904b1cb21.png)

Escrito por:  

Rafael Santos

[A Maior Escola de Bitcoin do Mundo | Area Bitcoin](https://www.areabitcoin.com.br/)

[Instagram (@area.bitcoin)](https://www.instagram.com/area.bitcoin/)

[Area Bitcoin](https://www.youtube.com/c/AreaBitcoin)
