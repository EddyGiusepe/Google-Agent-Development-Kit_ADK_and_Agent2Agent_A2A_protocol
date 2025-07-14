#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script agent.py
===============
Este arquivo define o agente de hospedagem.
"""
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

host_agent = Agent(
    name="host_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Coordena o planejamento de viagens chamando para agentes de voos (flight), estadia (stay) e atividades (activity).",
    instruction="Você é o agente de hospedagem responsável por orquestrar as tarefas de planejamento de viagens. "
    "Você chama agentes externos para coletar voos, estadias e atividades, e retorna um resultado final.",
)

session_service = InMemorySessionService()
runner = Runner(agent=host_agent, app_name="host_app", session_service=session_service)

USER_ID = "user_host"
SESSION_ID = "session_host"


async def execute(request):
    # 🔧 Garantir que a sessão exista:
    session_service.create_session(
        app_name="host_app", user_id=USER_ID, session_id=SESSION_ID
    )

    prompt = (
        f"Planejar uma viagem para {request['destination']} de {request['start_date']} a {request['end_date']} "
        f"dentro de um orçamento total de {request['budget']}. Chamar os agentes de voos, estadias e atividades para obter resultados."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}
