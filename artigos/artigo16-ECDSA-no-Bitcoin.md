# ECDSA no Bitcoin: anatomia da assinatura

Antes de mergulhar nos detalhes matemáticos do ECDSA, é essencial compreender **o propósito fundamental de uma assinatura digital**: provar a posse de uma chave privada **sem jamais revelá-la**.

Essa é a base da soberania criptográfica no Bitcoin. Cada vez que uma transação é transmitida, o remetente demonstra ao mundo que controla determinado UTXO, mas sem expor seu segredo.

Em termos simples, uma assinatura é um **selo matemático** que liga três elementos:

1. **A mensagem** (no caso do Bitcoin, partes da transação),
2. **A chave privada** (segredo do proprietário),
3. **O algoritmo de assinatura** (ECDSA, no caso do protocolo).

O resultado é um par de números, normalmente chamados de **(r, s),** que permitem a qualquer um verificar a autenticidade, mas impossibilitam reconstruir a chave privada original.

**Hashing ≠ Assinatura**

Embora o hashing e a assinatura digital pareçam relacionados, eles têm papéis distintos.

- O **hash** é uma operação unidirecional, usada para gerar uma “impressão digital” única de uma mensagem.
- A **assinatura digital**, por sua vez, é uma operação **assimétrica**, na qual apenas quem tem a chave privada pode gerar a assinatura, mas qualquer um com a chave pública pode verificá-la.

No Bitcoin, as duas técnicas trabalham em conjunto: o hash da transação é calculado antes da assinatura, garantindo que o resultado dependa do conteúdo exato da transação.

Assim, **qualquer alteração em um byte sequer invalida imediatamente a assinatura**.

**Determinismo e o papel do número k**

Um dos pontos mais delicados do ECDSA é o número **k**, também chamado de *nonce*.

Ele é um número aleatório usado **uma única vez** em cada assinatura, mas se for reutilizado ou previsível, a segurança se quebra por completo.

Isso porque tanto `r` quanto `s` (os dois componentes da assinatura) dependem diretamente de `k`. Se dois documentos diferentes forem assinados com o mesmo `k`, qualquer observador poderá extrair a chave privada.

Para evitar esse risco, o Bitcoin segue a **RFC 6979**, que define um modo *determinístico* de gerar `k`: em vez de ser totalmente aleatório, ele é calculado a partir do **hash da mensagem** e da **chave privada**, garantindo que o valor seja único e imprevisível e, ao mesmo tempo, reproduzível de forma segura.

---

### A curva elíptica secp256k1

O núcleo matemático do Bitcoin é uma curva elíptica chamada **secp256k1**. Ela é o alicerce sobre o qual se constroem as chaves públicas e as assinaturas digitais que garantem a segurança do sistema. Antes de entendê-la em detalhes, vale recordar o que é uma curva elíptica em termos gerais.

Uma **curva elíptica** é um conjunto de pontos que satisfaz uma equação do tipo:

$$
y^2=x^3+ax+b
$$

onde `a` e `b` são constantes que determinam a forma da curva.

Essas curvas têm propriedades geométricas especiais: é possível **somar dois pontos** sobre a curva e obter um terceiro ponto também pertencente a ela. Esse tipo de operação (chamada de *adição de pontos)* é o que dá origem à aritmética usada na criptografia moderna.

No Bitcoin, a curva adotada é **secp256k1**, definida pela equação:

$$
y^2=x^3+7 
$$

ou seja, `a = 0` e `b = 7`.

O nome *secp256k1* traz informações importantes:

- **secp** → *Standards for Efficient Cryptography Prime curve*
- **256** → tamanho das chaves privadas, em bits
- **k1** → indica uma família de curvas com parâmetros simples (koblitz curves)

Ela é usada sobre um **campo finito**, o que significa que todos os cálculos são feitos **módulo um número primo enorme**:

$$p=FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F$$

ou

$$p=2^{256}−2^{32}−977$$ 

Esse valor `p` define o “limite” do campo:

quando uma operação ultrapassa esse número, ela **volta ao início**, como um relógio de 12 horas. É essa aritmética modular que permite fazer cálculos seguros e previsíveis, sem infinitos ou frações.

**O ponto gerador e a ordem do grupo**

Para transformar essa estrutura geométrica em um sistema criptográfico, o Bitcoin define um **ponto gerador G**, fixo e público, que serve de base para todas as operações.

```
G = 04 
		79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798 
		483ADA77 26A3C465 5DA4FBFC 0E1108A8 FD17B448 A6855419 9C47D08F FB10D4B8
```

A partir dele, cria-se um conjunto de pontos obtidos por múltiplas adições sucessivas de `G`:

$$
2G=G+G,3G=2G+G,4G=3G+G,…
$$

Esse conjunto é **cíclico**, ou seja, depois de certo número de somas, o resultado volta ao ponto inicial. Esse número é chamado de **ordem** da curva, e é representado por `n`:

$$
n=FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
$$

**Chaves privadas e públicas**

A **chave privada** (`d`) é simplesmente um número aleatório entre `1` e `n−1`.

A **chave pública** (`Q`) é o resultado da multiplicação desse número pelo ponto gerador `G`:

$$
Q=d×G
$$

Essa operação significa somar `G` a si mesmo `d` vezes.

Embora pareça simples, o processo inverso (descobrir `d` a partir de `Q`) é considerado **computacionalmente impossível**. Esse é o chamado **problema do logaritmo discreto sobre curvas elípticas**, o fundamento de segurança do Bitcoin.

---

### **O algoritmo ECDSA**

Se a curva elíptica define o terreno onde tudo acontece, o **ECDSA (Elliptic Curve Digital Signature Algorithm)** é o conjunto de regras que transforma a chave privada em uma **assinatura digital verificável**.

É ele quem garante que apenas o detentor da chave possa autorizar um gasto e que qualquer nó da rede possa confirmar essa autorização sem depender de confiança.

O ECDSA é dividido em duas fases: **assinatura** e **verificação**. Ambas usam as mesmas operações da curva `secp256k1`, mas em direções opostas.

**Fase 1 – Assinatura**

O objetivo é gerar dois números, **r** e **s**, que formarão a assinatura final.

Esses números são resultado de operações modulares sobre a curva elíptica e sobre o hash da mensagem (no caso do Bitcoin, o hash da transação).

O processo ocorre assim:

1. **Escolher um número aleatório k**
    - Deve ser único e imprevisível para cada assinatura.
    - É chamado de *nonce*.
    - Se `k` for reutilizado, a chave privada pode ser revelada (falhas famosas já ocorreram por causa disso).
2. **Gerar o ponto R na curva**
    
$$
R=k×G
$$
    
O valor **r** é a coordenada x desse ponto, reduzida módulo `n`:
    
$$
r=R_x \bmod n
$$
    
3. **Calcular o hash da mensagem**
    
No Bitcoin, a mensagem a ser assinada é o *hash da transação*, já processado de acordo com o tipo de `SIGHASH`:
    
$$
z = \text{SHA256(SHA256(mensagem))}
$$
    
O resultado `z` é um número inteiro entre `0` e `n-1`.
    
4. **Calcular o valor s**
    
Este é o passo que envolve a chave privada (`d`):
    
$$
s = k^{-1} (z + r·d) \bmod n
$$
    
Aqui, `k⁻¹` é o inverso multiplicativo de `k` módulo `n`.
    

A assinatura final é o **par (r, s)**, que será codificado no formato **DER** antes de ser anexado à transação.

Resumindo: `r` vem da curva e `s` vem da chave privada. Juntos, eles provam que o signatário possui a chave que corresponde ao endereço de origem.

**Fase 2 – Verificação**

O verificador tem acesso à **mensagem (z)**, à **assinatura (r, s)** e à **chave pública (Q)**.

O desafio é confirmar se `(r, s)` realmente foi gerado a partir de `Q`, sem conhecer `d`.

O processo é o inverso da assinatura:

1. Calcular o inverso de `s`:
    
$$
w = s^{-1} \bmod n
$$
    
2. Calcular dois coeficientes:
    
$$
u_1 = z·w \bmod n,\quad u_2 = r·w \bmod n
$$
    
3. Combinar os dois pontos na curva:
    
$$
X = u_1·G + u_2·Q
$$
    
4. A assinatura é **válida** se:
    
$$
X_x \bmod n = r
$$
    

Essa verificação garante que somente quem possuiu a chave privada correspondente poderia ter produzido `(r, s)` para aquele `z`.

O aspecto mais elegante do ECDSA é sua simetria:

o mesmo ponto G e as mesmas operações são usadas tanto para **criar** quanto para **verificar** uma assinatura, apenas os papéis se invertem.

Durante a assinatura, a chave privada participa do cálculo, durante a verificação, a chave pública a substitui. Isso permite que qualquer pessoa valide a autenticidade de uma transação sem nunca ver o segredo que a originou.

**Sobre a aleatoriedade de k**

O valor `k` é o elo mais frágil do processo. Se ele for previsível ou repetido, é possível recuperar `d` pela simples diferença entre duas assinaturas:

$$
d = \frac{(s_1·k - z_1)}{r} \bmod n
$$

Por isso o Bitcoin utiliza **RFC 6979**, que torna `k` determinístico, calculado a partir do hash da mensagem e da chave privada. Isso elimina dependência de geradores aleatórios externos e previne vulnerabilidades catastróficas.

---

### **Exemplo em python**

Vamos ver um exemplo em python para entender melhor esse processo de assinaturas.

```python
# ex_ecdsa.py
from ecdsa import SigningKey, SECP256k1, util
import hashlib

# --- 1) chaves ---
sk = SigningKey.generate(curve=SECP256k1)              # chave privada (d)
vk = sk.get_verifying_key()                            # chave pública (Q)

priv_hex = sk.to_string().hex()
pub_xy = vk.to_string()                                # 64 bytes: x||y
x, y = pub_xy[:32], pub_xy[32:]
prefix = b'\x02' if (y[-1] & 1) == 0 else b'\x03'      # 02 se y par, 03 se ímpar
pub_compressed = (prefix + x).hex()

print("Chave privada (hex):", priv_hex)
print("Chave pública comprimida (hex):", pub_compressed)

# --- 2) mensagem e hash ---
msg = b"Transacao Bitcoin Coders"
z1 = hashlib.sha256(msg).digest()                      # SHA256 único (ok para demo)
z2 = hashlib.sha256(hashlib.sha256(msg).digest()).digest()  # SHA256d (fluxo tipico tx)

# --- 3) assinatura DER (RFC 6979 determinística) ---
sig_der = sk.sign_deterministic(z1, sigencode=util.sigencode_der)  # DER começa com 0x30
r_int, s_int = util.sigdecode_der(sig_der, sk.curve.generator.order())

print("\nAssinatura DER (hex):", sig_der.hex())
print("r =", r_int)
print("s =", s_int)

# --- 4) verificação (usando DER) ---
valid = vk.verify(sig_der, z1, sigdecode=util.sigdecode_der)
print("\nAssinatura válida?", valid)

# --- 5) teste de integridade ---
msg_bad = b"Transacao Bitcoin Coderz"  # 1 byte diferente
z_bad = hashlib.sha256(msg_bad).digest()
try:
    print("Assinatura ainda válida para msg_bad?",
          vk.verify(sig_der, z_bad, sigdecode=util.sigdecode_der))
except Exception:
    print("Assinatura ainda válida para msg_bad? False")

# --- 6) extra: assinando com SHA256d (como em tx Bitcoin) ---
sig_der_dbl = sk.sign_deterministic(z2, sigencode=util.sigencode_der)
ok_dbl = vk.verify(sig_der_dbl, z2, sigdecode=util.sigdecode_der)
print("\n[Extra] Assinatura (SHA256d) válida?", ok_dbl)

```

Obs: você precisará instalar o módulo `ecdsa`.

Rodando esse script, obtemos como resposta:

```python
Chave privada (hex): ce82fc4e6a6d7f2d0d91811f68b243af4f16620d2dd0d2352f91f2dfba83faa7
Chave pública comprimida (hex): 02fc3419e9830eb1aa155934f7a3324db30f6dca7bc9f321b99f1ab0c40ddc1a6a

Assinatura DER (hex): 304402204f42e66ec6a6fd86d131ebacd3942dba344444d4c212ebbd39e29198cd17ef3402204a0f37dd28ea25fb20ae38e6ae72291a99427c1fd365014ee79e8eb4b96d8520
r = 35850917332527842854576023313360054268363076929465430209753732273776008621876
s = 33498039059639490142276516930806616447695304690656852897813841950729365718304

Assinatura válida? True
Assinatura ainda válida para msg_bad? False

[Extra] Assinatura (SHA256d) válida? True
```

O script reproduz o funcionamento essencial do **ECDSA** no contexto do Bitcoin, desde a geração das chaves até a verificação da assinatura, incluindo a versão com **hash duplo (SHA256d)** usada nas transações reais. Vamos entender cada parte.

**1. Geração das chaves**

```python
sk = SigningKey.generate(curve=SECP256k1)
vk = sk.get_verifying_key()
```

Aqui é criada uma **chave privada (`sk`)** e sua correspondente **chave pública (`vk`)**, ambas sobre a curva elíptica `secp256k1`.

A chave privada é um número de 256 bits, enquanto a pública é um **ponto na curva**, composto pelas coordenadas `(x, y)`.

Em seguida, a chave pública é convertida para o formato **comprimido**, de 33 bytes:

```python
prefix = b'\x02' if (y[-1] & 1) == 0 else b'\x03'
pub_compressed = (prefix + x).hex()
```

O prefixo `02` indica que `y` é par, e `03` que é ímpar, exatamente o formato que o Bitcoin usa em endereços modernos (P2WPKH e Taproot).

**2. Mensagem e hash**

```python
msg = b"Transacao Bitcoin Coders"
z1 = hashlib.sha256(msg).digest()
z2 = hashlib.sha256(hashlib.sha256(msg).digest()).digest()
```

O texto é convertido em bytes e depois **hasheado**.

O primeiro hash (`z1`) representa uma assinatura simples para demonstração.

O segundo (`z2`) aplica **SHA256d**, o mesmo esquema usado pelo Bitcoin para gerar o hash das transações, ou seja, **duplo SHA-256**.

**3. Assinatura DER determinística**

```python
sig_der = sk.sign_deterministic(z1, sigencode=util.sigencode_der)
r_int, s_int = util.sigdecode_der(sig_der, sk.curve.generator.order())
```

O método `sign_deterministic()` segue a **RFC 6979**, que calcula o número aleatório `k` de forma **determinística** a partir do hash da mensagem e da chave privada, eliminando o risco de reutilização de `k`.

A assinatura resultante é codificada no formato **DER**, que é o padrão usado nas transações Bitcoin. O código também extrai os valores internos `(r, s)` para mostrar os números reais que formam a assinatura.

**4. Verificação da assinatura**

```python
valid = vk.verify(sig_der, z1, sigdecode=util.sigdecode_der)
```

Essa etapa realiza a **verificação criptográfica**:

usa a chave pública (`vk`), o hash da mensagem (`z1`) e a assinatura DER (`sig_der`).

O método refaz internamente as operações matemáticas do ECDSA:

$$
X = u_1·G + u_2·Q \quad\text{e}\quad X_x \bmod n = r
$$

Se o resultado for verdadeiro, a assinatura é válida, isto é, ela poderia ter sido gerada apenas com a chave privada correspondente à chave pública `vk`.

**5. Teste de integridade**

```python
msg_bad = b"Transacao Bitcoin Coderz"
```

Alterar apenas **um byte** da mensagem gera um hash completamente diferente.

A verificação falha, retornando `False`, demonstrando que **assinaturas Bitcoin são extremamente sensíveis ao conteúdo**.

Nenhuma modificação, por menor que seja, passa despercebida pela rede.

**6. Extra: assinando com SHA256d**

```python
sig_der_dbl = sk.sign_deterministic(z2, sigencode=util.sigencode_der)
```

Aqui o código assina o **duplo hash** (`z2`), reproduzindo exatamente o que o Bitcoin faz ao assinar transações reais. O resultado é outra assinatura válida, igualmente verificável com a chave pública.

**Em uma transação real**, o Bitcoin usa exatamente a mesma lógica, apenas substitui a mensagem pelo *preimage* da transação e adiciona o byte `SIGHASH` (`01` = SIGHASH_ALL) ao final do DER, formando a assinatura que aparece dentro do `scriptSig`.

---

Compreender o ECDSA é entender o motor matemático por trás das assinaturas Bitcoin.

Mas entre essa matemática e a rede existe uma camada de codificação: o formato **DER**, responsável por empacotar os números `(r, s)` em bytes padronizados e acrescentar o identificador **`SIGHASH`**. É esse empacotamento que transforma a assinatura em algo que o Bitcoin Core pode interpretar dentro do `scriptSig`.

No próximo artigo, vamos abrir essa estrutura byte a byte e ver como cada campo do DER representa a prova de posse na blockchain.
