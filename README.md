
# CLIMORORA
Plataforma de monitoramento meteorológico com dashboard, mapas, gráficos e um assistente de IA restrito ao domínio do clima
=======
# Climora

> Inteligência climática para o seu dia.

Plataforma de monitoramento meteorológico com dashboard, mapas, gráficos e um
assistente de IA restrito ao domínio do clima.

Consulte `ARCHITECTURE.md` para decisões de arquitetura, lições registradas e
roadmap, e `docs/API.md` para a referência completa da API.

## Estado atual

Projeto concluído: 14 etapas.

- Application factory com extensões, logging, CORS, rate limiting e JWT configurados
- Envelope de resposta padronizado e handlers globais de erro
- Seis entidades mapeadas com relacionamentos e exclusão em cascata
- Autenticação completa com JWT em cookies httpOnly e renovação transparente
- Providers meteorológicos atrás de interface, com DTOs normalizados e fallback
- Cache em memória com TTL por tipo de dado, pronto para migrar para Redis
- Dashboard com condições atuais, oito métricas, busca com autocomplete e geolocalização
- Favoritos com CRUD, unicidade por coordenada e rótulo personalizado
- Histórico paginado, com busca e deduplicação de consultas repetidas
- Mapa Leaflet com marcador de temperatura, tiles claros/escuros e recentragem animada
- Busca de cidades filtrada para lugares habitados, ignorando países e regiões
- Gráficos Chart.js de temperatura, chuva, vento, umidade, pressão e previsão semanal
- Faixa de previsão de 7 dias com ícones, máximas, mínimas e chance de chuva
- Insights do Dia por motor de regras determinístico, sem custo e sem alucinação
- Assistente restrito a clima, com três camadas de contenção e histórico de conversas
- Perfil com edição de nome, troca de senha, preferências e exclusão de conta em cascata
- Menu de conta com avatar, e avisos globais para sessão expirada, falha de rede e ações
- Error boundary, páginas de erro por rota e detecção de perda de conexão
- Preferências de unidade aplicadas em todo o painel, incluindo gráficos e mapa

### Endpoints disponíveis

| Método | Rota | Protegida |
|---|---|---|
| GET | `/api/v1/system/health` | não |
| POST | `/api/v1/auth/register` | não |
| POST | `/api/v1/auth/login` | não |
| POST | `/api/v1/auth/refresh` | refresh token |
| POST | `/api/v1/auth/logout` | opcional |
| GET | `/api/v1/auth/me` | sim |
| GET | `/api/v1/weather/search?q=` | sim |
| GET | `/api/v1/weather/reverse?lat=&lon=` | sim |
| GET | `/api/v1/weather/snapshot?lat=&lon=` | sim |
| GET | `/api/v1/weather/air-quality?lat=&lon=` | sim |
| GET | `/api/v1/favorites?q=` | sim |
| POST | `/api/v1/favorites` | sim |
| PATCH | `/api/v1/favorites/<id>` | sim |
| DELETE | `/api/v1/favorites/<id>` | sim |
| GET | `/api/v1/history?page=&per_page=&q=` | sim |
| POST | `/api/v1/history` | sim |
| DELETE | `/api/v1/history/<id>` | sim |
| DELETE | `/api/v1/history` | sim |
| GET | `/api/v1/insights?lat=&lon=` | sim |
| POST | `/api/v1/ai/chat` | sim |
| GET | `/api/v1/ai/conversations` | sim |
| GET | `/api/v1/ai/conversations/<id>/messages` | sim |
| DELETE | `/api/v1/ai/conversations/<id>` | sim |
| GET | `/api/v1/profile` | sim |
| PATCH | `/api/v1/profile` | sim |
| PUT | `/api/v1/profile/password` | sim |
| DELETE | `/api/v1/profile` | sim |
| GET | `/api/v1/profile/settings` | sim |
| PUT | `/api/v1/profile/settings` | sim |

## Requisitos

- Python 3.13+
- Node.js 20+

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

cp .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"   # gere SECRET_KEY e JWT_SECRET_KEY

python run.py
```

API disponível em `http://127.0.0.1:5000`.

Verificação:

```bash
curl http://127.0.0.1:5000/api/v1/system/health
```

### Migrations

Na primeira execução, crie o histórico e aplique o schema:

```bash
flask --app run.py db init
flask --app run.py db migrate -m "initial schema"
flask --app run.py db upgrade
```

Nas alterações seguintes, apenas `db migrate` e `db upgrade`. Sempre revise o
arquivo gerado em `migrations/versions/` antes de aplicar — o autogenerate
detecta colunas e índices, mas não adivinha renomeações.

### Testes e verificações

```bash
pytest
python tools/check_imports.py
```

O `check_imports.py` valida estaticamente que todo nome importado entre módulos
do projeto existe de fato na origem. Python só falha nisso quando a linha
executa, então um método renomeado pode passar pelo `py_compile` e quebrar em
produção.

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Verificação de imports entre módulos:

```bash
npm run check:imports
```

Interface disponível em `http://localhost:5173`. O Vite encaminha `/api` para o
backend, então não há configuração de CORS a fazer em desenvolvimento.

## Qualidade

```bash
cd backend
black . && isort . && ruff check .
```

## Estrutura

```text
climora/
├── backend/        # API Flask em camadas
├── frontend/       # SPA React + Vite
├── ARCHITECTURE.md
└── README.md
```
>>>>>>> e797aac (Adiciona projeto CLIMORA)
