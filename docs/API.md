# Climora — Referência da API

**Base:** `/api/v1`
**Autenticação:** JWT em cookies `httpOnly`, com proteção CSRF por double-submit.

---

## Convenções

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
    "message": "Mensagem apresentável ao usuário",
    "details": { "email": "Formato inválido" }
  }
}
```

O campo `message` é sempre exibível ao usuário final. Stack traces vão para o
log, nunca para a resposta.

### Códigos de erro

| Código | HTTP | Significado |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Corpo ou query string inválidos; `details` mapeia campo → mensagem |
| `AUTHENTICATION_ERROR` | 401 | Credenciais inválidas ou sessão ausente |
| `TOKEN_EXPIRED` | 401 | Access token expirado; o cliente deve renovar |
| `AUTHORIZATION_ERROR` | 403 | Sem permissão |
| `NOT_FOUND` | 404 | Recurso inexistente ou de outro usuário |
| `CONFLICT` | 409 | Recurso já existe |
| `RATE_LIMIT_EXCEEDED` | 429 | Limite de requisições atingido |
| `EXTERNAL_SERVICE_ERROR` | 502 | Falha em provedor externo |
| `INTERNAL_ERROR` | 500 | Erro não previsto |

### CSRF

Requisições que alteram estado (`POST`, `PUT`, `PATCH`, `DELETE`) exigem o
header `X-CSRF-TOKEN`, cujo valor está no cookie `csrf_access_token`. A rota de
refresh usa `csrf_refresh_token`.

### Limites de requisição

| Endpoint | Limite |
|---|---|
| `POST /auth/login` | 5 por minuto |
| `POST /auth/register` | 5 por hora |
| `PUT /profile/password`, `DELETE /profile` | 10 por hora |
| `POST /ai/chat` | 20 por minuto |
| `/weather/*` | 60 por minuto |
| Demais | 200 por hora |

---

## Sistema

### `GET /system/health`

Não autenticado. Verifica aplicação e schema do banco.

```json
{
  "success": true,
  "data": {
    "application": "Climora",
    "version": "1.0.0",
    "environment": "development",
    "database": "up"
  }
}
```

Devolve `503` com `"database": "schema_incomplete"` e a lista `missing_tables`
quando as migrations não foram aplicadas.

---

## Autenticação

### `POST /auth/register`

```json
{
  "name": "Arthur Assis",
  "email": "arthur@example.com",
  "password": "climora2026",
  "password_confirmation": "climora2026"
}
```

Senha: mínimo de 8 caracteres, com ao menos uma letra e um número. Responde
`201` com o usuário e define os cookies de sessão. `409` se o e-mail já existe.

### `POST /auth/login`

```json
{ "email": "arthur@example.com", "password": "climora2026", "remember_me": false }
```

`remember_me` estende o refresh token de 7 para 30 dias. E-mail inexistente e
senha errada devolvem a mesma mensagem, para não revelar quais endereços têm
conta.

### `POST /auth/refresh`

Requer o refresh token. Emite novo access token sem pedir credenciais.

### `POST /auth/logout`

Limpa os cookies. Funciona com ou sem sessão ativa.

### `GET /auth/me`

Usuário da sessão atual. Usado pelo frontend para restaurar a sessão no
carregamento da página, já que o cookie `httpOnly` não é legível por script.

---

## Clima

Todos exigem autenticação.

### `GET /weather/search?q=<texto>&limit=<1-10>`

Autocomplete de cidades. Filtra para lugares habitados, ignorando países e
regiões, salvo quando isso não deixaria resultado algum.

### `GET /weather/reverse?lat=&lon=`

Coordenada para lugar nomeado.

### `GET /weather/snapshot?lat=&lon=`

Retorno completo em uma chamada: condições atuais, 48 horas, 7 dias,
qualidade do ar e o dia anterior.

```json
{
  "location": { "name": "Sabará", "state": "Minas Gerais", "location_key": "-19.8889,-43.8058" },
  "current": { "temperature": 24.3, "condition": "Parcialmente nublado", "uv_index": 3.2 },
  "hourly": [ { "time": "2026-07-28T19:00", "temperature": 22.8 } ],
  "daily": [ { "date": "2026-07-28", "temperature_max": 27.4 } ],
  "air_quality": { "index": 18, "category": "Boa" },
  "previous_day": { "date": "2026-07-27", "temperature_max": 26.0 },
  "provider": "open-meteo"
}
```

Unidades canônicas: Celsius e km/h. A conversão para preferência do usuário
acontece no frontend.

### `GET /weather/air-quality?lat=&lon=`

Qualidade do ar isolada.

---

## Favoritos

### `GET /favorites?q=<busca opcional>`

Ordenados por posição.

### `POST /favorites`

```json
{
  "name": "Sabará",
  "latitude": -19.8889,
  "longitude": -43.8058,
  "state": "Minas Gerais",
  "country": "Brasil",
  "country_code": "BR"
}
```

A identidade de um lugar são suas coordenadas arredondadas a quatro casas, não
o nome: adicionar "Sabará" e depois "Sabara" nas mesmas coordenadas devolve
`409`. Limite de 50 por usuário.

### `PATCH /favorites/<id>`

Aceita `label` e `position`. Atualização parcial: campos ausentes permanecem.

### `DELETE /favorites/<id>`

Um id de outro usuário devolve `404`, não `403` — um `403` confirmaria que
aquele registro existe.

---

## Histórico

### `GET /history?page=&per_page=&q=`

Paginado, mais recentes primeiro. `meta` traz `page`, `per_page`, `total` e
`pages`. Máximo de 50 por página.

### `POST /history`

Registra uma consulta deliberada. Reabrir a mesma cidade em menos de 10 minutos
atualiza o registro em vez de duplicar.

### `DELETE /history/<id>` · `DELETE /history`

Remove um registro ou limpa tudo. A limpeza devolve `removed` com a contagem.

---

## Insights

### `GET /insights?lat=&lon=`

Insights do Dia, gerados por motor de regras determinístico — sem custo, sem
latência de modelo e sem risco de alucinação.

```json
[
  {
    "id": "rain",
    "title": "Leve guarda-chuva",
    "description": "A chance de chuva chega a 70% hoje.",
    "icon": "umbrella",
    "severity": "warning",
    "priority": 90
  }
]
```

`severity` assume `positive`, `info` ou `warning`. Retorna no máximo 4, das
maiores prioridades.

---

## Assistente

### `POST /ai/chat`

```json
{
  "message": "Vai chover hoje?",
  "conversation_id": null,
  "lat": -19.8889,
  "lon": -43.8058
}
```

Sem `conversation_id`, uma conversa nova é criada com a pergunta como título.

Três camadas de contenção: um validador de escopo rejeita perguntas fora do
domínio antes de gastar token; o snapshot meteorológico real é injetado no
prompt para que o modelo interprete números em vez de produzi-los; e o prompt
de sistema restringe o comportamento.

Responde `201` com `conversation`, `question` e `answer`.

### `GET /ai/conversations` · `GET /ai/conversations/<id>/messages` · `DELETE /ai/conversations/<id>`

Listagem, mensagens e exclusão. Conversas de outro usuário devolvem `404`.

---

## Perfil

### `GET /profile` · `PATCH /profile`

Leitura e atualização de `name` e `avatar_url`. Payload vazio devolve `422`.

### `PUT /profile/password`

```json
{
  "current_password": "climora2026",
  "new_password": "novaSenha2027",
  "new_password_confirmation": "novaSenha2027"
}
```

Exige a senha atual. Emite cookies novos, então a sessão sobrevive à troca.

### `DELETE /profile`

```json
{ "password": "climora2026" }
```

Exclusão definitiva. Favoritos, histórico, conversas e preferências vão junto
pelas cascatas do banco.

### `GET /profile/settings` · `PUT /profile/settings`

```json
{ "temperature_unit": "fahrenheit", "wind_speed_unit": "ms", "theme": "dark", "language": "pt-BR" }
```

Atualização parcial: preferências não enviadas permanecem.

---

## Documentação interativa

Swagger/OpenAPI não está implementado. A estrutura favorece a adição: os
schemas pydantic de cada módulo já descrevem entrada e saída, e podem gerar a
especificação sem duplicação de definições.
