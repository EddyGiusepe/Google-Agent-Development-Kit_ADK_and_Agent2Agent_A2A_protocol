#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script __main__.py
==================
Este script é responsável por iniciar o servidor FastAPI para o agente de voos.
Ele usa a função create_app para configurar o aplicativo e o task_manager para
executar a lógica do agente.
"""
from common.a2a_server import create_app
from .task_manager import run

app = create_app(agent=type("Agent", (), {"execute": run}))

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8003)
