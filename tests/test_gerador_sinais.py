from src.config import FREQUENCIA_CARDIACA
from src.simulador.gerador_sinais import gerar_sinal_base
from src.simulador.injetor_ruido import injetar_ruido


def test_sinal_base_fica_dentro_da_faixa_de_normalidade():
    sinal = gerar_sinal_base(faixa = FREQUENCIA_CARDIACA, numero_leituras = 200, semente = 1)
    assert sinal.min() >= FREQUENCIA_CARDIACA.minimo_normal
    assert sinal.max() <= FREQUENCIA_CARDIACA.maximo_normal


def test_sinal_base_tem_o_tamanho_pedido():
    sinal = gerar_sinal_base(faixa = FREQUENCIA_CARDIACA, numero_leituras = 50, semente = 1)
    assert len(sinal) == 50


def test_ruido_e_reprodutivel_com_a_mesma_semente():
    sinal = gerar_sinal_base(faixa = FREQUENCIA_CARDIACA, numero_leituras = 100, semente = 1)
    sinal_com_ruido_a = injetar_ruido(sinal = sinal, desvio_padrao = 0.5, semente = 7)
    sinal_com_ruido_b = injetar_ruido(sinal = sinal, desvio_padrao = 0.5, semente = 7)
    assert (sinal_com_ruido_a == sinal_com_ruido_b).all()
