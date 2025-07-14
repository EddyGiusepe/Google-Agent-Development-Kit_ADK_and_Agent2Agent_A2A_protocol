#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script task_manager.py
======================
Este arquivo define a função run que executa o agente de estadia.
"""
from .agent import execute


async def run(payload):
    return await execute(payload)
