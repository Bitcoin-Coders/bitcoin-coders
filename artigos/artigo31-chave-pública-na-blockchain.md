# Sua chave pública já apareceu na blockchain?

Quando recebemos bitcoin, é comum pensar que tudo o que protege aquele saldo já está visível na blockchain. Mas nem sempre é assim.

Dependendo do tipo de output utilizado, a blockchain pode conter apenas um **compromisso com uma chave pública**, e não a chave pública propriamente dita. Em alguns casos, essa chave só aparece quando o bitcoin é gasto.

Essa diferença sempre existiu no Bitcoin, mas ganhou uma importância nova com as discussões sobre segurança pós-quântica.

No início de setembro, surgiu na lista de desenvolvimento do Bitcoin uma proposta para padronizar justamente essa pergunta:

> **a chave pública necessária para gastar determinado output já foi publicada on-chain?**
> 

Parece uma classificação simples. Na prática, diferentes ferramentas nem sempre concordam sobre a resposta.

### Uma chave que ainda não apareceu

Vamos pegar um output P2WPKH como exemplo.

Ao enviar bitcoin para um endereço desse tipo, o `scriptPubKey` não contém diretamente a chave pública. Ele contém um hash dela:

```
OP_0 <HASH160(pubkey)>
```

Podemos pensar nisso assim:

```
UTXO ainda não gasto

pubkey
  │
  └── HASH160
        │
        └── registrado na blockchain
```

Enquanto aquele UTXO permanece sem ser gasto, alguém observando apenas a blockchain não possui a chave pública que corresponde àquele hash.

Isso muda no momento do gasto.

Para provar que pode gastar o UTXO, o proprietário inclui no witness tanto a assinatura quanto a chave pública:

```
witness

assinatura
pubkey
```

A partir daquele momento, a chave pública passou a fazer parte permanentemente da história da blockchain.

Essa distinção também explica um dos problemas do **reuso de endereços**.

Imagine que um endereço P2WPKH recebeu vários pagamentos. Depois, apenas alguns daqueles UTXOs são gastos.

Ao realizar o primeiro gasto, a chave pública correspondente aparece na blockchain. Os outros bitcoins que continuam associados à mesma chave agora também têm uma chave pública conhecida.

Ou seja, não basta olhar apenas para o UTXO isoladamente. Às vezes é necessário olhar para o histórico daquela chave.

### Por que isso está sendo discutindo agora?

A razão principal é a discussão sobre computadores quânticos.

Os esquemas de assinatura usados atualmente pelo Bitcoin dependem da dificuldade de descobrir uma chave privada a partir de sua chave pública.

Um computador quântico suficientemente poderoso, executando algoritmos como o de Shor, mudaria esse cenário.

Isso cria uma diferença importante entre dois casos:

```
caso A

hash(pubkey) → conhecido
pubkey       → ainda desconhecida
```

e:

```
caso B

pubkey → conhecida
```

No segundo caso, um eventual atacante quântico já teria o material necessário para tentar derivar a chave privada.

No primeiro, ainda existe uma camada adicional: a chave pública propriamente dita não está disponível on-chain.

É justamente por isso que propostas recentes relacionadas a uma eventual migração pós-quântica precisam saber **quais moedas já possuem suas chaves públicas expostas**.

O problema é que hoje não existe uma definição única para isso.

### Afinal, o que significa estar “exposto”?

A proposta publicada recentemente tenta criar uma classificação padronizada para outputs existentes.

O draft define quatro situações:

```
EXPOSED_AT_REST
EXPOSED_ON_SPEND
NOT_EXPOSED
UNDETERMINED
```

A ideia é distinguir outputs cuja chave pública já está disponível, aqueles que só a revelarão quando forem gastos, aqueles cuja estrutura não expõe a chave dessa maneira e situações em que não há informação suficiente para determinar com segurança.

Isso parece detalhe de implementação, mas já existem divergências relevantes.

As estimativas citadas pelo autor para a quantidade de bitcoin atualmente associada a chaves públicas expostas variam de aproximadamente **25% a mais de 34% da oferta**. Segundo ele, boa parte dessa diferença não vem dos dados, mas das diferentes definições utilizadas pelas ferramentas.

Um exemplo é o próprio Taproot. Um output P2TR já coloca uma chave pública de 32 bytes diretamente no `scriptPubKey`. Isso faz com que sua classificação seja diferente de um P2WPKH ainda não gasto, mesmo sendo uma tecnologia mais recente.

Outro caso é um endereço P2PKH que já foi utilizado para gastar bitcoins, mas continua contendo outros UTXOs. A chave pública já apareceu em um gasto anterior e, portanto, aqueles bitcoins restantes não estão mais na mesma situação de um endereço nunca utilizado para gastar.

### Antes da solução, precisa-se identificar o problema

A proposta ainda está em discussão e não altera nenhuma regra de consenso do Bitcoin. Ela também não torna o Bitcoin resistente a computadores quânticos.

O objetivo é bem mais básico: criar uma definição determinística para algo que diferentes softwares precisarão responder da mesma forma.

Se no futuro uma carteira precisar avisar:

```
Esta moeda utiliza uma chave pública
que já foi exposta na blockchain.
```

ou recomendar que determinados UTXOs sejam migrados para um novo tipo de output, primeiro precisamos concordar sobre **quais moedas realmente estão nessa situação**.

Antes de discutir como proteger bitcoins de uma ameaça quântica futura, portanto, existe uma pergunta bem mais simples a responder: **a chave pública desses bitcoins já está disponível hoje?**

por: Rafael Penna
