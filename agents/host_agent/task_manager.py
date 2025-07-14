#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script task_manager.py
======================
Este arquivo define a função run que executa o agente de hospedagem.
"""
from common.a2a_client import call_agent

FLIGHT_URL = "http://localhost:8001/run"
STAY_URL = "http://localhost:8002/run"
ACTIVITIES_URL = "http://localhost:8003/run"


async def run(payload):
    # 👀 Imprimir o que o agente de hospedagem está enviando:
    print("🚀 Entrada do payload:", payload)

    flights = await call_agent(FLIGHT_URL, payload)
    stay = await call_agent(STAY_URL, payload)
    activities = await call_agent(ACTIVITIES_URL, payload)

    # 🧾 Saída de Log:
    print("📦 Voos:", flights)
    print("📦 Estadia:", stay)
    print("📦 Atividades:", activities)

    # 🛡 Garantir que todos sejam dicionários antes de acessar:
    flights = flights if isinstance(flights, dict) else {}
    stay = stay if isinstance(stay, dict) else {}
    activities = activities if isinstance(activities, dict) else {}

    return {
        "flights": flights.get("flights", "Nenhum voo retornado."),
        "stay": stay.get("stays", "Nenhuma estadia retornada."),
        "activities": activities.get("activities", "Nenhuma atividade encontrada."),
    }
