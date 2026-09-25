"""The assistant's first containment layer."""

import pytest

from app.ai.scope_validator import is_weather_related, normalize


@pytest.mark.parametrize(
    "question",
    [
        "Vai chover hoje?",
        "Qual melhor horário para caminhar?",
        "Vou viajar amanhã",
        "Preciso levar guarda-chuva?",
        "Como estará o tempo no final de semana?",
        "Vai fazer frio?",
        "Melhor horário para correr?",
        "Devo estender roupa no varal?",
        "O indice uv esta alto?",
    ],
)
def test_weather_questions_are_accepted(question):
    assert is_weather_related(question) is True


@pytest.mark.parametrize(
    "question",
    [
        "Escreva um código Python para ordenar uma lista",
        "Quem é o presidente do Brasil?",
        "Me dê uma receita de bolo de cenoura",
        "Qual foi o resultado do jogo ontem?",
        "Devo investir em bitcoin?",
        "Traduza esta frase para o inglês",
        "Que remédio tomar para dor de cabeça?",
    ],
)
def test_off_topic_questions_are_rejected(question):
    assert is_weather_related(question) is False


def test_off_topic_wins_even_with_a_time_reference():
    """"Que código escrevo hoje" must not pass on the strength of "hoje"."""
    assert is_weather_related("Que código eu escrevo hoje?") is False


def test_matching_ignores_accents_and_case():
    assert normalize("PREVISÃO") == "previsao"
    assert is_weather_related("PREVISAO PARA AMANHA") is True


@pytest.mark.parametrize(
    "question",
    [
        "isso pra qual cidade?",
        "e amanhã?",
        "tem certeza?",
        "me explica melhor",
        "qual o resumo?",
        "e onde?",
    ],
)
def test_short_follow_ups_are_accepted_inside_a_conversation(question):
    """A follow-up carries no vocabulary of its own; the thread supplies it."""
    assert is_weather_related(question, has_history=True) is True


def test_the_same_follow_up_is_rejected_as_a_first_message():
    assert is_weather_related("isso pra qual cidade?") is False


def test_off_topic_is_rejected_even_mid_conversation():
    assert is_weather_related("escreva um código Python", has_history=True) is False
    assert is_weather_related("quem é o presidente?", has_history=True) is False


def test_a_long_message_without_weather_terms_is_still_rejected():
    """The follow-up allowance is for short questions, not free-form text."""
    message = "me conte uma historia longa sobre isso que aconteceu com voce ontem por favor"

    assert is_weather_related(message, has_history=True) is False


def test_terms_match_whole_words_not_fragments():
    """Regression: "ar" fired inside "para" and "ceu" inside "aconteceu"."""
    assert is_weather_related("Traduza esta frase para o inglês") is False
    assert is_weather_related("o que aconteceu com voce") is False


def test_stems_cover_inflections():
    """"chuv" has to reach chuva, chuvas and chuvoso."""
    for phrase in ("vai ter chuva?", "as chuvas continuam?", "o dia esta chuvoso?"):
        assert is_weather_related(phrase) is True
