"""Assistant endpoints, with the model and the weather layer mocked."""

from unittest.mock import patch

from app.ai.providers.base import ChatCompletion
from app.ai.prompts import OUT_OF_SCOPE_REPLY

ACCOUNT = {
    "name": "Arthur Assis",
    "email": "arthur@example.com",
    "password": "climora2026",
    "password_confirmation": "climora2026",
}

QUESTION = {"message": "Vai chover hoje?", "lat": -19.8889, "lon": -43.8058}

ANSWER = "A chance de chuva hoje é de 10%, então provavelmente não chove."


def authenticate(client):
    client.post("/api/v1/auth/register", json=ACCOUNT)


def ask(client, **overrides):
    return client.post("/api/v1/ai/chat", json={**QUESTION, **overrides})


def mock_model(content=ANSWER):
    return patch(
        "app.ai.providers.openai_provider.OpenAIProvider.complete",
        return_value=ChatCompletion(content=content, tokens_used=120),
    )


def mock_weather():
    from tests.unit.test_insights import build_snapshot

    return patch("app.weather.service.WeatherService.get_snapshot", return_value=build_snapshot())


def test_chat_requires_authentication(client):
    assert ask(client).status_code == 401


def test_a_weather_question_reaches_the_model(client):
    authenticate(client)

    with mock_weather(), mock_model():
        response = ask(client)

    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["answer"]["content"] == ANSWER
    assert data["answer"]["role"] == "assistant"
    assert data["conversation"]["title"] == "Vai chover hoje?"


def test_an_off_topic_question_never_reaches_the_model(client):
    authenticate(client)

    with mock_weather(), mock_model() as model:
        response = ask(client, message="Escreva um código Python")

    assert response.status_code == 201
    assert response.get_json()["data"]["answer"]["content"] == OUT_OF_SCOPE_REPLY
    # The point of the first layer: no tokens spent.
    model.assert_not_called()


def test_the_prompt_carries_real_weather_data(client):
    """The model must interpret numbers, never produce them."""
    authenticate(client)

    with mock_weather(), mock_model() as model:
        ask(client)

    system_prompt = model.call_args.args[0]
    assert "DADOS METEOROLÓGICOS DISPONÍVEIS" in system_prompt
    assert "Sabará" in system_prompt
    assert "Temperatura: 22°C" in system_prompt


def test_a_follow_up_stays_in_the_same_conversation(client):
    authenticate(client)

    with mock_weather(), mock_model():
        first = ask(client).get_json()["data"]["conversation"]["id"]
        second = ask(client, message="E amanhã?", conversation_id=first)

    assert second.get_json()["data"]["conversation"]["id"] == first


def test_history_is_replayed_to_the_model(client):
    authenticate(client)

    with mock_weather(), mock_model() as model:
        conversation_id = ask(client).get_json()["data"]["conversation"]["id"]
        ask(client, message="E amanhã?", conversation_id=conversation_id)

    history = model.call_args.args[1]
    assert [turn.content for turn in history][:3] == [QUESTION["message"], ANSWER, "E amanhã?"]


def test_messages_can_be_listed(client):
    authenticate(client)

    with mock_weather(), mock_model():
        conversation_id = ask(client).get_json()["data"]["conversation"]["id"]

    response = client.get(f"/api/v1/ai/conversations/{conversation_id}/messages")

    assert response.status_code == 200
    assert len(response.get_json()["data"]) == 2


def test_conversations_are_listed_for_the_owner(client):
    authenticate(client)

    with mock_weather(), mock_model():
        ask(client)

    assert len(client.get("/api/v1/ai/conversations").get_json()["data"]) == 1


def test_another_users_conversation_is_invisible(client):
    authenticate(client)
    with mock_weather(), mock_model():
        conversation_id = ask(client).get_json()["data"]["conversation"]["id"]
    client.post("/api/v1/auth/logout")

    client.post("/api/v1/auth/register", json={**ACCOUNT, "email": "outra@example.com"})
    response = client.get(f"/api/v1/ai/conversations/{conversation_id}/messages")

    assert response.status_code == 404


def test_a_conversation_can_be_deleted_with_its_messages(client):
    authenticate(client)

    with mock_weather(), mock_model():
        conversation_id = ask(client).get_json()["data"]["conversation"]["id"]

    assert client.delete(f"/api/v1/ai/conversations/{conversation_id}").status_code == 200
    assert client.get("/api/v1/ai/conversations").get_json()["data"] == []


def test_an_empty_message_is_rejected(client):
    authenticate(client)

    assert ask(client, message="   ").status_code == 422


def test_coordinates_are_required(client):
    authenticate(client)

    response = client.post("/api/v1/ai/chat", json={"message": "Vai chover?"})

    assert response.status_code == 422


def test_a_follow_up_reaches_the_model_when_the_thread_has_history(client):
    """"isso pra qual cidade?" was being refused before the thread was read."""
    authenticate(client)

    with mock_weather(), mock_model() as model:
        conversation_id = ask(client).get_json()["data"]["conversation"]["id"]
        response = ask(client, message="isso pra qual cidade?", conversation_id=conversation_id)

    assert response.get_json()["data"]["answer"]["content"] == ANSWER
    assert model.call_count == 2


def test_the_same_follow_up_is_refused_as_a_first_message(client):
    authenticate(client)

    with mock_weather(), mock_model() as model:
        response = ask(client, message="isso pra qual cidade?")

    assert response.get_json()["data"]["answer"]["content"] == OUT_OF_SCOPE_REPLY
    model.assert_not_called()


def test_the_context_names_the_weekday_so_the_model_need_not_calculate_it(client):
    authenticate(client)

    with mock_weather(), mock_model() as model:
        ask(client, message="Vai chover no domingo?")

    system_prompt = model.call_args.args[0]
    assert "PRÓXIMOS DIAS" in system_prompt
    assert any(day in system_prompt for day in ("segunda-feira", "terça-feira", "domingo"))


def test_the_prompt_names_the_city_it_is_answering_about(client):
    authenticate(client)

    with mock_weather(), mock_model() as model:
        ask(client)

    system_prompt = model.call_args.args[0]
    assert "Sabará" in system_prompt


def test_the_prompt_forbids_synoptic_concepts_the_data_cannot_support(client):
    """Sounding technical is not the same as being right."""
    authenticate(client)

    with mock_weather(), mock_model() as model:
        ask(client)

    system_prompt = model.call_args.args[0]
    for forbidden in ("frente fria", "massa de ar", "CAPE", "radar"):
        assert forbidden in system_prompt  # named only to be prohibited
    assert "NUNCA mencione frente fria" in system_prompt
