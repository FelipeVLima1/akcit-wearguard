from langgraph.graph import END, StateGraph
from src.grafo.estado import EstadoWearGuard
from src.grafo.nos import no_calcular_metricas, no_comparar_com_gabarito, no_gerar_sinais_base, no_injetar_ruido, no_inserir_eventos, no_persistir_resultados, no_rodar_algoritmos


def montar_grafo():
    """Monta o grafo LangGraph que orquestra o pipeline completo do WearGuard."""
    grafo = StateGraph(EstadoWearGuard)

    grafo.add_node("gerar_sinais_base", no_gerar_sinais_base)
    grafo.add_node("injetar_ruido", no_injetar_ruido)
    grafo.add_node("inserir_eventos", no_inserir_eventos)
    grafo.add_node("rodar_algoritmos", no_rodar_algoritmos)
    grafo.add_node("comparar_com_gabarito", no_comparar_com_gabarito)
    grafo.add_node("calcular_metricas", no_calcular_metricas)
    grafo.add_node("persistir_resultados", no_persistir_resultados)

    grafo.set_entry_point("gerar_sinais_base")
    grafo.add_edge("gerar_sinais_base", "injetar_ruido")
    grafo.add_edge("injetar_ruido", "inserir_eventos")
    grafo.add_edge("inserir_eventos", "rodar_algoritmos")
    grafo.add_edge("rodar_algoritmos", "comparar_com_gabarito")
    grafo.add_edge("comparar_com_gabarito", "calcular_metricas")
    grafo.add_edge("calcular_metricas", "persistir_resultados")
    grafo.add_edge("persistir_resultados", END)

    return grafo.compile()
