import streamlit as st
from front.estilo.tema import CORES, montar_cartao_html
from src.modelos import EventoGabarito


def exibir_cartoes_status(execucao_id: int, criado_em: str, parametros: dict, gabarito: list[EventoGabarito]) -> None:
    """Exibe um resumo colorido da execução selecionada: id, parâmetros usados e eventos no gabarito."""
    tipos_de_evento = sorted({evento.tipo_evento for evento in gabarito})
    legenda_tipos = ", ".join(tipo.title() for tipo in tipos_de_evento) if tipos_de_evento else "-"

    cartoes = [
        ("Execução", f"#{execucao_id}", CORES["destaque"], criado_em),
        ("Leituras simuladas", str(parametros.get("duracao_total_leituras", "-")), CORES["texto_suave"], f"{parametros.get('intervalo_leitura_segundos', '-')} s por leitura"),
        ("Desvio padrão do ruído", str(parametros.get("desvio_padrao_ruido", "-")), CORES["limiar_simples"], f"semente {parametros.get('semente_aleatoria', '-')}"),
        ("Leituras p/ confirmar alerta", str(parametros.get("leituras_consecutivas_para_alerta", "-")), CORES["persistencia"], "critério de persistência"),
        ("Eventos no gabarito", str(len(gabarito)), CORES["evento_forte"], legenda_tipos),
    ]

    colunas = st.columns(len(cartoes))
    for coluna, (label, valor, cor, legenda) in zip(colunas, cartoes):
        with coluna:
            st.markdown(montar_cartao_html(label = label, valor = valor, cor = cor, legenda = legenda), unsafe_allow_html = True)
