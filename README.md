# Termômetro da Polarização

Este repositório é um projeto que acompanha a polarização política na Câmara dos Deputados a partir de votos nominais.  
A ideia é medir comportamento real de votação, transformar isso em rede e disponibilizar os resultados em API, dashboard e grafo interativo.

Artigo: [Quantificando Polarização, Coesão e Permeabilidade na Câmara dos Deputados do Brasil (WebMedia 2025)](https://sol.sbc.org.br/index.php/webmedia/article/view/37984).

## Metodologia

- Cada deputado é um nó da rede.
- Para cada par de deputados:
  - se votam igual, a conexão soma `+1`;
  - se votam diferente, a conexão soma `-1`.
- Com o acúmulo das votações, surge uma rede com arestas positivas (concordância) e negativas (discordância).
- O pipeline aplica filtros e métricas para destacar estrutura política da rede, incluindo backbone, layout, PageRank e índice de polarização por triângulos de relação.

Em termos práticos: quanto mais a rede se organiza em blocos opostos e coesos, maior a polarização estrutural.

## Organização do projeto

- `services/`
  - `web`: frontend
  - `api`: API
  - `pipeline`: ingestão, transformação, construção dos grafos e cálculo das métricas
- `libs/`
  - `termopol_db`: camada de acesso ao banco (queries e repositórios)
- `ops/`
  - infraestrutura e operação (nginx, postgres, migrations e scripts de deploy)

## Subindo o projeto com Docker

Na raiz do repositório:

```bash
docker compose up -d --build
```

Principais serviços:

- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- Docs da API: `http://localhost:8000/docs`

Para parar:

```bash
docker compose down
```

## Variáveis essenciais no `.env`

```env
# Banco
POSTGRES_DB=termopol
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_PORT=5432
POSTGRES_HOST=...
POSTGRES_SCHEMA=termopol

PIPELINE_SCHEDULE_CRON="0 3 * * *"

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_FROM=email
SMTP_USER=email
SMTP_PASSWORD=password
PIPELINE_NOTIFY_EMAIL_TO=email
```

## Rodando o pipeline manualmente

```bash
python services/pipeline/run.py
```
