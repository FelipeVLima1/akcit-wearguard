from src.avaliacao.comparador import classificar_alertas, listar_eventos_nao_detectados
from src.avaliacao.metricas import calcular_metricas
from src.modelos import Alerta, EventoGabarito


def montar_cenario():
    eventos = [EventoGabarito(sinal = "frequencia_cardiaca", tipo_evento = "taquicardia", leitura_inicio = 10, leitura_fim = 20)]
    alertas = [
        Alerta(algoritmo = "limiar_simples", sinal = "frequencia_cardiaca", tipo_evento = "taquicardia", leitura_indice = 3),
        Alerta(algoritmo = "limiar_simples", sinal = "frequencia_cardiaca", tipo_evento = "taquicardia", leitura_indice = 12),
    ]
    return eventos, alertas


def test_classificar_alertas_identifica_verdadeiro_e_falso_positivo():
    eventos, alertas = montar_cenario()
    alertas_classificados = classificar_alertas(alertas = alertas, eventos = eventos)
    classificacoes = {alerta.leitura_indice: alerta.classificacao for alerta in alertas_classificados}
    assert classificacoes[3] == "falso_positivo"
    assert classificacoes[12] == "verdadeiro_positivo"


def test_listar_eventos_nao_detectados_fica_vazio_quando_ha_alerta_dentro_do_evento():
    eventos, alertas = montar_cenario()
    eventos_nao_detectados = listar_eventos_nao_detectados(alertas = alertas, eventos = eventos)
    assert eventos_nao_detectados == []


def test_listar_eventos_nao_detectados_encontra_falso_negativo():
    eventos = [EventoGabarito(sinal = "frequencia_cardiaca", tipo_evento = "bradicardia", leitura_inicio = 50, leitura_fim = 60)]
    eventos_nao_detectados = listar_eventos_nao_detectados(alertas = [], eventos = eventos)
    assert len(eventos_nao_detectados) == 1


def test_calcular_metricas_conta_tp_fp_fn_e_tempo_medio():
    eventos, alertas = montar_cenario()
    alertas_classificados = classificar_alertas(alertas = alertas, eventos = eventos)
    eventos_nao_detectados = listar_eventos_nao_detectados(alertas = alertas, eventos = eventos)
    metricas = calcular_metricas(algoritmo = "limiar_simples", alertas_classificados = alertas_classificados, eventos = eventos, eventos_nao_detectados = eventos_nao_detectados, intervalo_leitura_segundos = 1.0)
    assert len(metricas) == 1
    metrica = metricas[0]
    assert metrica.verdadeiros_positivos == 1
    assert metrica.falsos_positivos == 1
    assert metrica.falsos_negativos == 0
    assert metrica.tempo_medio_deteccao == 2.0
