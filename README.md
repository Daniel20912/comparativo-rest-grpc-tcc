# Análise Comparativa de Desempenho entre REST e gRPC em Microsserviços

Código-fonte, scripts de automação e dados do Trabalho de Conclusão de Curso (TCC) de Ciência da Computação da Universidade Regional Integrada do Alto Uruguai e das Missões (URI), Campus Santo Ângelo.

- **Autor:** Daniel Oliveira de Jesus
- **Orientador:** Alan Motta Schumacher
- **Ano:** 2026

## Sobre o estudo

A literatura sobre comunicação entre microsserviços costuma se basear em cenários de grande escala. Este trabalho avalia **REST (HTTP/1.1 + JSON)** e **gRPC (HTTP/2 + Protocol Buffers)** em um contexto de **recursos limitados**, típico de pequenas e médias empresas (PMEs).

Foram medidas quatro métricas quantitativas em operações CRUD, com análise estatística para verificar se as diferenças observadas são reais ou fruto de variação aleatória:

| Métrica | Fonte da medição |
|---|---|
| Uso de CPU | Spring Boot Actuator + Prometheus |
| Pico de memória (Heap total) | Spring Boot Actuator + Prometheus |
| Latência (tempo total de resposta) | Apache JMeter |
| Vazão (req/s) | Apache JMeter |

## Estrutura do repositório

```
.
├── codigo_fonte_apis/        # Microsserviço Java/Spring Boot em duas versões: REST e gRPC
├── planos_de_teste_jmeter/   # Planos de teste do Apache JMeter (carga sobre as APIs)
├── scripts_powershell/       # Orquestração dos testes e coleta de métricas
├── scripts_python/           # Extração, tratamento e análise estatística dos dados
└── resultados_csv/           # Dados brutos e consolidados das execuções
```

## Metodologia resumida

**Sistema avaliado.** Um microsserviço com operações CRUD sobre a entidade `Produto` (identificador, nome, categoria, preço, estoque, descrição e data de cadastro), implementado em duas versões funcionalmente idênticas (REST e gRPC). A lógica de negócio é a mesma, e a única variável experimental é o protocolo de comunicação. O repositório de dados é **em memória**, para isolar o custo do protocolo e eliminar a variabilidade de I/O de disco.

**Carga.** Apache JMeter com 100 threads, ramp-up de 20 segundos e 50 iterações por usuário, totalizando **5.000 requisições por bateria**. O valor foi dimensionado a partir do perfil de PMEs (entre 1.000 e 10.000 requisições diárias).

**Repetições.** **30 baterias independentes** por protocolo e por operação (Create, Read, Update, Delete). A cada bateria, a JVM é encerrada e a aplicação é reiniciada do zero, e a etapa seguinte só começa depois que o sistema operacional confirma que a porta foi liberada (8080 para REST, 9091 para gRPC).

**Tratamento dos dados.**
- Latência e vazão: descarte das 5 primeiras requisições de cada teste (filtro de *warm-up* da JVM), para refletir o estado estável.
- CPU: média calculada apenas durante a fase de carga, excluindo as fases de *baseline* e *cooldown*.
- Memória: pico máximo de alocação de Heap total ao longo do ciclo.

**Análise estatística** (α = 0,05, n = 30 por cenário): teste de normalidade de Shapiro-Wilk, seguido de teste t de Welch (dados normais) ou Mann-Whitney U (dados não normais).

## Resultados resumidos

Médias de 30 execuções por cenário. Valores em **negrito** indicam o menor consumo/latência ou a maior vazão com diferença estatisticamente significativa (p < 0,05). "Empate" indica diferença não significativa.

| Operação | CPU REST | CPU gRPC | Memória REST (MB) | Memória gRPC (MB) | Vazão REST (req/s) | Vazão gRPC (req/s) | Latência REST (ms) | Latência gRPC (ms) |
|---|---|---|---|---|---|---|---|---|
| Create | 5,44% | **4,61%** | 230,13 | **224,50** | 255,79 | **258,18** | **0,87** | 0,89 |
| Read | 4,34% | 4,37% (empate) | **193,23** | 223,90 | 255,43 | **258,00** | **0,72** | 0,85 |
| Update | 5,63% | **4,47%** | 237,33 | **223,67** | 256,43 | **258,32** | 0,88 (empate) | 0,88 (empate) |
| Delete | **3,65%** | 4,18% | **169,50** | 220,20 | 255,03 | **257,77** | **0,65** | 0,79 |

**Principais conclusões do estudo:**
- O gRPC teve menor uso de CPU e de memória em operações com payload (Create e Update).
- O REST consumiu menos CPU e memória em operações sem corpo de requisição (Read e Delete). O gRPC apresentou um "custo fixo" de cerca de 220 MB de Heap.
- O gRPC obteve maior vazão em todas as operações, mas a diferença absoluta foi pequena (cerca de 1%).
- Nas condições testadas, o REST apresentou o melhor custo-benefício para PMEs. O gRPC se destaca em cenários de alta ingestão de dados (telemetria, IoT).

Os detalhes, gráficos de variabilidade e a discussão completa estão no artigo.

## Limitações

- Execução em **localhost** e em um único hardware (Intel Core i5-10300H, 16 GB de RAM), sem latência real de rede.
- Repositório de dados em memória, sem os gargalos de um banco de dados real.
- Carga estática de 5.000 requisições e payloads uniformes, sem teste de estresse de longa duração.
- Um único framework (Spring Boot) e um único microsserviço, sem chamadas em cascata.
- Sem avaliação de autenticação, criptografia (mTLS) ou ajustes avançados de Garbage Collection.
- Como a carga é distribuída em um ramp-up fixo de 20 segundos, a vazão medida tende a ficar próxima de um mesmo patamar para ambos os protocolos. As diferenças de vazão devem ser interpretadas com esse cuidado.

## Ferramentas utilizadas

Java 25, Spring Boot 3.5.7, gRPC / Protocol Buffers, Apache JMeter, Spring Boot Actuator, Prometheus, PowerShell, Python (Pandas).

## Uso de inteligência artificial

Conforme declarado no artigo, a ferramenta Gemini foi utilizada para apoiar a organização de ideias, a revisão da redação e a estruturação dos scripts de automação em Python e PowerShell. A pesquisa bibliográfica, a concepção arquitetural, a execução dos testes e a interpretação dos dados são de autoria do autor.

## Como citar

> Jesus, D. O. de; Schumacher, A. M. (orient.). *Análise Comparativa de Desempenho entre REST e gRPC em Microsserviços*. Trabalho de Conclusão de Curso, Ciência da Computação, URI Santo Ângelo, 2026.

## Contato

Daniel Oliveira de Jesus: [LinkedIn](https://www.linkedin.com/in/daniel-oliveira-de-jesus) | [GitHub](https://github.com/Daniel20912)
