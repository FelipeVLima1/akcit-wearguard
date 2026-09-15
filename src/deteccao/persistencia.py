import numpy as np
from src.config import FaixaClinica, ParametrosDeteccao
from src.modelos import Alerta

NOME_ALGORITMO = "persistencia"


def detectar_persistencia(sinal: np.ndarray, faixa: FaixaClinica, parametros: ParametrosDeteccao) -> list[Alerta]:
    """Emite um alerta somente após N leituras consecutivas fora da faixa de normalidade."""
    alertas: list[Alerta] = []
    contador_alto = 0
    contador_baixo = 0

    for indice, valor in enumerate(sinal):
        fora_do_limite_alto = faixa.limite_alerta_alto is not None and valor > faixa.limite_alerta_alto
        fora_do_limite_baixo = faixa.limite_alerta_baixo is not None and valor < faixa.limite_alerta_baixo

        contador_alto = contador_alto + 1 if fora_do_limite_alto else 0
        contador_baixo = contador_baixo + 1 if fora_do_limite_baixo else 0

        if contador_alto == parametros.leituras_consecutivas_para_alerta:
            alertas.append(Alerta(algoritmo = NOME_ALGORITMO, sinal = faixa.nome, tipo_evento = faixa.evento_alto, leitura_indice = indice))
        if contador_baixo == parametros.leituras_consecutivas_para_alerta:
            alertas.append(Alerta(algoritmo = NOME_ALGORITMO, sinal = faixa.nome, tipo_evento = faixa.evento_baixo, leitura_indice = indice))

    return alertas
