"""First containment layer: reject what is plainly not about weather.

A cheap filter, not the real guard. It exists to avoid spending tokens on
obvious off-topic questions, and it is deliberately lenient: refusing a
legitimate question costs the product more than a few wasted tokens. The
system prompt is what actually holds the line, and the injected context is
what keeps answers factual.
"""

from __future__ import annotations

import re
import unicodedata

# Terms are stems matched at word start, so "chuv" covers chuva, chuvas and
# chuvoso. Matching by plain substring would fire on "ar" inside "para" and
# "ceu" inside "aconteceu".
WEATHER_STEMS = frozenset(
    {
        "chuv", "chov", "temporal", "tempestade", "garoa", "granizo",
        "sol", "ensolarad", "nublad", "nuvem", "nuven", "ceu", "clima", "tempo",
        "previs", "temperatura", "termic", "termometro", "grau",
        "frio", "esfri", "calor", "esquent", "quente", "gelad", "abafad",
        "neve", "nevar", "vento", "ventan", "ventil", "rajada",
        "umidade", "umid", "seco", "secura", "pressao", "uv", "ultravioleta",
        "neblina", "nevoeiro", "visibilidade", "raio", "trovoada", "orvalho",
        "casaco", "agasalho", "protetor", "guarda-chuva", "guarda chuva", "sombrinha",
        "poluic", "qualidade do ar", "insolac", "desidrat", "alergi", "respir",
        "amanhecer", "anoitecer", "nascer do sol", "por do sol",
        "estacao", "verao", "inverno", "outono", "primavera",
        "sensacao termica", "precipitac", "meteorolog",
    }
)

CONTEXT_STEMS = frozenset(
    {
        "hoje", "amanha", "agora", "ontem", "semana", "fim de semana",
        "final de semana", "manha", "tarde", "noite", "madrugada",
        "sabado", "domingo", "segunda", "terca", "quarta", "quinta", "sexta",
        "horario", "hora", "dia",
        "viaj", "caminh", "corr", "pedal", "sair", "praia", "piscina",
        "roupa", "vestir", "levar", "estender", "varal", "pratic", "trein",
        "exercicio", "passe", "churrasco", "evento", "moto", "trilha",
        "lavar o carro", "pet", "crianca", "idoso", "plant", "agricultura",
        "pesca", "acamp",
    }
)

OFF_TOPIC_STEMS = frozenset(
    {
        "codigo", "program", "python", "javascript", "sql", "compil",
        "receita", "cozinh", "futebol", "jogo", "campeonato",
        "politic", "presidente", "eleic", "governo",
        "bitcoin", "investi", "bolsa", "acao da",
        "traduz", "poema", "musica", "filme", "serie", "piada",
        "namorad", "remedio", "medico", "diagnostic", "sintoma",
        "matematica", "equacao", "curriculo", "emprego", "senha", "hackear",
        "historia sobre", "conte uma",
    }
)

# A short follow-up carries no vocabulary of its own: "isso pra qual cidade?"
# means nothing alone but is obvious after an answer about the forecast.
FOLLOW_UP_STEMS = frozenset(
    {
        "isso", "esse", "essa", "isto", "ele", "ela", "la", "ai", "aqui",
        "cidade", "local", "lugar", "regiao", "onde", "qual", "quais",
        "quanto", "quando", "como", "porque", "por que", "pq",
        "detalh", "explic", "confirm", "certeza", "compar",
        "melhor", "pior", "media", "maximo", "minimo", "resum",
        "mais", "menos", "tambem", "obrigad", "valeu", "entendi",
    }
)

SHORT_FOLLOW_UP_WORDS = 8


def normalize(text: str) -> str:
    """Fold accents and case so matching does not depend on spelling."""
    decomposed = unicodedata.normalize("NFD", text.lower())
    return "".join(char for char in decomposed if unicodedata.category(char) != "Mn")


def _build_matcher(stems: frozenset[str]) -> re.Pattern[str]:
    """Match each stem at a word start, allowing any suffix."""
    ordered = sorted((re.escape(stem) for stem in stems), key=len, reverse=True)
    return re.compile(r"(?<!\w)(?:" + "|".join(ordered) + r")\w*")


_WEATHER = _build_matcher(WEATHER_STEMS)
_CONTEXT = _build_matcher(CONTEXT_STEMS)
_OFF_TOPIC = _build_matcher(OFF_TOPIC_STEMS)
_FOLLOW_UP = _build_matcher(FOLLOW_UP_STEMS)


def is_weather_related(message: str, has_history: bool = False) -> bool:
    """Whether the question plausibly concerns the weather."""
    normalized = normalize(message)

    # Anything clearly from another domain is rejected regardless of context.
    if _OFF_TOPIC.search(normalized):
        return False

    if _WEATHER.search(normalized):
        return True

    # "Vou viajar amanhã" carries no weather word but is a weather question in
    # this product.
    if _CONTEXT.search(normalized):
        return True

    # Mid-conversation, a short question refers to what was just discussed.
    if has_history and len(normalized.split()) <= SHORT_FOLLOW_UP_WORDS:
        return bool(_FOLLOW_UP.search(normalized))

    return False
