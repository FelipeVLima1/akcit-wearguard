import streamlit as st
from front.estilo.tema import CORES, montar_cartao_html


def exibir_cartoes_ml(resultado: dict) -> None:
    """Exibe cards com o resumo do treinamento de machine learning mais recente."""
    cartoes = [
        ("Modelo", resultado["algoritmo"].replace("_", " ").title(), CORES["destaque"], resultado["criado_em"]),
        ("Acurácia geral", f"{resultado['acuracia'] * 100:.1f}%", CORES["persistencia"], "batimentos corretos no teste"),
        ("Macro-F1", f"{resultado['macro_f1']:.3f}", CORES["limiar_simples"], "média entre as 5 classes, sem viés de classe majoritária"),
        ("Batimentos de treino", f"{resultado['total_batimentos_treino']:,}".replace(",", "."), CORES["texto_suave"], "22 pacientes (split DS1)"),
        ("Batimentos de teste", f"{resultado['total_batimentos_teste']:,}".replace(",", "."), CORES["evento_forte"], "22 pacientes diferentes (split DS2)"),
    ]

    colunas = st.columns(len(cartoes))
    for coluna, (label, valor, cor, legenda) in zip(colunas, cartoes):
        with coluna:
            st.markdown(montar_cartao_html(label = label, valor = valor, cor = cor, legenda = legenda), unsafe_allow_html = True)
