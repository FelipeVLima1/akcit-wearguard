import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import streamlit as st
from front.componentes.barra_lateral import selecionar_execucao
from front.componentes.cartoes_metricas import exibir_cartoes_metricas
from front.componentes.grafico_sinais import montar_grafico_sinal
from front.componentes.tabela_alertas import montar_tabela_alertas
from front.dados.consultas import obter_alertas, obter_gabarito, obter_leituras, obter_metricas
from front.estilo.tema import CSS_PERSONALIZADO
from src.config import FAIXAS_CLINICAS
from src.modelos import AlertaClassificado, EventoGabarito, Metrica


def configurar_pagina() -> None:
    """Define título e layout da página e aplica o CSS personalizado do dashboard."""
    st.set_page_config(page_title = "WearGuard", layout = "wide")
    st.markdown(CSS_PERSONALIZADO, unsafe_allow_html = True)


def exibir_cabecalho() -> None:
    """Exibe o título e a descrição curta do dashboard."""
    st.title("WearGuard")
    st.caption("Comparação entre detecção por limiar simples e por critério de persistência em sinais vitais simulados")


def exibir_aba_visao_geral(leituras: dict[str, np.ndarray], gabarito: list[EventoGabarito], alertas: list[AlertaClassificado]) -> None:
    """Mostra o gráfico de cada sinal vital com a faixa normal, os eventos reais e os alertas emitidos."""
    st.subheader("Sinais vitais simulados")
    for faixa in FAIXAS_CLINICAS:
        if faixa.nome in leituras:
            figura = montar_grafico_sinal(faixa = faixa, valores = leituras[faixa.nome], eventos = gabarito, alertas = alertas)
            st.pyplot(figura)


def exibir_aba_alertas(alertas: list[AlertaClassificado]) -> None:
    """Mostra a tabela com todos os alertas emitidos pelos dois algoritmos."""
    st.subheader("Alertas emitidos")
    tabela = montar_tabela_alertas(alertas)
    if tabela.empty:
        st.info("Nenhum alerta emitido nesta execução.")
        return
    st.dataframe(tabela, use_container_width = True, hide_index = True)


def exibir_aba_metricas(metricas: list[Metrica]) -> None:
    """Mostra os cartões de resumo e a tabela detalhada de métricas por tipo de evento."""
    st.subheader("Desempenho comparado dos algoritmos")
    exibir_cartoes_metricas(metricas)
    st.divider()
    st.subheader("Detalhamento por tipo de evento")
    linhas = [metrica.model_dump() for metrica in metricas]
    st.dataframe(pd.DataFrame(linhas), use_container_width = True, hide_index = True)


def main() -> None:
    """Monta o dashboard completo do WearGuard."""
    configurar_pagina()
    exibir_cabecalho()

    execucao_id = selecionar_execucao()
    if execucao_id is None:
        return

    leituras = obter_leituras(execucao_id)
    gabarito = obter_gabarito(execucao_id)
    alertas = obter_alertas(execucao_id)
    metricas = obter_metricas(execucao_id)

    aba_visao_geral, aba_alertas, aba_metricas = st.tabs(["Visão geral", "Alertas", "Métricas"])
    with aba_visao_geral:
        exibir_aba_visao_geral(leituras, gabarito, alertas)
    with aba_alertas:
        exibir_aba_alertas(alertas)
    with aba_metricas:
        exibir_aba_metricas(metricas)


if __name__ == "__main__":
    main()
