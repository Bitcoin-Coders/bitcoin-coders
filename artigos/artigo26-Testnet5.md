# Por que já estão discutindo uma Testnet5 para o Bitcoin?

Em junho de 2026, uma proposta apareceu na Bitcoin Development Mailing List: a criação de uma nova rede de testes chamada Testnet5.

A ideia chamou atenção porque a Testnet4 foi lançada há apenas dois anos. Em um primeiro momento, pode parecer exagero substituir uma rede tão recente. No entanto, a discussão rapidamente revelou problemas que vão muito além de uma simples atualização de parâmetros. Questões envolvendo mineração, ajuste de dificuldade, estabilidade da rede e até o valor econômico das moedas de teste entraram no debate.

Para entender por que alguns desenvolvedores já defendem uma nova testnet, precisamos primeiro entender os problemas com a atual.

### O papel de uma testnet

A maioria dos desenvolvedores começa sua jornada no Bitcoin utilizando Regtest, Signet ou Testnet. A Regtest permite criar uma blockchain privada e totalmente controlada localmente. O desenvolvedor pode minerar blocos instantaneamente, criar moedas sempre que desejar e reproduzir cenários específicos sem depender de outros participantes.

A Signet ocupa uma posição intermediária. Ela é uma rede pública, acessível pela internet, mas com um conjunto controlado de assinantes responsáveis pela produção dos blocos. Isso resulta em um ambiente mais previsível e estável para testes.

Já a Testnet busca reproduzir de forma mais fiel o comportamento da rede principal. Qualquer pessoa pode executar um node, minerar blocos e participar da rede. Transações são propagadas entre participantes reais e a blockchain evolui de forma descentralizada, de maneira semelhante ao que acontece na mainnet.

A ideia é simples: oferecer um ambiente parecido com o Bitcoin real sem exigir bitcoins reais. Na prática, porém, criar uma cópia funcional da rede Bitcoin é mais difícil do que parece. Foi justamente essa dificuldade que motivou a recente discussão sobre a criação de uma Testnet5.

### **O problema da Testnet4**

Grande parte da discussão sobre a Testnet5 surgiu por causa de uma característica herdada das versões anteriores da rede de testes.

Na Testnet4 existe uma regra especial para evitar que a blockchain fique parada por muito tempo. Caso nenhum bloco seja encontrado durante vinte minutos, o próximo bloco pode ser minerado com dificuldade mínima.

A motivação é compreensível. Como a testnet possui muito menos hashpower do que a mainnet, existe o risco de períodos prolongados sem mineração. A regra foi criada justamente para evitar que desenvolvedores fiquem esperando horas ou dias pela confirmação de uma transação.

O problema é que essa solução acabou produzindo efeitos colaterais.

Segundo Antoine Poinsot, um dos participantes da discussão, a Testnet4 tornou-se altamente instável devido à exploração dessa exceção de dificuldade. Em vez de simplesmente evitar travamentos, a regra passou a facilitar a criação de cadeias concorrentes e reorganizações frequentes, afastando a rede do comportamento observado na mainnet.

Em outras palavras, a rede criada para simular o Bitcoin começou a se comportar de forma cada vez menos parecida com o Bitcoin real.

### A proposta da Testnet5

Foi nesse contexto que Pol Espinasa apresentou o rascunho de uma nova BIP propondo a criação da Testnet5. A principal mudança é justamente remover a regra especial de dificuldade mínima.

A proposta busca criar uma rede cujo comportamento seja mais próximo da mainnet, mesmo que isso signifique aceitar o risco de períodos temporários de baixa atividade quando houver poucos mineradores participando.

Outro objetivo importante é transformar a nova testnet em um ambiente adequado para experimentação da BIP54. Essa proposta, discutida separadamente pelos desenvolvedores do Bitcoin, reúne diversas limpezas e correções de consenso acumuladas ao longo dos anos. Como suas mudanças afetam diretamente a mineração e a validação de blocos, os autores da Testnet5 defendem que elas sejam testadas em uma rede pública antes de qualquer adoção mais ampla.

A ideia central é simples: menos exceções e mais fidelidade ao comportamento real do Bitcoin.

### Um problema que talvez não tenha solução

Embora a discussão tenha começado por questões técnicas, um dos pontos mais interessantes foi levantado por um dos participantes. Ele chamou atenção para um problema que não depende das regras de consenso. Mesmo que a Testnet5 funcione perfeitamente, o que impede que suas moedas adquiram valor econômico?

Historicamente, toda vez que uma rede de testes se torna útil e amplamente utilizada, suas moedas passam a ser demandadas por desenvolvedores. E quando existe demanda, inevitavelmente surge um mercado.

Hoje não é difícil encontrar pessoas trocando moedas de testnet ou signet por bitcoins reais. Não existe qualquer garantia de que isso não aconteça novamente.

A observação é particularmente interessante porque mostra que algumas características do dinheiro surgem naturalmente. Mesmo quando uma moeda é criada explicitamente para não ter valor, ela pode acabar adquirindo utilidade suficiente para que pessoas estejam dispostas a pagar por ela.

### O risco de um premine sem premine

Outro momento marcante da discussão ocorreu quando outro participante analisou os parâmetros iniciais da proposta. Embora o texto previsse uma rede sem premine, ele observou que isso não significava necessariamente uma distribuição equilibrada das moedas.

Se a dificuldade inicial fosse muito baixa, um único ASIC moderno poderia minerar dezenas de milhares de blocos logo após o lançamento da rede. Antes mesmo que o mecanismo de ajuste de dificuldade tivesse tempo de reagir, uma enorme quantidade de moedas já estaria concentrada nas mãos dos primeiros participantes.

O resultado seria algo muito próximo de um premine, ainda que nenhum premine tivesse sido planejado. Para evitar esse cenário, foi sugerido aumentar significativamente a dificuldade inicial da rede.

### O Bitcoin funcionando como foi projetado

Talvez a parte mais interessante da discussão seja o que aconteceu depois. Poucos dias após as mensagens iniciais, um dos proponentes respondeu à discussão informando que o rascunho da proposta havia sido atualizado. Entre as alterações estava justamente o aumento da dificuldade inicial, incorporando uma das principais críticas apresentadas pela comunidade.

Esse episódio ilustra perfeitamente como o desenvolvimento do Bitcoin acontece. Não existe uma empresa decidindo unilateralmente quais mudanças serão adotadas. As propostas são publicadas, discutidas, criticadas e revisadas em público. Muitas vezes a versão final de uma ideia acaba sendo bastante diferente da versão originalmente apresentada.

A discussão sobre a Testnet5 é mais um exemplo desse processo funcionando exatamente como deveria.

### Atualizações recentes

Enquanto este artigo era escrito, a proposta continuou evoluindo. Após as discussões iniciais na mailing list, o rascunho foi movido para o repositório de BIPs, onde segue recebendo comentários e revisões da comunidade.

Entre as alterações realizadas até o momento estão a correção de alguns detalhes relacionados à ativação da BIP54, ajustes na especificação do bloco gênese e o aumento da dificuldade inicial da rede, uma mudança motivada pelas preocupações levantadas sobre um possível "premine acidental".

Embora a proposta ainda não tenha sido aceita, a rápida incorporação de sugestões da comunidade mostra como o processo de desenvolvimento do Bitcoin ocorre de forma aberta e iterativa.

---

A proposta da Testnet5 ainda está em discussão e pode sofrer alterações antes de uma eventual implementação. Mesmo assim, a conversa já revelou algo importante: reproduzir o comportamento da mainnet em uma rede de testes é um desafio muito maior do que simplesmente copiar suas regras.

Incentivos econômicos, mineração, ajuste de dificuldade e distribuição de moedas continuam existindo, mesmo quando os bitcoins em questão deveriam servir apenas para testes. A própria discussão mostra que, em uma rede aberta, até mesmo as ferramentas criadas para desenvolvimento acabam enfrentando muitos dos mesmos problemas observados na rede principal.

---

### Apêndice — A proposta de BIP Testnet5

A proposta publicada por Pol Espinasa e Fabian Jahr ainda está em estágio de rascunho, mas já define os principais parâmetros da futura Testnet5.

O texto abaixo resume os principais pontos da versão 0.1.0 do rascunho publicado por Pol Espinasa e Fabian Jahr.

**Objetivo**

A Testnet5 tem como objetivo substituir a Testnet4.

Segundo os autores, a regra de exceção de dificuldade herdada das versões anteriores acabou sendo explorada de forma contínua, tornando a rede instável e difícil de utilizar para testes.

Além disso, a nova rede serviria como ambiente de experimentação para a BIP54.

**BIP54 ativa desde o início**

A proposta determina que todas as regras da BIP54 sejam aplicadas a partir do bloco 1 da rede.

Entre os objetivos da BIP54 estão:

- mitigar o ataque conhecido como Timewarp;
- reduzir o pior caso de tempo de validação de blocos;
- corrigir algumas fragilidades da árvore de Merkle;
- eliminar a necessidade de certas verificações históricas relacionadas a transações duplicadas.

**Sem exceção de dificuldade**

A principal mudança em relação à Testnet4 é a remoção completa da regra que permite minerar blocos com dificuldade mínima após longos períodos sem atividade.

Segundo os autores, qualquer exceção desse tipo acaba se tornando explorável por participantes maliciosos.

O objetivo é aproximar o comportamento da rede de testes ao comportamento da mainnet.

**Dificuldade inicial maior**

O limite máximo de Proof of Work foi definido como:

```
nBits = 0x1a0fffff
```

Isso corresponde aproximadamente a uma dificuldade mínima de 1 milhão.

A escolha busca evitar que um único minerador consiga produzir dezenas de milhares de blocos logo após o lançamento da rede.

**Novo bloco gênese**

A Testnet5 possuirá um bloco gênese próprio.

Uma das ideias propostas é utilizar o hash de um bloco recente da mainnet dentro da coinbase do bloco gênese.

Segundo os autores, isso produz dois efeitos:

- torna a saída comprovadamente impossível de gastar;
- funciona como um compromisso público contra qualquer premine.

No momento da publicação da proposta, os valores definitivos do bloco gênese ainda não haviam sido definidos.

**Novo magic value**

A proposta também define um novo identificador de rede.

O valor escolhido é:

```
0x46495645
```

Interpretado como ASCII, o valor corresponde à palavra:

```
FIVE
```

**Porta padrão**

A porta P2P padrão da Testnet5 será:

```
18335
```

**Compatibilidade**

A Testnet5 não será compatível com a Testnet3 nem com a Testnet4.

Além de utilizar um novo bloco gênese, ela adota as regras da BIP54 e remove a exceção de dificuldade existente nas versões anteriores.

Por esse motivo, softwares que desejarem suportar a nova rede precisarão adicionar explicitamente seus parâmetros e regras de consenso.

---

**Proposta completa:**

[https://github.com/fjahr/bips/blob/bip-t5-draft/bip-XXXX.md](https://github.com/fjahr/bips/blob/bip-t5-draft/bip-XXXX.md)

por: Rafael Santos
