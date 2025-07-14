#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Script schema.py
================
Definimos um esquema TravelRequest usando o Pydantic. Isso
garante que todos os agentes concordem com a estrutura das
solicitações recebidas, o que inclui o destino, as datas da
viagem e o orçamento do usuário.

Esta class ajuda em:

* Manter a entrada consistente para todos os agentes.
* Adicionando validação automática com `FastAPI`.
* Simplificando a reutilização de código.
"""
from pydantic import BaseModel


class TravelRequest(BaseModel):
    destination: str
    start_date: str
    end_date: str
    budget: float
