import numpy as np
from src.config import FREQUENCIA_CARDIACA, ParametrosDeteccao
from src.deteccao.limiar_simples import detectar_limiar_simples
from src.deteccao.persistencia import detectar_persistencia


def test_limiar_simples_dispara_em_um_unico_pico_de_ruido():
    sinal = np.full(shape = 20, fill_value = 80.0)
    sinal[10] = 105.0
    alertas = detectar_limiar_simples(sinal = sinal, faixa = FREQUENCIA_CARDIACA)
    assert len(alertas) == 1
    assert alertas[0].leitura_indice == 10
    assert alertas[0].tipo_evento == "taquicardia"


def test_persistencia_ignora_um_unico_pico_de_ruido():
    sinal = np.full(shape = 20, fill_value = 80.0)
    sinal[10] = 105.0
    parametros = ParametrosDeteccao(leituras_consecutivas_para_alerta = 5)
    alertas = detectar_persistencia(sinal = sinal, faixa = FREQUENCIA_CARDIACA, parametros = parametros)
    assert alertas == []


def test_persistencia_dispara_uma_vez_apos_evento_real():
    sinal = np.full(shape = 20, fill_value = 80.0)
    sinal[5:15] = 110.0
    parametros = ParametrosDeteccao(leituras_consecutivas_para_alerta = 5)
    alertas = detectar_persistencia(sinal = sinal, faixa = FREQUENCIA_CARDIACA, parametros = parametros)
    assert len(alertas) == 1
    assert alertas[0].leitura_indice == 9
    assert alertas[0].tipo_evento == "taquicardia"


def test_persistencia_detecta_evento_baixo():
    sinal = np.full(shape = 20, fill_value = 80.0)
    sinal[3:12] = 50.0
    parametros = ParametrosDeteccao(leituras_consecutivas_para_alerta = 5)
    alertas = detectar_persistencia(sinal = sinal, faixa = FREQUENCIA_CARDIACA, parametros = parametros)
    assert len(alertas) == 1
    assert alertas[0].tipo_evento == "bradicardia"
