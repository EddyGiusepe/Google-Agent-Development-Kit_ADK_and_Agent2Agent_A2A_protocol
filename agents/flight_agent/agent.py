#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script agent.py
===============
Este arquivo define o agente de voos.
"""
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Sugerir opções de voos para um destino.",
    instruction=(
        "Dado um destino, datas de viagem e orçamento, sugerir 1-2 opções de voos realistas. "
        "Incluir nome da companhia aérea, preço e horário de partida. Garantir que os voos sejam compatíveis com o orçamento."
    ),
)

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent, app_name="flight_app", session_service=session_service
)

USER_ID = "user_1"
SESSION_ID = "session_001"


async def execute(request):
    # 🔧 Garantir que a sessão seja criada antes de executar o agente:
    await session_service.create_session(
        app_name="flight_app", user_id=USER_ID, session_id=SESSION_ID
    )

    # prompt = (
    #     f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
    #     f"with a budget of {request['budget']}. Suggest flight options."
    # )
    prompt = (
        f"O usuário está voando de {request['origin']} para {request['destination']} "
        f"de {request['start_date']} a {request['end_date']}, com um orçamento de {request['budget']}. "
        "Sugerir 2-3 opções de voos realistas. Para cada opção, incluir nome da companhia aérea, horário de partida, horário de chegada, "
        "preço e mencionar se é direto ou tem escalas."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            return {"flights": event.content.parts[0].text}
