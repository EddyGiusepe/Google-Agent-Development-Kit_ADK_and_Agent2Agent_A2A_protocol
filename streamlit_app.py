#! /usr/bin/env python3
"""
Senior Data Scientist.: Dr. Eddy Giusepe Chirinos Isidro

Este maravilhoso projeto foi baseao no Tutorial Datacamp de
Aashi Dutt.

Script streamlit_app.py
=======================
Este script é responsável por criar a interface do usuário
Streamlit para o sistema de planejamento de viagens.

Run
---
streamlit run streamlit_app.py
"""
import streamlit as st
import requests

st.set_page_config(page_title="Planejador de viagens com tecnologia ADK", page_icon="✈️")

st.title("🌍 Planejador de viagens com tecnologia ADK")

# ✨ Add start location here
origin = st.text_input("De onde você está voando?", placeholder="e.g., Vitória-ES")

destination = st.text_input(
    "Para onde você está indo?", placeholder="e.g., Lima-Perú"
)
start_date = st.date_input("Data de partida")
end_date = st.date_input("Data de chegada")
budget = st.number_input("Orçamento (em USD)", min_value=100, step=50)

if st.button("Planejar minha viagem ✨"):
    if not all([origin, destination, start_date, end_date, budget]):
        st.warning("Por favor, preencha todos os detalhes.")
    else:
        payload = {
            "origin": origin,
            "destination": destination,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "budget": budget,
        }
        response = requests.post("http://localhost:8000/run", json=payload)

        if response.ok:
            data = response.json()
            st.subheader("✈️ Voos")
            st.markdown(data["flights"])
            st.subheader("🏨 Estadias")
            st.markdown(data["stay"])
            st.subheader("🗺️ Atividades")
            st.markdown(data["activities"])
        else:
            st.error("Falha ao buscar o plano de viagem. Por favor, tente novamente.")
