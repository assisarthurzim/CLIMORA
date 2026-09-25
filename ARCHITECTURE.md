# Climora — Documento de Arquitetura

> Inteligência Climática para o seu dia.

**Versão:** 1.1
**Status:** Etapas 1 a 14 concluídas

---

## 1. Visão geral

O Climora é uma aplicação web de monitoramento meteorológico composta por:

- **Backend**: API REST em Flask, arquitetura em camadas, SQLite via SQLAlchemy.
- **Frontend**: SPA em React + Vite, consumindo exclusivamente a API própria.
- **Integrações**: Open-Meteo (clima), Nominatim/OpenStreetMap (geocoding), OpenWeatherMap (complemento/fallback), provedor de LLM (assistente).

O frontend **nunca** chama APIs externas diretamente. Todo tráfego passa pelo backend, o que permite cache, normalização, rate limiting e proteção das chaves.

### Princípio central

> A regra de dependência aponta sempre para dentro: Rotas → Services → Repositories → Models. Nenhuma camada conhece quem está acima dela.

---

## 2. Decisões arquiteturais (ADR resumido)

### ADR-001 — Organização por domínio com camadas compartilhadas

**Contexto**: o briefing descreve simultaneamente módulos de domínio (`auth/`, `weather/`) e camadas técnicas globais (`routes/`, `services/`, `repositories/`), o que gera ambiguidade sobre onde cada arquivo mora.

**Opções**:

| Abordagem | Prós | Contras |
|---|---|---|
| Camadas técnicas globais | Familiar; fácil de localizar por tipo de arquivo | Uma feature se espalha por 5 pastas; acoplamento cresce sem sinal; difícil extrair módulo |
| Módulos por domínio | Alta coesão; mudança de feature toca uma pasta; extraível | Exige disciplina para não duplicar código transversal |

**Decisão**: híbrido. Cada domínio é um pacote autocontido com `routes.py`, `service.py`, `repository.py`, `schemas.py`. O que é transversal (`models/`, `utils/`, `middleware/`, `extensions.py`, `config.py`) permanece compartilhado.

**Justificativa para `models/` centralizado**: o SQLAlchemy usa um registro único de metadata. Modelos espalhados por pacotes causam falhas de resolução de relacionamento por ordem de import e quebram o autogenerate do Alembic.

---

### ADR-002 — Armazenamento do JWT em cookies httpOnly

**Opções**:

| Abordagem | Prós | Contras |
|---|---|---|
| localStorage | Trivial; cross-origin sem configuração | Legível por qualquer script: um XSS = sessão roubada |
| Cookie httpOnly | Inacessível a JavaScript; envio automático | Exige CSRF token e CORS com credentials |

**Decisão**: cookies `httpOnly` + `SameSite=Lax` + `Secure` em produção, com proteção CSRF double-submit (suporte nativo do Flask-JWT-Extended).

**Política de tokens**:

- Access token: 15 minutos.
- Refresh token: 7 dias — 30 dias quando "Lembrar-me" estiver marcado.
- Rotação do refresh a cada renovação.
- Estrutura de denylist (`jti`) preparada para logout imediato e revogação.

---

### ADR-003 — Insights do Dia por motor de regras determinístico

**Opções**:

| Abordagem | Prós | Contras |
|---|---|---|
| LLM gera os insights | Linguagem natural variada | Custo por requisição; latência; risco de alucinação; não testável |
| Motor de regras | Determinístico; testável; custo zero; instantâneo | Frases mais previsíveis |

**Decisão**: `InsightRuleEngine` com regras plugáveis (padrão Strategy). Cada regra implementa uma interface comum e declara severidade e prioridade. O engine avalia todas contra o snapshot meteorológico e retorna as N mais relevantes.

Adicionar um insight novo = criar uma classe e registrá-la. Nenhuma alteração no engine.

A IA fica restrita ao Assistant, onde a linguagem natural é o valor real.

---

### ADR-004 — Contenção da IA em três camadas

Prompt restritivo isolado é insuficiente. O módulo aplica:

1. **Validação de escopo** (pré-chamada): heurística de domínio meteorológico. Fora do escopo, responde com recusa padronizada sem consumir token.
2. **Injeção de contexto factual**: o `WeatherService` monta um snapshot real (atual + previsão) que entra no prompt. O modelo **interpreta** números, nunca os produz.
3. **System prompt restritivo**: instrui recusa explícita fora do domínio e proíbe estimativa de dados ausentes do contexto.

Provedor de LLM atrás de uma interface `AIProvider` — trocar de fornecedor é trocar uma implementação.

---

### ADR-005 — Abstração de provedores meteorológicos

**Decisão**: interface `WeatherProvider` com DTOs normalizados (`CurrentWeatherDTO`, `ForecastDTO`, `AirQualityDTO`).

- `OpenMeteoProvider` — primário (sem chave, sem limite prático).
- `OpenWeatherProvider` — complemento/fallback.
- `NominatimGeocoder` — geocoding e autocomplete (respeitando a política de uso: User-Agent identificado e throttling).

Um `WeatherProviderChain` tenta o primário e degrada para o fallback em erro ou timeout. Nenhuma camada acima conhece o provedor concreto.

---

### ADR-006 — Cache com interface desde o início

**Decisão**: interface `CacheBackend` (`get`, `set`, `delete`) com implementação `InMemoryTTLCache` agora. Migrar para Redis depois é registrar outra implementação no factory — zero alteração nos services.

TTLs previstos: clima atual 10 min, previsão 30 min, geocoding 24 h, qualidade do ar 30 min.

---

### ADR-007 — Estado no frontend com Context API

Redux seria overhead para o volume de estado global do projeto (usuário, tema, unidades). **Decisão**: Context API para estado global + hooks customizados (`useWeather`, `useFavorites`) encapsulando o Axios. Nenhum componente importa `axios` diretamente.

---

## 3. Estrutura de pastas

### Backend

```text
backend/
├── app/
│   ├── __init__.py                 # create_app() — application factory
│   ├── config.py                   # Development / Testing / Production
│   ├── extensions.py               # db, migrate, jwt, cors, limiter (sem app)
│   │
│   ├── auth/
│   │   ├── routes.py               # blueprint: /api/v1/auth
│   │   ├── service.py              # registro, login, refresh, senha
│   │   ├── repository.py
│   │   └── schemas.py              # validação de entrada/saída
│   │
│   ├── weather/
│   │   ├── routes.py               # /api/v1/weather
│   │   ├── service.py              # orquestra providers + cache
│   │   ├── schemas.py
│   │   └── providers/
│   │       ├── base.py             # WeatherProvider (ABC) + DTOs
│   │       ├── open_meteo.py
│   │       ├── open_weather.py
│   │       ├── nominatim.py
│   │       └── chain.py            # fallback encadeado
│   │
│   ├── ai/
│   │   ├── routes.py               # /api/v1/ai
│   │   ├── service.py              # orquestra escopo + contexto + provider
│   │   ├── repository.py           # conversas e mensagens
│   │   ├── schemas.py
│   │   ├── scope_validator.py      # camada 1
│   │   ├── context_builder.py      # camada 2
│   │   ├── prompts.py              # camada 3
│   │   └── providers/
│   │       ├── base.py             # AIProvider (ABC)
│   │       └── openai_provider.py
│   │
│   ├── insights/
│   │   ├── engine.py               # InsightRuleEngine
│   │   └── rules/                  # uma classe por regra
│   │
│   ├── favorites/                  # routes, service, repository, schemas
│   ├── history/
│   ├── profile/
│   ├── dashboard/                  # agregação para a tela principal
│   │
│   ├── models/
│   │   ├── base.py                 # TimestampMixin (id, created_at, updated_at)
│   │   ├── user.py
│   │   ├── favorite_city.py
│   │   ├── search_history.py
│   │   ├── conversation.py
│   │   ├── conversation_message.py
│   │   └── config.py
│   │
│   ├── repositories/
│   │   └── base.py                 # BaseRepository genérico (CRUD)
│   │
│   ├── middleware/
│   │   ├── error_handler.py        # handlers globais
│   │   ├── request_logger.py
│   │   └── security.py             # headers de segurança
│   │
│   ├── validators/                 # validadores reutilizáveis
│   ├── utils/
│   │   ├── exceptions.py           # hierarquia de exceções de domínio
│   │   ├── responses.py            # envelope padronizado
│   │   ├── cache.py                # CacheBackend + InMemoryTTLCache
│   │   ├── logger.py
│   │   └── security.py             # hash de senha
│   │
│   └── extensions.py
│
├── instance/weather.db
├── migrations/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   └── integration/
├── .env.example
├── requirements.txt
├── pyproject.toml                  # black, ruff, isort, pytest
└── run.py
```

### Frontend

```text
frontend/
├── src/
│   ├── main.jsx
│   ├── App.jsx
│   │
│   ├── components/
│   │   ├── ui/                     # Button, Card, Input, Modal, Spinner...
│   │   ├── weather/                # WeatherCard, MetricTile, ForecastList
│   │   ├── charts/                 # wrappers sobre Chart.js
│   │   ├── map/                    # wrappers sobre Leaflet
│   │   └── ai/                     # ChatWindow, MessageBubble
│   │
│   ├── layouts/                    # PublicLayout, AppLayout
│   ├── pages/                      # Landing, Login, Register, Dashboard...
│   ├── router/                     # rotas + ProtectedRoute
│   │
│   ├── services/
│   │   ├── httpClient.js           # instância Axios + interceptors
│   │   ├── authService.js
│   │   ├── weatherService.js
│   │   └── ...
│   │
│   ├── context/                    # AuthContext, ThemeContext, UnitsContext
│   ├── hooks/                      # useAuth, useWeather, useDebounce...
│   ├── utils/                      # formatters, constants
│   ├── styles/
│   │   ├── tokens.css              # design tokens (custom properties)
│   │   ├── theme.css               # claro/escuro
│   │   └── global.css
│   └── assets/
│
├── .env.example
├── vite.config.js
└── package.json
```

---

## 4. Modelo de dados (visão preliminar)

Todos os modelos herdam de `TimestampMixin`: `id`, `created_at`, `updated_at`.

| Entidade | Relacionamentos | Observações |
|---|---|---|
| `User` | 1:N com todas as demais | Soft delete (`is_active`) para preservar integridade histórica |
| `FavoriteCity` | N:1 `User` | Unique composto `(user_id, latitude, longitude)` |
| `SearchHistory` | N:1 `User` | Índice em `(user_id, created_at DESC)` |
| `Conversation` | N:1 `User`, 1:N mensagens | Já plural desde o início — suporta múltiplas conversas |
| `ConversationMessage` | N:1 `Conversation` | `role` (user/assistant), `content`, `weather_context` (JSON) |
| `Config` | N:1 `User` | Preferências: unidades, idioma, tema |

Coordenadas são a chave canônica de uma cidade, não o nome — evita ambiguidade entre homônimos.

Detalhamento completo fica para a Etapa 4.

---

## 5. Contratos da API

**Base**: `/api/v1` — versionamento desde o primeiro endpoint evita breaking changes futuros.

### Envelope de resposta

Sucesso:

```json
{ "success": true, "data": { }, "meta": { } }
```

Erro:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Mensagem amigável ao usuário",
    "details": { "email": "Formato inválido" }
  }
}
```

O `message` é sempre apresentável ao usuário final. Stack traces vão para o log, nunca para a resposta.

### Convenções

- Substantivos no plural: `/favorites`, `/history`.
- Verbo HTTP carrega a ação — nada de `/getFavorites`.
- Paginação por query string: `?page=1&per_page=20`.
- Códigos: 200, 201, 204, 400, 401, 403, 404, 409, 422, 429, 500.

---

## 6. Segurança

| Vetor | Mitigação |
|---|---|
| Senhas | Hash com algoritmo de custo adaptativo; nunca reversível |
| Força bruta | Flask-Limiter: 5 tentativas/min por IP no login |
| XSS | JWT em cookie httpOnly; sanitização de entrada |
| CSRF | Double-submit token nos cookies JWT |
| Injeção SQL | ORM exclusivamente; zero SQL concatenado |
| Enumeração de usuários | Mensagem genérica no login e no "esqueci minha senha" |
| Exposição de chaves | `.env` fora do versionamento; `.env.example` versionado |
| Abuso da IA | Rate limit dedicado por usuário no endpoint do assistente |

**Regra inegociável**: toda entrada do frontend é validada no backend por schema, mesmo que já validada no cliente. Validação no frontend é experiência do usuário, não segurança.

---

## 7. Tratamento de erros

Hierarquia de exceções de domínio em `utils/exceptions.py`:

```text
ClimoraException
├── ValidationError        → 422
├── AuthenticationError    → 401
├── AuthorizationError     → 403
├── NotFoundError          → 404
├── ConflictError          → 409
├── RateLimitError         → 429
└── ExternalServiceError   → 502
```

Services lançam exceções de domínio. Rotas não usam try/except: os handlers globais traduzem exceção em resposta HTTP. Isso mantém as rotas com 3 a 5 linhas.

---

## 8. Logging

Logging estruturado com rotação de arquivo. Eventos registrados: registro, login (sucesso e falha), refresh, alteração de senha, exclusão de conta, chamadas a APIs externas (com latência), pesquisas, chamadas à IA (com tokens consumidos) e exceções não tratadas.

**Nunca logar**: senhas, tokens completos, conteúdo integral das conversas.

---

## 9. Design system do frontend

Bootstrap 5 fornece grid e componentes base. Sobre ele, uma camada de design tokens em CSS custom properties.

- **Tema**: atributo `data-bs-theme` (nativo do Bootstrap 5.3) alternando entre `light` e `dark`. Todos os tokens são redefinidos por tema — nenhuma cor hardcoded em componente.
- **Paleta**: azul primário, branco como superfície, cinza para hierarquia textual, amarelo para destaques e alertas de UV.
- **Glassmorphism**: aplicado apenas em superfícies elevadas (cards de métrica, navbar), com `backdrop-filter` e fallback sólido para navegadores sem suporte.
- **Movimento**: transições de 150–250 ms em `transform` e `opacity`. Respeitar `prefers-reduced-motion`.
- **Responsividade**: mobile-first. O dashboard reflui de 4 colunas para 1.

---

## 10. Configuração

`.env` na raiz do backend, nunca versionado:

```text
FLASK_ENV=development
SECRET_KEY=
JWT_SECRET_KEY=
DATABASE_URL=sqlite:///instance/weather.db
OPENWEATHER_KEY=
OPENAI_KEY=
CORS_ORIGINS=http://localhost:5173
```

`config.py` valida na inicialização que as chaves obrigatórias existem em produção — falha rápido e explícita, nunca silenciosa.

---

## 11. Preparação para o futuro

| Funcionalidade | Preparação já contemplada |
|---|---|
| Cache/Redis | Interface `CacheBackend` desde a Etapa 6 |
| Docker | Configuração externalizada; sem caminho absoluto |
| PostgreSQL | ORM exclusivo; migrations versionadas |
| Múltiplos idiomas | Mensagens centralizadas; `Config.language` no modelo |
| Múltiplas conversas de IA | `Conversation` já é entidade separada |
| Notificações/alertas | Motor de regras já produz eventos com severidade |
| PWA | Vite com build estático; service worker é aditivo |
| Comparação entre cidades | DTOs normalizados permitem agregação |

---

## 12. Convenções de código

**Python**: PEP 8, `black` (linha 100), `ruff`, `isort`. Type hints em assinaturas públicas. Docstrings apenas onde o "porquê" não é óbvio.

**JavaScript**: ESLint + Prettier. Componentes em PascalCase, hooks com prefixo `use`, utilitários em camelCase.

**Geral**: identificadores em inglês; mensagens ao usuário em português. Funções com responsabilidade única. Comentário existe para explicar decisão, não para narrar código.

---

## 13. Roadmap

| # | Etapa | Entregável |
|---|---|---|
| 1 | Arquitetura | Este documento |
| 2 | Estrutura inicial | Esqueleto backend + frontend, factory, `/health` |
| 3 | Ambiente | Dependências, `.env`, linters, scripts |
| 4 | Modelagem | Models, migrations, repositories base |
| 5 | Autenticação | Registro, login, refresh, telas, rotas protegidas |
| 6 | APIs meteorológicas | Providers, DTOs, cache, geocoding |
| 7 | Dashboard | Tela principal completa |
| 8 | Pesquisa, favoritos, histórico | Autocomplete e CRUD |
| 9 | Mapas | Leaflet integrado |
| 10 | Gráficos | Chart.js — 6 visualizações |
| 11 | IA | Assistant + Insights |
| 12 | Perfil | Edição, senha, exclusão |
| 13 | Erros | Handlers globais e telas de erro |
| 14 | Qualidade | Testes, refatoração, documentação |

Cada etapa foi revisada e validada antes do início da seguinte.

---

## 14. Decisões tomadas durante a execução

Registro do que mudou frente ao plano original, e por quê.

| Decisão | Motivo |
|---|---|
| Geocoding pelo Open-Meteo, não Nominatim | O Nominatim limita a 1 requisição por segundo, inviável para autocomplete. Permanece como fallback e para geocoding reverso, com throttle implementado |
| `AI_BASE_URL` configurável | Chamar o modelo por HTTP puro em vez do SDK permitiu suportar OpenAI, Groq, OpenRouter e Ollama trocando duas linhas do `.env` |
| Um endpoint `/snapshot` em vez de quatro | Evita quatro requisições, quatro estados de carregamento e quatro pontos de falha no dashboard |
| Conversão de unidades no frontend | Mantém o cache do backend numa unidade canônica; trocar de preferência não invalida cache nem dispara nova requisição |
| `past_days=1` no Open-Meteo | Permite responder "está mais frio que ontem?" com dado real em vez de inferência |
| `insights/` separado de `ai/` | Insights são determinísticos; misturá-los com o assistente acoplaria coisas de natureza diferente |
| `UserSettings` em vez de `Config` | Evita ambiguidade com `app/config.py` |

---

## 15. Lições registradas

Defeitos encontrados em produção que a suíte não pegava, e o que mudou.

**Variável de ambiente vazia sobrescreve o padrão.** `os.getenv` só aplica o
fallback quando o nome não existe; `JWT_SECRET_KEY=` no `.env` venceu o padrão
e derrubou a assinatura de token. O helper `env()` trata valor em branco como
ausente. Os testes não pegaram porque o pytest não carrega `.env`.

**SQLite ignora foreign keys sem `PRAGMA foreign_keys=ON`.** Sem isso, todo
`ON DELETE CASCADE` seria silenciosamente inócuo e excluir uma conta deixaria
órfãos.

**SQLite não armazena fuso horário.** Uma coluna `DateTime(timezone=True)`
retorna naive, e comparar com um datetime aware levanta `TypeError`. O helper
`ensure_utc()` normaliza toda leitura.

**Health check que só executa `SELECT 1` mente.** Passava com o banco vazio. Passou
a verificar a presença das tabelas.

**Comparação de termos por substring dispara em fragmentos.** No validador de
escopo, `"ar"` casava dentro de "para" e `"ceu"` dentro de "aconteceu". A
comparação passou a ser por início de palavra, com radicais.

**Séries do Open-Meteo começam à meia-noite, não agora.** A previsão horária
mostrava o passado do dia e três cards liam valores da hora errada.

**Uma regra de insight sem noção de dia e noite recomenda caminhada às 21h.**
O UV é zero à noite, então todas as outras condições passavam. A regra passou a
cruzar com nascer e pôr do sol.

O padrão comum: números plausíveis, lógica passando, resultado sem sentido no
mundo real. Nenhum foi detectado por teste automatizado — todos apareceram na
revisão visual de cada etapa.

---

## 16. Ferramentas de verificação

Além do pytest, o projeto traz duas verificações estáticas criadas durante a
execução, ambas após defeitos reais escaparem:

```bash
cd backend && python tools/check_imports.py
cd frontend && npm run check:imports
```

Elas validam que todo nome importado entre módulos do projeto existe na origem.
Python e JavaScript só falham nisso quando a linha executa, então um método
renomeado passa por `py_compile` e quebra em produção.
