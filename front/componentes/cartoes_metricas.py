import streamlit as st
from front.dados.derivadas import calcular_indicadores_por_algoritmo
from front.estilo.tema import CORES
from src.modelos import Metrica

COR_POR_ALGORITMO = {"limiar_simples": CORES["limiar_simples"], "persistencia": CORES["persistencia"]}


def exibir_cartao_algoritmo_regra(algoritmo: str, valores: dict) -> None:
    """Exibe o card de um algoritmo baseado em regra (limiar simples ou persistência)."""
    cor = COR_POR_ALGORITMO.get(algoritmo, CORES["destaque"])
    with st.container(border = True):
        st.markdown(f"<div style='border-left:5px solid {cor};padding-left:10px;'><strong>{algoritmo.replace('_', ' ').title()}</strong></div>", unsafe_allow_html = True)
        st.write("")

        linha_1 = st.columns(2)
        with linha_1[0]:
            st.metric(label = "Verdadeiros positivos", value = valores["verdadeiros_positivos"])
        with linha_1[1]:
            st.metric(label = "Falsos positivos", value = valores["falsos_positivos"])

        linha_2 = st.columns(2)
        with linha_2[0]:
            st.metric(label = "Falsos negativos", value = valores["falsos_negativos"])
        with linha_2[1]:
            st.metric(label = "Tempo médio (s)", value = valores["tempo_medio_deteccao"] if valores["tempo_medio_deteccao"] is not None else "-")

        st.progress(value = valores["precisao"] or 0.0, text = f"Precisão: {valores['precisao'] if valores['precisao'] is not None else '-'}")
        st.caption(f"Taxa de falsos positivos sobre os alertas emitidos: {valores['taxa_falsos_positivos'] if valores['taxa_falsos_positivos'] is not None else '-'}")


def exibir_cartao_machine_learning(resultado_ml: dict) -> None:
    """Exibe o card do classificador de arritmias (ECG real), no mesmo formato dos cards de regra."""
    total_treino = f"{resultado_ml['total_batimentos_treino']:,}".replace(",", ".")
    total_teste = f"{resultado_ml['total_batimentos_teste']:,}".replace(",", ".")

    with st.container(border = True):
        st.markdown(f"<div style='border-left:5px solid {CORES['destaque']};padding-left:10px;'><strong>Machine Learning</strong></div>", unsafe_allow_html = True)
        st.write("")

        linha_1 = st.columns(2)
        with linha_1[0]:
            st.metric(label = "Acurácia geral", value = f"{resultado_ml['acuracia'] * 100:.1f}%")
        with linha_1[1]:
            st.metric(label = "Macro-F1", value = f"{resultado_ml['macro_f1']:.3f}")

        linha_2 = st.columns(2)
        with linha_2[0]:
            st.metric(label = "Batimentos treino", value = total_treino)
        with linha_2[1]:
            st.metric(label = "Batimentos teste", value = total_teste)

        st.progress(value = resultado_ml["macro_f1"], text = f"Macro-F1: {resultado_ml['macro_f1']:.3f}")
        st.caption("Treinado com ECG real (MIT-BIH), em um problema diferente (5 classes de arritmia) — comparação apenas ilustrativa.")


def exibir_cartoes_metricas(metricas: list[Metrica], resultado_ml: dict | None = None) -> None:
    """Exibe, lado a lado, um card por algoritmo baseado em regra e, se disponível, o card de machine learning."""
    indicadores = calcular_indicadores_por_algoritmo(metricas)
    total_cartoes = len(indicadores) + (1 if resultado_ml is not None else 0)
    if total_cartoes == 0:
        return

    colunas = st.columns(total_cartoes)

    for coluna, (algoritmo, valores) in zip(colunas, indicadores.items()):
        with coluna:
            exibir_cartao_algoritmo_regra(algoritmo, valores)

    if resultado_ml is not None:
        with colunas[-1]:
            exibir_cartao_machine_learning(resultado_ml)
