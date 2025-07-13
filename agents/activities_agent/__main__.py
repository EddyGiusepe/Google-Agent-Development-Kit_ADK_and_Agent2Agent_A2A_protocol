#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script __main__.py
==================
Este script é o ponto de entrada para o agente de atividades.
Ele cria um aplicativo FastAPI com uma rota `/run` padrão
que delega a execução ao agente fornecido. Ele garante uma interface
de agente para agente (A2A) consistente para todos os serviços
usando entrada JSON estruturada.
"""
from common.a2a_server import create_app
from .task_manager import run

app = create_app(agent=type("Agent", (), {"execute": run}))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8001)
