import streamlit as st
from src.modelos import Metrica


def exibir_cartoes_metricas(metricas: list[Metrica]) -> None:
    """Exibe cartões resumo comparando o desempenho geral de cada algoritmo."""
    algoritmos = sorted({metrica.algoritmo for metrica in metricas})
    colunas = st.columns(len(algoritmos)) if algoritmos else []

    for coluna, algoritmo in zip(colunas, algoritmos):
        metricas_do_algoritmo = [metrica for metrica in metricas if metrica.algoritmo == algoritmo]
        total_verdadeiros_positivos = sum(metrica.verdadeiros_positivos for metrica in metricas_do_algoritmo)
        total_falsos_positivos = sum(metrica.falsos_positivos for metrica in metricas_do_algoritmo)
        total_falsos_negativos = sum(metrica.falsos_negativos for metrica in metricas_do_algoritmo)
        tempos_validos = [metrica.tempo_medio_deteccao for metrica in metricas_do_algoritmo if metrica.tempo_medio_deteccao is not None]
        tempo_medio_geral = sum(tempos_validos) / len(tempos_validos) if tempos_validos else None

        with coluna:
            st.markdown(f"##### {algoritmo.replace('_', ' ').title()}")
            st.metric(label = "Verdadeiros positivos", value = total_verdadeiros_positivos)
            st.metric(label = "Falsos positivos", value = total_falsos_positivos)
            st.metric(label = "Falsos negativos", value = total_falsos_negativos)
            st.metric(label = "Tempo médio de detecção (s)", value = round(tempo_medio_geral, 2) if tempo_medio_geral is not None else "-")
