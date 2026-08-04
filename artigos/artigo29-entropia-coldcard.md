# A falha de entropia da COLDCARD: quando a aleatoriedade aparente engana

Em 30 de julho de 2026, a Coinkite publicou o alerta de segurança “Mk3 Security Advisory”, atualizado no dia seguinte. O aviso informa que seeds geradas em dispositivos COLDCARD Mk3 com firmware entre as versões 4.0.1 e 4.1.9 podem estar em risco.

Em uma migração realizada em 2021, o código de geração de seeds passou de `ckcc.rng_bytes()` para `ngu.random.bytes()`. A intenção era continuar usando o gerador aleatório de hardware da COLDCARD, mas, devido à forma como as implementações foram integradas e resolvidas durante a compilação, essa chamada acabou alcançando o PRNG de fallback do MicroPython.

Na prática, o código do gerador de hardware continuava presente no firmware, mas aquela chamada não chegava até ele no caminho de geração da seed. Na Mk3, o PRNG efetivamente utilizado era alimentado principalmente por estados do dispositivo e informações de temporização, o que levou a Coinkite a estimar preliminarmente um espaço efetivo de aproximadamente 40 bits. Nos modelos Mk4, Mk5 e Q, valores adicionais dos secure elements foram misturados ao estado do gerador, elevando a estimativa para cerca de 72 bits.

Este artigo não tenta reproduzir a implementação vulnerável da COLDCARD. Em vez disso, usamos um modelo sintético para demonstrar como uma saída pode parecer perfeitamente aleatória mesmo quando foi produzida a partir de um espaço interno muito menor do que o esperado.

Antes de continuar, é importante deixar muito claro:

> O nosso laboratório mede o tamanho de um espaço sintético por meio de colisões. Ele não simula busca por seeds, endereços ou fundos.
> 

O laboratório também não:

- gera palavras BIP39;
- deriva chaves privadas;
- deriva chaves públicas;
- produz endereços Bitcoin;
- consulta a blockchain;
- verifica saldos;
- procura carteiras existentes;
- tenta recuperar fundos.

Todo o experimento trabalha apenas com bytes sintéticos, sem qualquer relação com carteiras reais.

### O que significa ter 128 bits de entropia?

Uma seed BIP39 de 12 palavras é formada a partir de:

- 128 bits de entropia;
- 4 bits de checksum;
- total de 132 bits;
- divididos em 12 grupos de 11 bits.

Isso permite, em condições ideais, um espaço de $2^{128}$ possibilidades.

Esse número não vem da quantidade de caracteres exibidos nem da aparência das palavras. Ele depende da quantidade de estados internos que o gerador realmente consegue produzir.

Um sistema pode apresentar uma saída longa e aparentemente aleatória, mas ter começado com muito menos informação.

### Quando 256 bits não significam 256 bits

Para entender o que significa um espaço interno reduzido, imagine um gerador que possua apenas **4 bits de informação interna**.

Quatro bits permitem representar somente 16 valores diferentes:

$$
2^4 = 16
$$

É como lançar um dado de 16 faces. A cada geração, o sistema escolhe apenas um entre 16 resultados possíveis.

Agora imagine que o sistema passe o resultado desse dado pelo SHA-256. Uma das saídas poderia ser:

```
8da3f925b53c9090c152bb967996d0af...
```

O resultado possui 256 bits e, olhando apenas para ele, parece completamente aleatório.

Porém, o SHA-256 recebeu como entrada somente um dos 16 valores possíveis. Isso significa que o sistema continuará sendo capaz de produzir apenas **16 hashes diferentes**.

Podemos imaginar o processo assim:

```
Estado 0  → SHA-256 → saída de 256 bits A
Estado 1  → SHA-256 → saída de 256 bits B
Estado 2  → SHA-256 → saída de 256 bits C
...
Estado 15 → SHA-256 → saída de 256 bits P
```

As saídas são longas e visualmente diferentes, mas todas vêm de um conjunto de apenas 16 possibilidades.

Portanto:

```
Tamanho de cada saída: 256 bits
Quantidade de saídas possíveis: 16
Entropia real do gerador: 4 bits
```

O SHA-256 não cria entropia nova. Ele apenas transforma e espalha a informação que recebeu.

No nosso laboratório usamos espaços maiores. Com um estado interno de 20 bits, por exemplo, o sistema pode escolher entre $2^{20} = 1.048.576$ valores. Depois de passar cada valor pelo SHA-256, as saídas continuam tendo 256 bits, mas ainda existem somente cerca de 1 milhão de resultados possíveis e não $2^{256}$.

### Como funciona o laboratório

O laboratório gera dois conjuntos de dados.

**Referência uniforme**

O primeiro conjunto contém amostras sintéticas uniformes de 32 bytes. Ele funciona como grupo de controle.

**Estado interno reduzido**

O segundo conjunto começa com um estado interno de tamanho configurável:

```
8 bits
16 bits
20 bits
24 bits
32 bits
40 bits
```

Esse estado é expandido para uma saída de 32 bytes usando SHA-256 com separação de domínio. A saída possui 256 bits, mas a quantidade máxima de resultados possíveis continua limitada pelo estado inicial.

Por exemplo, no teste de 24 bits existem apenas 

$2^{24} = 16.777.216$

estados possíveis.

É importante reforçar que essa construção não corresponde ao algoritmo da COLDCARD. Ela é apenas um modelo controlado no qual conhecemos antecipadamente o tamanho do espaço e podemos verificar se as métricas conseguem recuperá-lo.

### O que analisamos

Para comparar os dois conjuntos, o laboratório observa diferentes sinais de aleatoriedade.

A **entropia de Shannon** mede o quanto os valores dos bytes estão distribuídos. Se alguns valores aparecem muito mais do que outros, a entropia diminui. Uma saída bem distribuída tende a ficar próxima do máximo de 8 bits por byte.

A **proporção de zeros e uns** verifica se aproximadamente metade dos bits é `0` e metade é `1`. O **teste monobit** transforma esse equilíbrio em uma medida numérica, ajudando a identificar desvios grandes.

A **correlação serial** procura dependência entre bytes vizinhos. Em uma sequência aleatória, conhecer um byte não deveria ajudar a prever o próximo.

A **compressibilidade** verifica se os dados contêm padrões ou repetições que permitam reduzir seu tamanho. Dados realmente aleatórios costumam ser pouco compressíveis.

A **distância de Hamming** conta quantos bits mudam de uma amostra para outra. Entre duas saídas independentes de 256 bits, esperamos, em média, que aproximadamente metade dos bits seja diferente.

Esses testes ajudam a responder:

> As saídas parecem aleatórias quando observamos seus bits e bytes?
> 

O laboratório também conta:

- quantas amostras diferentes foram geradas;
- quantas apareceram mais de uma vez;
- quantos pares de colisão ocorreram.

Uma **colisão** acontece quando duas gerações independentes produzem exatamente a mesma saída.

A partir da frequência dessas colisões, podemos estimar o tamanho do espaço de onde as saídas vieram.

Essa segunda parte responde a uma pergunta diferente:

> Mesmo que as saídas pareçam aleatórias, quantos resultados distintos esse gerador parece realmente ser capaz de produzir?
> 

Essa distinção é central para o experimento: uma saída pode parecer aleatória nos testes básicos e, ainda assim, pertencer a um espaço interno muito menor do que seu tamanho sugere.

### Medindo o espaço por colisões

Se um gerador tiver poucos resultados possíveis, repetições começarão a aparecer mais cedo. Se o espaço for muito grande, será necessário gerar muito mais amostras até que duas delas coincidam.

É a mesma ideia do paradoxo do aniversário: em um grupo de pessoas, não precisamos testar todas as datas do calendário para que duas pessoas provavelmente façam aniversário no mesmo dia.

No laboratório, geramos $n$ amostras e contamos quantas vezes duas gerações produziram exatamente a mesma saída. Cada par igual é chamado de **par de colisão**.

Se o gerador possuir um espaço uniforme de $2^b$ possibilidades, a quantidade esperada de pares de colisão é aproximadamente:

$E[C] \approx \frac{n(n-1)}{2 \cdot 2^b}$

Nessa expressão:

- $n$ é a quantidade de amostras geradas;
- $b$ é o tamanho do espaço em bits;
- $E[C]$ é a quantidade de colisões que esperamos observar.

A relação é simples: **quanto menor o espaço, mais colisões aparecem**.

Também podemos fazer o caminho inverso. Depois de gerar as amostras e observar $C$ pares de colisão, estimamos o tamanho do espaço com:

$\hat{b} = \log_2\left(\frac{n(n-1)}{2C}\right)$

Aqui, $\hat{b}$ representa o tamanho estimado do espaço em bits.

Se o resultado for próximo de 24, por exemplo, isso significa que as colisões observadas são compatíveis com um gerador que produz aproximadamente $2^{24}$ resultados diferentes.

Essa estimativa não revela quais estados internos foram usados e não permite reconstruir nenhuma entrada. Ela responde apenas:

> Pelo ritmo com que as repetições apareceram, qual parece ser o tamanho do espaço de resultados desse gerador?
> 

No nosso laboratório, os estados são escolhidos uniformemente, por isso essa conta funciona de forma direta. Em um gerador real, com valores mais prováveis do que outros ou dependências entre gerações, seria necessária uma análise adicional.

### Resultados do laboratório

Antes de analisar os números, vale recapitular o experimento.

Para cada tamanho de estado interno, geramos dois conjuntos de saídas de 32 bytes (256 bits):

1. uma **referência uniforme**, usada como grupo de controle, com saídas de 256 bits distribuídas de forma aproximadamente uniforme;
2. um conjunto de **estado reduzido**, no qual cada saída de 256 bits foi produzida a partir de apenas 8, 16, 20, 24, 32 ou 40 bits internos.

Nos dois casos, as amostras finais tinham exatamente o mesmo tamanho. A diferença era a quantidade de resultados que o gerador realmente poderia produzir.

Nos espaços menores, executamos 50 mil gerações. Para 24, 32 e 40 bits, aumentamos a coleta para 1 milhão de amostras, pois colisões se tornam progressivamente mais raras conforme o espaço cresce.

Os scripts usados para gerar os conjuntos, calcular as métricas e produzir os gráficos estão disponíveis no GitHub do Bitcoin Coders ([https://github.com/Bitcoin-Coders/bitcoin-coders/tree/main/laboratorios/entropia-coldcard](https://github.com/Bitcoin-Coders/bitcoin-coders/tree/main/laboratorios/entropia-coldcard)).

A tabela abaixo compara:

- o tamanho interno configurado;
- a quantidade de amostras geradas;
- o número de colisões previsto matematicamente;
- o número efetivamente encontrado;
- o tamanho do espaço estimado a partir dessas colisões.

| Estado configurado | Amostras | Pares de colisão  esperadas | Pares de colisão observados | Bits estimados |
| --- | --- | --- | --- | --- |
| 8 bits | 50.000 | 4.882.715 | 4.883.771 | 8,00 |
| 16 bits | 50.000 | 19.073 | 19.159 | 15,99 |
| 20 bits | 50.000 | 1.192 | 1.180 | 20,01 |
| 24 bits | 1.000.000 | 29.802 | 29.972 | 23,9918 |
| 32 bits | 1.000.000 | 116,42 | 113 | 32,043 |
| 40 bits | 1.000.000 | 0,455 | 1 | inconclusivo |

Um mesmo valor que aparece várias vezes pode formar vários pares de colisão. Por exemplo, se uma saída aparecer três vezes, ela produzirá três pares: primeira com segunda, primeira com terceira e segunda com terceira. Por isso, a quantidade de pares de colisão pode ser maior que o número de amostras.

![**Figura 1 – Comparação consolidada dos resultados finais do laboratório sintético.** As colisões observadas acompanham de perto a previsão matemática e permitem recuperar o tamanho efetivo do espaço enquanto há colisões suficientes. Foram usadas 50 mil amostras nos ensaios de 8, 16 e 20 bits e 1 milhão nos ensaios de 24, 32 e 40 bits.](A%20falha%20de%20entropia%20da%20COLDCARD%20quando%20a%20aleatorie/combined_comparison_final.png)

**Figura 1 – Comparação consolidada dos resultados finais do laboratório sintético.** As colisões observadas acompanham de perto a previsão matemática e permitem recuperar o tamanho efetivo do espaço enquanto há colisões suficientes. Foram usadas 50 mil amostras nos ensaios de 8, 16 e 20 bits e 1 milhão nos ensaios de 24, 32 e 40 bits.

Entre 8 e 32 bits, a quantidade observada de colisões ficou muito próxima da previsão matemática.

No experimento de 24 bits, por exemplo, o gerador poderia produzir $2^{24}$ saídas diferentes. Depois de 1 milhão de gerações, esperávamos aproximadamente 29.802 pares de colisão e encontramos 29.972.

A partir desse resultado, o laboratório estimou um espaço de:

```
23,9918 bits
```

Ou seja, recuperou quase exatamente os 24 bits usados na configuração.

O mesmo aconteceu no ensaio de 32 bits. Esperávamos aproximadamente 116 colisões, observamos 113 e obtivemos a estimativa:

```
32,043 bits
```

Isso mostra que, quando há colisões suficientes, é possível estimar com boa precisão o tamanho do espaço escondido por trás das saídas de 256 bits.

O caso de 40 bits foi diferente. Em 1 milhão de amostras, a previsão era de apenas 0,455 colisão e encontramos uma. Como uma única ocorrência é insuficiente para uma estimativa estável, classificamos esse resultado como inconclusivo.

Esse último teste também é importante: ele mostra que a ausência, ou a presença de apenas uma colisão, não comprova que o espaço seja seguro. Pode significar apenas que ainda não foram geradas amostras suficientes para medi-lo.

### A saída parecia perfeitamente aleatória

O aspecto mais interessante do resultado é que as verificações estatísticas básicas praticamente não revelaram a redução do espaço.

No ensaio de 24 bits com 1 milhão de amostras, obtivemos:

| Métrica | Referência uniforme | Estado reduzido |
| --- | --- | --- |
| Shannon por byte | 7,999993 | 7,999994 |
| Proporção de bits 1 | 0,500031 | 0,499986 |
| Correlação serial | 0,000065 | 0,000129 |
| Razão de compressão | 1,000305 | 1,000305 |
| Distância de Hamming média | 127,999 | 128,005 |
| Pares de colisão | 0 | 29.972 |

![**Figura 2 – Comparação entre a referência uniforme e o modelo com estado interno de 24 bits após 1 milhão de gerações.** O equilíbrio dos bits e a distância de Hamming são praticamente indistinguíveis, mas o conjunto de estado reduzido apresenta 29.371 observações duplicadas.](A%20falha%20de%20entropia%20da%20COLDCARD%20quando%20a%20aleatorie/entropy_comparison.png)

**Figura 2 – Comparação entre a referência uniforme e o modelo com estado interno de 24 bits após 1 milhão de gerações.** O equilíbrio dos bits e a distância de Hamming são praticamente indistinguíveis, mas o conjunto de estado reduzido apresenta 29.371 observações duplicadas.

A diferença entre os números da tabela e da figura é normal:

- **29.371 observações duplicadas**: quantidade de gerações além da primeira ocorrência de cada valor;
- **29.972 pares de colisão**: quantidade total de pares iguais, considerando também os valores que apareceram mais de duas vezes.

A entropia de Shannon por byte estava praticamente no valor máximo. A proporção entre zeros e uns estava praticamente equilibrada. A correlação serial estava próxima de zero. A compressão não encontrou redundância aproveitável. A distância de Hamming ficou próxima dos 128 bits esperados entre duas sequências aleatórias de 256 bits.

Essas métricas permaneceram próximas dos valores esperados porque o SHA-256 espalha pequenas diferenças na entrada por toda a saída. Mesmo quando o estado interno pertence a um espaço reduzido, os hashes resultantes tendem a apresentar bytes bem distribuídos, proporção equilibrada de zeros e uns, pouca correlação e grande distância de Hamming entre si. Isso faz com que as saídas pareçam aleatórias quando observadas localmente.

No entanto, o SHA-256 não aumenta a quantidade de entropia nem cria novas possibilidades. Se a entrada puder assumir apenas $2^{24}$ valores, continuarão existindo no máximo $2^{24}$ saídas distintas, embora cada uma tenha 256 bits e pareça aleatória. Por isso, as verificações aplicadas aos bits e bytes não revelaram a redução do espaço, enquanto a contagem de colisões permitiu detectá-la.

Esse é o ponto central do experimento:

> Uma saída pode parecer normal em verificações estatísticas básicas e ainda ter sido produzida por um espaço interno perigosamente pequeno.
> 

### O que aconteceu no teste de 40 bits?

Com 1 milhão de amostras em um espaço de ($2^{40}$), a quantidade esperada de colisões é apenas $0{,}455$. Observamos uma única colisão.

Se aplicássemos diretamente a fórmula, obteríamos uma estimativa próxima de 38,86 bits. No entanto, essa estimativa não é confiável.

Com tão poucos eventos:

- zero colisões não permitiria calcular valor algum;
- uma colisão produz uma estimativa;
- duas colisões mudariam o resultado em aproximadamente um bit;
- pequenas variações aleatórias alterariam completamente a conclusão.

Por isso classificamos o ensaio de 40 bits como inconclusivo.

Ele demonstra o limite do método:

> A ausência de colisões não prova que a entropia seja suficiente. Pode significar apenas que a amostra é pequena demais em relação ao espaço analisado.
> 

Para obter aproximadamente 100 colisões em um espaço de 40 bits, seriam necessárias cerca de 15 milhões de amostras.

### Qual é a relação entre o teste de 40 bits e a Mk3?

Existe uma relação numérica, mas não uma reprodução experimental.

A análise preliminar da Coinkite estima que o espaço efetivo da Mk3 afetada seja de aproximadamente 40 bits. No nosso laboratório, também configuramos um espaço de 40 bits, mas o modelo é completamente diferente: partimos de $2^{40}$ estados uniformemente distribuídos e expandimos cada um deles com SHA-256.

O gerador real da Mk3 utilizava um PRNG alimentado principalmente por estados do dispositivo e informações de temporização. Essa distribuição pode conter vieses e dependências que não existem no nosso modelo sintético.

Portanto, a única colisão observada em 1 milhão de amostras não mede nem confirma a entropia da Mk3. O teste demonstra apenas que, mesmo em um espaço uniforme de 40 bits, 1 milhão de amostras é insuficiente para estimar seu tamanho com precisão por meio de colisões.

O ensaio de 40 bits deve ser interpretado como uma ilustração da escala envolvida, e não como uma reconstrução da vulnerabilidade ou uma estimativa do custo de um ataque.

### E os 72 bits informados para Mk4, Mk5 e Q?

Com 1 milhão de amostras em um espaço de ($2^{72}$), a quantidade esperada de colisões seria:

$\frac{10^6(10^6-1)}{2 \cdot 2^{72}} \approx 1{,}06 \times 10^{-10}$

Na prática, observaríamos zero colisões.

Para esperar apenas uma colisão seriam necessárias aproximadamente:

```
97 bilhões de amostras
```

Com 32 bytes por amostra, somente os dados brutos ocupariam aproximadamente:

```
3,1 TB
```

Para esperar cerca de 100 colisões e obter uma estimativa mais estável seriam necessárias aproximadamente:

```
972 bilhões de amostras
```

Ou mais de:

```
31 TB de dados brutos
```

Por isso não tentamos reproduzir diretamente um espaço de 72 bits. Os espaços menores usados no laboratório tornam o mesmo princípio estatístico observável com recursos comuns.

### Colisões não são busca por seeds

O paradoxo do aniversário indica que colisões começam a aparecer depois de aproximadamente $2^{b/2}$ amostras.

Isso não significa que seja possível encontrar um estado específico com ($2^{b/2}$) tentativas. São dois problemas diferentes.

**Encontrar qualquer colisão**

Queremos encontrar duas saídas iguais dentro de um conjunto. Aproximadamente $2^{b/2}$ amostras podem ser suficientes.

**Encontrar uma seed específica**

Queremos encontrar um único estado previamente determinado. Nesse caso, o trabalho pode chegar a $2^b$ tentativas. Portanto, observar colisões em um espaço de 72 bits não equivale a procurar uma seed específica de 72 bits.

Nosso laboratório realiza somente análise estatística de colisões. Ele não implementa nenhuma forma de busca por carteiras.

### Reproduzindo o experimento

Os scripts geram os conjuntos sintéticos, executam as análises e produzem relatórios e gráficos.

Primeiro, criamos o ambiente:

```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
chmod +x run_lab.sh
```

Para executar o ensaio de 20 bits com 50 mil amostras:

```bash
SAMPLES=50000 STATE_BITS=20 ./run_lab.sh
```

Para executar o ensaio de 24 bits com 1 milhão de amostras:

```bash
SAMPLES=1000000 STATE_BITS=24 ./run_lab.sh
```

Para executar o ensaio de 32 bits:

```bash
SAMPLES=1000000 STATE_BITS=32 ./run_lab.sh
```

Os resultados incluem:

- arquivos binários com as amostras;
- relatórios JSON;
- tabela Markdown;
- gráficos comparativos;
- quantidade de colisões;
- estimativa do tamanho efetivo do espaço.

Nenhum dos scripts importa bibliotecas BIP39, BIP32 ou secp256k1. Nenhum deles possui código para geração de endereços ou comunicação com serviços Bitcoin.

### O que usuários de COLDCARD devem fazer?

Este laboratório é educacional e não substitui as orientações do fabricante.

Segundo o pronunciamento oficial:

- versões corrigidas de firmware já estão disponíveis para os modelos afetados;
- atualizar o firmware corrige novas gerações;
- atualizar não repara uma seed criada anteriormente;
- usuários afetados devem seguir cuidadosamente o procedimento oficial de migração;

Segundo o alerta oficial, antes de gerar uma nova seed é necessário instalar uma versão corrigida: Mk3 4.2.0 ou posterior; Mk4/Mk5 Standard 5.6.0 ou posterior; Q Standard 1.5.0Q ou posterior; Mk4/Mk5 Edge 6.6.0X ou posterior; e Q Edge 6.6.0QX ou posterior.

A atualização corrige novas gerações, mas não repara uma seed criada anteriormente. A exceção descrita pela Coinkite se aplica a usuários que adicionaram pelo menos 50 lançamentos justos, independentes e privados de um dado físico durante a criação da seed. Em caso de dúvida, deve-se seguir o procedimento oficial de migração.

Antes de tomar qualquer decisão, consulte diretamente o alerta oficial e confirme a versão e o canal de firmware usado pelo dispositivo.

### Conclusão

A aparência aleatória de uma saída não demonstra, por si só, que ela foi produzida por uma fonte de entropia adequada.

No nosso laboratório, saídas de 256 bits geradas a partir de apenas 24 ou 32 bits internos apresentaram:

- entropia de Shannon próxima do máximo;
- proporção equilibrada de zeros e uns;
- correlação próxima de zero;
- nenhuma compressibilidade relevante;
- distância de Hamming compatível com aleatoriedade.

Mesmo assim, as colisões revelaram corretamente o tamanho reduzido do espaço.

**Resumindo, o ponto principal dos nossos testes é o seguinte.** Quando geramos 1.000.000 de saídas de 256 bits na referência uniforme, não encontramos nenhuma repetição completa, o que é o esperado, já que o espaço de possibilidades é gigantesco ($2^{256}$).

Já no experimento com estado interno de 24 bits, continuamos produzindo saídas finais de 256 bits, mas agora todas elas vêm de um espaço de apenas $2^{24} = 16.777.216$ possibilidades. Nesse caso, ao gerar 1.000.000 de amostras, começamos a observar repetições: o conjunto apresentou 29.371 observações duplicadas e 29.972 pares de colisão.

Em outras palavras, a aparência de 256 bits na saída não garante, por si só, que o gerador esteja explorando um espaço realmente compatível com $2^{256}$ possibilidades. Uma saída pode parecer perfeitamente aleatória e, ainda assim, ter sido produzida a partir de um espaço interno muito menor.

O experimento não reproduz a falha da COLDCARD, não mede nem valida a estimativa preliminar de aproximadamente 40 bits para a Mk3 e não realiza qualquer busca por seeds, chaves, endereços ou fundos.

O caso da COLDCARD mostra por que a qualidade do processo de geração é tão importante quanto o formato final da seed e por que testes superficiais podem não revelar uma redução grave no espaço de possibilidades.

### Referências

- Coinkite — **Mk3 Security Advisory:** [https://blog.coinkite.com/coldcard-mk3-seed-generation-warning/](https://blog.coinkite.com/coldcard-mk3-seed-generation-warning/)
- Coinkite — **Technical Deep Dive into the Entropy Issue:**
    
    [https://blog.coinkite.com/entropy-technical-backgrounder/](https://blog.coinkite.com/entropy-technical-backgrounder/)
    
- Bitcoin Coders — código-fonte e resultados do laboratório:
    
    [https://github.com/Bitcoin-Coders/bitcoin-coders](https://github.com/Bitcoin-Coders/bitcoin-coders)
    

![IMG-20250722-WA0010.jpg](A%20falha%20de%20entropia%20da%20COLDCARD%20quando%20a%20aleatorie/7d12c3ef-1d0d-4c45-8cf9-96c904b1cb21.png)

Escrito por:  

Rafael Penna
