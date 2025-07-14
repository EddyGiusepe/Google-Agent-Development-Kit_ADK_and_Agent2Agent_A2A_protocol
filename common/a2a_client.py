#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script a2a_client.py
====================
Este utilitário assíncrono leve permite que qualquer
agente (especialmente o host) invoque outro agente
usando o protocolo A2A chamando o ponto de extremidade `/run`.

Este utilitário envia de forma assíncrona uma solicitação POST para o
endpoint /run de outro agente usando httpx. Ele retorna a resposta
JSON analisada e gera um erro se a solicitação falhar.

Usaremos esse utilitário em nosso agente host para chamar
`flight_agent`, `stay_agent`, e `activities_agent`.
"""
import httpx


async def call_agent(url, payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=60.0)
        response.raise_for_status()
        return response.json()
