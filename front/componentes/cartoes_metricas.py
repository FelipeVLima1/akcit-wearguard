import streamlit as st
from front.dados.derivadas import calcular_indicadores_por_algoritmo
from src.modelos import Metrica


def exibir_cartoes_metricas(metricas: list[Metrica]) -> None:
    """Exibe cartões resumo comparando o desempenho geral de cada algoritmo."""
    indicadores = calcular_indicadores_por_algoritmo(metricas)
    colunas = st.columns(len(indicadores)) if indicadores else []

    for coluna, (algoritmo, valores) in zip(colunas, indicadores.items()):
        with coluna:
            st.markdown(f"##### {algoritmo.replace('_', ' ').title()}")
            linha_1, linha_2 = st.columns(2), st.columns(2)

            with linha_1[0]:
                st.metric(label = "Verdadeiros positivos", value = valores["verdadeiros_positivos"])
            with linha_1[1]:
                st.metric(label = "Falsos positivos", value = valores["falsos_positivos"])
            with linha_2[0]:
                st.metric(label = "Falsos negativos", value = valores["falsos_negativos"])
            with linha_2[1]:
                st.metric(label = "Tempo médio (s)", value = valores["tempo_medio_deteccao"] if valores["tempo_medio_deteccao"] is not None else "-")

            st.progress(value = valores["precisao"] or 0.0, text = f"Precisão: {valores['precisao'] if valores['precisao'] is not None else '-'}")
            st.caption(f"Taxa de falsos positivos sobre os alertas emitidos: {valores['taxa_falsos_positivos'] if valores['taxa_falsos_positivos'] is not None else '-'}")
