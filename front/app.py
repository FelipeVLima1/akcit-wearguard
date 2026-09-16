import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import streamlit as st
from front.componentes.barra_lateral import selecionar_execucao
from front.componentes.cartoes_metricas import exibir_cartoes_metricas
from front.componentes.cartoes_status import exibir_cartoes_status
from front.componentes.grafico_sinais import montar_grafico_sinal
from front.componentes.tabela_alertas import montar_tabela_alertas
from front.dados.consultas import obter_alertas, obter_execucao, obter_gabarito, obter_leituras, obter_metricas, obter_parametros
from front.dados.derivadas import montar_resumo_comparativo
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
    """Mostra os três sinais vitais lado a lado, com a faixa normal, os eventos reais e os alertas emitidos."""
    st.subheader("Sinais vitais simulados")
    st.caption("Área azul: faixa normal. Área vermelha: evento real inserido. Círculo laranja: alerta do limiar simples. Losango verde: alerta da persistência.")

    colunas = st.columns(len(FAIXAS_CLINICAS))
    for coluna, faixa in zip(colunas, FAIXAS_CLINICAS):
        with coluna:
            if faixa.nome in leituras:
                figura = montar_grafico_sinal(faixa = faixa, valores = leituras[faixa.nome], eventos = gabarito, alertas = alertas)
                st.pyplot(figura, use_container_width = True)


def exibir_aba_alertas(alertas: list[AlertaClassificado]) -> None:
    """Mostra a tabela com todos os alertas emitidos pelos dois algoritmos, com filtros básicos."""
    st.subheader("Alertas emitidos")
    tabela = montar_tabela_alertas(alertas)
    if tabela.empty:
        st.info("Nenhum alerta emitido nesta execução.")
        return

    coluna_algoritmo, coluna_classificacao = st.columns(2)
    with coluna_algoritmo:
        algoritmos_escolhidos = st.multiselect(label = "Algoritmo", options = sorted(tabela["Algoritmo"].unique()), default = sorted(tabela["Algoritmo"].unique()))
    with coluna_classificacao:
        classificacoes_escolhidas = st.multiselect(label = "Classificação", options = sorted(tabela["Classificação"].unique()), default = sorted(tabela["Classificação"].unique()))

    tabela_filtrada = tabela[tabela["Algoritmo"].isin(algoritmos_escolhidos) & tabela["Classificação"].isin(classificacoes_escolhidas)]
    st.dataframe(tabela_filtrada, use_container_width = True, hide_index = True)
    st.caption(f"{len(tabela_filtrada)} de {len(tabela)} alertas exibidos")


def exibir_aba_metricas(metricas: list[Metrica]) -> None:
    """Mostra os cartões de resumo, o comparativo lado a lado e a tabela detalhada de métricas."""
    st.subheader("Desempenho comparado dos algoritmos")
    exibir_cartoes_metricas(metricas)

    st.divider()
    st.subheader("Comparativo por tipo de evento")
    st.caption("Redução de FP (%) mostra o quanto a persistência diminuiu os falsos positivos em relação ao limiar simples nesse tipo de evento.")
    st.dataframe(montar_resumo_comparativo(metricas), use_container_width = True, hide_index = True)

    st.divider()
    st.subheader("Métricas completas por algoritmo e tipo de evento")
    linhas = [metrica.model_dump() for metrica in metricas]
    st.dataframe(pd.DataFrame(linhas), use_container_width = True, hide_index = True)


def main() -> None:
    """Monta o dashboard completo do WearGuard."""
    configurar_pagina()
    exibir_cabecalho()

    execucao_id = selecionar_execucao()
    if execucao_id is None:
        return

    execucao = obter_execucao(execucao_id)
    parametros = obter_parametros(execucao_id)
    leituras = obter_leituras(execucao_id)
    gabarito = obter_gabarito(execucao_id)
    alertas = obter_alertas(execucao_id)
    metricas = obter_metricas(execucao_id)

    exibir_cartoes_status(execucao_id = execucao_id, criado_em = execucao[1] if execucao else "-", parametros = parametros, gabarito = gabarito)
    st.divider()

    aba_visao_geral, aba_alertas, aba_metricas = st.tabs(["Visão geral", "Alertas", "Métricas"])
    with aba_visao_geral:
        exibir_aba_visao_geral(leituras, gabarito, alertas)
    with aba_alertas:
        exibir_aba_alertas(alertas)
    with aba_metricas:
        exibir_aba_metricas(metricas)


if __name__ == "__main__":
    main()
