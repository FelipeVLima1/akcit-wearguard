from src.config import ParametrosDeteccao, ParametrosSimulacao
from src.grafo.estado import EstadoWearGuard
from src.grafo.pipeline import montar_grafo


def test_pipeline_completo_produz_gabarito_alertas_e_metricas():
    grafo = montar_grafo()
    estado_inicial: EstadoWearGuard = {"parametros_simulacao": ParametrosSimulacao(), "parametros_deteccao": ParametrosDeteccao()}
    estado_final = grafo.invoke(estado_inicial)

    assert estado_final["execucao_id"] is not None
    assert len(estado_final["gabarito"]) > 0
    assert len(estado_final["alertas_limiar_simples"]) > 0
    assert len(estado_final["alertas_persistencia"]) > 0
    assert len(estado_final["metricas"]) == 8


def test_persistencia_gera_menos_ou_igual_falsos_positivos_que_limiar_simples():
    grafo = montar_grafo()
    estado_inicial: EstadoWearGuard = {"parametros_simulacao": ParametrosSimulacao(), "parametros_deteccao": ParametrosDeteccao()}
    estado_final = grafo.invoke(estado_inicial)

    total_fp_limiar_simples = sum(metrica.falsos_positivos for metrica in estado_final["metricas"] if metrica.algoritmo == "limiar_simples")
    total_fp_persistencia = sum(metrica.falsos_positivos for metrica in estado_final["metricas"] if metrica.algoritmo == "persistencia")
    assert total_fp_persistencia <= total_fp_limiar_simples
