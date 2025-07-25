from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

stay_agent = Agent(
    name="stay_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Sugerir opções de hotel ou estadia para um destino.",
    instruction=(
        "Dado um destino, datas de viagem e orçamento, sugerir 2-3 opções de hotel ou estadia. "
        "Incluir nome do hotel, preço por noite e localização. Garantir que as sugestões sejam dentro do orçamento."
    ),
)

session_service = InMemorySessionService()
runner = Runner(agent=stay_agent, app_name="stay_app", session_service=session_service)

USER_ID = "user_stay"
SESSION_ID = "session_stay"


async def execute(request):
    await session_service.create_session(
        app_name="stay_app", user_id=USER_ID, session_id=SESSION_ID
    )

    prompt = (
        f"O usuário está hospedando-se em {request['destination']} de {request['start_date']} a {request['end_date']} "
        f"com um orçamento de {request['budget']}. Sugerir opções de estadia."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            return {"stays": event.content.parts[0].text}
