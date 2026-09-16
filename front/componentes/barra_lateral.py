import streamlit as st
from front.dados.consultas import listar_execucoes
from src.main import executar_pipeline


def selecionar_execucao() -> int | None:
    """Monta a barra lateral com o botão de nova simulação e a lista de execuções salvas."""
    st.sidebar.title("WearGuard")
    st.sidebar.caption("Monitoramento remoto: limiar simples vs. critério de persistência")

    if st.sidebar.button(label = "Rodar nova simulação", use_container_width = True):
        with st.spinner(text = "Rodando pipeline completo..."):
            executar_pipeline()
        st.rerun()

    st.sidebar.divider()

    execucoes = listar_execucoes()
    if not execucoes:
        st.sidebar.info("Nenhuma execução encontrada ainda. Rode uma simulação para começar.")
        return None

    opcoes = {f"Execução {execucao_id} — {criado_em}": execucao_id for execucao_id, criado_em in execucoes}
    escolha = st.sidebar.selectbox(label = "Execução", options = list(opcoes.keys()))
    return opcoes[escolha]
