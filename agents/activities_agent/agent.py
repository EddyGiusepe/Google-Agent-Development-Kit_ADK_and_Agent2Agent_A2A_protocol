#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script agent.py
===============
Este script define o agente de atividades. Ele cria um agente que sugere 
atividades interessantes para o usuário em um destino.
"""
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

activities_agent = Agent(
    name="activities_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Sugere atividades interessantes para o usuário em um destino.",
    instruction=(
        "Dado um destino, datas e orçamento, sugerir 2-3 atividades turísticas ou culturais. "
        "Para cada atividade, fornecer nome, descrição curta, estimativa de preço e duração em horas. "
        "Responda em português brasileiro simples (não JSON). Mantenha-o conciso e bem formatado."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent,
    app_name="activities_app",
    session_service=session_service
)

USER_ID = "user_activities"
SESSION_ID = "session_activities"

async def execute(request):
    await session_service.create_session(
        app_name="activities_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = (
        f"O usuário está voando para {request['destination']} de {request['start_date']} até {request['end_date']}, "
        f"com um orçamento de {request['budget']}. Sugeira 2-3 atividades, cada uma com nome, descrição concisa, estimativa de preço e duração. "
        f"Responda em formato JSON usando a chave 'activities' com uma lista de objetos de atividade."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "activities" in parsed and isinstance(parsed["activities"], list):
                    return {"activities": parsed["activities"]}
                else:
                    print("❌ A chave 'activities' está ausente ou não é uma lista no JSON da resposta")
                    return {"activities": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("❌ Falha ao analisar o JSON:", e)
                print("Conteúdo da resposta:", response_text)
                return {"activities": response_text}  # fallback to raw text
            
