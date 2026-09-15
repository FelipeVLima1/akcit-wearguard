from src.config import FREQUENCIA_CARDIACA, SPO2, ParametrosSimulacao
from src.simulador.gerador_sinais import gerar_sinal_base
from src.simulador.eventos import inserir_eventos


def test_inserir_eventos_gera_o_numero_esperado_de_eventos():
    parametros = ParametrosSimulacao(duracao_total_leituras = 400, duracao_evento_leituras = 20, numero_eventos_por_tipo = 3)
    sinal = gerar_sinal_base(faixa = FREQUENCIA_CARDIACA, numero_leituras = 400, semente = 1)
    _, eventos = inserir_eventos(sinal = sinal, faixa = FREQUENCIA_CARDIACA, parametros = parametros, semente = 2)
    tipos_encontrados = {evento.tipo_evento for evento in eventos}
    assert tipos_encontrados == {"taquicardia", "bradicardia"}
    assert len(eventos) == 6


def test_evento_alto_ultrapassa_o_limite_de_alerta():
    parametros = ParametrosSimulacao(duracao_total_leituras = 300, duracao_evento_leituras = 15, numero_eventos_por_tipo = 2)
    sinal = gerar_sinal_base(faixa = FREQUENCIA_CARDIACA, numero_leituras = 300, semente = 1)
    sinal_modificado, eventos = inserir_eventos(sinal = sinal, faixa = FREQUENCIA_CARDIACA, parametros = parametros, semente = 3)
    eventos_taquicardia = [evento for evento in eventos if evento.tipo_evento == "taquicardia"]
    for evento in eventos_taquicardia:
        trecho = sinal_modificado[evento.leitura_inicio:evento.leitura_fim]
        assert (trecho > FREQUENCIA_CARDIACA.limite_alerta_alto).all()


def test_sinal_sem_evento_baixo_configurado_nao_gera_evento_baixo():
    parametros = ParametrosSimulacao(duracao_total_leituras = 300, duracao_evento_leituras = 15, numero_eventos_por_tipo = 2)
    sinal = gerar_sinal_base(faixa = SPO2, numero_leituras = 300, semente = 1)
    _, eventos = inserir_eventos(sinal = sinal, faixa = SPO2, parametros = parametros, semente = 4)
    tipos_encontrados = {evento.tipo_evento for evento in eventos}
    assert tipos_encontrados == {"hipoxia"}
