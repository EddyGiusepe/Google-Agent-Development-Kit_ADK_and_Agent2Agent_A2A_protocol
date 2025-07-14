#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script a2a_server.py
====================
Em vez de escrever uma rota FastAPI personalizada para cada agente,
nós a generalizamos usando a função create_app(agent), que manipula:

* Servindo o agente em `/run`
* Recebendo uma solicitação de viagem
* Retornando uma resposta estruturada

Este utilitário cria um aplicativo FastAPI com uma rota `/run` padrão
que delega a execução ao agente fornecido. Ele garante uma interface de
agente para agente (A2A) consistente para todos os serviços usando entrada
JSON estruturada.

Juntos, esses componentes compartilhados tornam nosso sistema multiagente
mais sustentável, reutilizável e alinhado à filosofia A2A do Google de
mensagens interagentes simples e estruturadas.
"""
from fastapi import FastAPI
import uvicorn


def create_app(agent):
    app = FastAPI(
        title="🤗 Agente que sugere atividades interessantes ao usuário🤗",
        version="1.0.0",
        description="""Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro""",
    )

    @app.post("/run")
    async def run(payload: dict):
        return await agent.execute(payload)

    return app
