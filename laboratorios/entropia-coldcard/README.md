# Laboratório de redução de entropia — COLDCARD

Este laboratório acompanha o artigo **“A falha de entropia da COLDCARD: quando a aleatoriedade aparente engana”**.

O experimento usa um modelo sintético para demonstrar como saídas de 256 bits podem parecer estatisticamente aleatórias mesmo quando são derivadas de um espaço interno muito menor.

## Escopo e limitações

Este laboratório:

- não reproduz o gerador vulnerável da COLDCARD;
- não gera mnemônicos BIP39;
- não deriva chaves privadas ou públicas;
- não produz endereços Bitcoin;
- não consulta a blockchain;
- não procura seeds, carteiras ou fundos.

Todo o experimento trabalha apenas com bytes sintéticos.

## Arquivos

- `generate_datasets.py`: gera a referência uniforme e o conjunto com estado reduzido;
- `analyze_entropy.py`: calcula métricas estatísticas e colisões;
- `plot_results.py`: produz os gráficos comparativos;
- `compare_reports.py`: gera a tabela comparativa em Markdown;
- `run_lab.sh`: executa todas as etapas do laboratório;
- `requirements.txt`: lista as dependências Python.

## Requisitos

- Python 3;
- NumPy;
- Matplotlib.

## Preparação

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    chmod +x run_lab.sh

## Execução

Exemplo com 20 bits e 50 mil amostras:

    SAMPLES=50000 STATE_BITS=20 ./run_lab.sh

Exemplo com 24 bits e 1 milhão de amostras:

    SAMPLES=1000000 STATE_BITS=24 ./run_lab.sh

Exemplo com 32 bits e 1 milhão de amostras:

    SAMPLES=1000000 STATE_BITS=32 ./run_lab.sh

## Resultados publicados

| Estado interno | Amostras | Pares de colisão observados | Bits estimados |
|---:|---:|---:|---:|
| 8 bits | 50.000 | 4.883.771 | 8,00 |
| 16 bits | 50.000 | 19.159 | 15,99 |
| 20 bits | 50.000 | 1.180 | 20,01 |
| 24 bits | 1.000.000 | 29.972 | 23,9918 |
| 32 bits | 1.000.000 | 113 | 32,043 |
| 40 bits | 1.000.000 | 1 | inconclusivo |

Um mesmo valor que aparece várias vezes pode formar vários pares de colisão. Por isso, a quantidade de pares pode ser maior que o número de amostras.

O caso de 40 bits é inconclusivo porque uma única colisão não permite estimar o espaço com estabilidade.

## Conclusão

O tamanho da saída não determina o tamanho do espaço que realmente a gerou. Saídas de 256 bits podem passar em testes estatísticos básicos e ainda ter sido derivadas de um estado interno muito menor.
