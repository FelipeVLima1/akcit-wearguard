import streamlit as st
from src.modelos import EventoGabarito


def exibir_cartoes_status(execucao_id: int, criado_em: str, parametros: dict, gabarito: list[EventoGabarito]) -> None:
    """Exibe um resumo da execução selecionada: id, parâmetros usados e eventos no gabarito."""
    tipos_de_evento = sorted({evento.tipo_evento for evento in gabarito})

    coluna_execucao, coluna_leituras, coluna_ruido, coluna_persistencia, coluna_eventos = st.columns(5)

    with coluna_execucao:
        st.metric(label = "Execução", value = f"#{execucao_id}")
        st.caption(criado_em)

    with coluna_leituras:
        st.metric(label = "Leituras simuladas", value = parametros.get("duracao_total_leituras", "-"))
        st.caption(f"{parametros.get('intervalo_leitura_segundos', '-')} s por leitura")

    with coluna_ruido:
        st.metric(label = "Desvio padrão do ruído", value = parametros.get("desvio_padrao_ruido", "-"))
        st.caption(f"semente {parametros.get('semente_aleatoria', '-')}")

    with coluna_persistencia:
        st.metric(label = "Leituras p/ confirmar alerta", value = parametros.get("leituras_consecutivas_para_alerta", "-"))
        st.caption("critério de persistência")

    with coluna_eventos:
        st.metric(label = "Eventos no gabarito", value = len(gabarito))
        st.caption(", ".join(tipo.title() for tipo in tipos_de_evento) if tipos_de_evento else "-")
