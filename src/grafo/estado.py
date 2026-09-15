from typing import TypedDict
import numpy as np
from src.config import ParametrosDeteccao, ParametrosSimulacao
from src.modelos import Alerta, AlertaClassificado, EventoGabarito, Metrica


class EstadoWearGuard(TypedDict, total = False):
    """Estado compartilhado entre os nós do grafo LangGraph do pipeline WearGuard."""
    parametros_simulacao: ParametrosSimulacao
    parametros_deteccao: ParametrosDeteccao
    sinais_base: dict[str, np.ndarray]
    sinais_com_ruido: dict[str, np.ndarray]
    sinais_finais: dict[str, np.ndarray]
    gabarito: list[EventoGabarito]
    alertas_limiar_simples: list[Alerta]
    alertas_persistencia: list[Alerta]
    alertas_classificados: list[AlertaClassificado]
    eventos_nao_detectados_limiar_simples: list[EventoGabarito]
    eventos_nao_detectados_persistencia: list[EventoGabarito]
    metricas: list[Metrica]
    execucao_id: int
