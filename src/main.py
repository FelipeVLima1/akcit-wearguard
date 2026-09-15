from src.config import ParametrosDeteccao, ParametrosSimulacao
from src.grafo.estado import EstadoWearGuard
from src.grafo.pipeline import montar_grafo
from src.logger import criar_logger

logger = criar_logger(nome = "wearguard.main")


def executar_pipeline() -> EstadoWearGuard:
    """Roda o pipeline completo do WearGuard do início ao fim e retorna o estado final."""
    grafo = montar_grafo()
    estado_inicial: EstadoWearGuard = {"parametros_simulacao": ParametrosSimulacao(), "parametros_deteccao": ParametrosDeteccao()}
    return grafo.invoke(estado_inicial)


def imprimir_resumo(estado_final: EstadoWearGuard) -> None:
    """Imprime um resumo legível das métricas obtidas na execução."""
    print(f"Execucao {estado_final['execucao_id']} concluida")
    print(f"Total de eventos no gabarito: {len(estado_final['gabarito'])}")
    for metrica in estado_final["metricas"]:
        print(f"[{metrica.algoritmo}] {metrica.tipo_evento}: VP={metrica.verdadeiros_positivos} FP={metrica.falsos_positivos} FN={metrica.falsos_negativos} tempo_medio_deteccao={metrica.tempo_medio_deteccao}")


if __name__ == "__main__":
    estado_final = executar_pipeline()
    imprimir_resumo(estado_final)
