import numpy as np
from src.config import FaixaClinica
from src.modelos import Alerta

NOME_ALGORITMO = "limiar_simples"


def detectar_limiar_simples(sinal: np.ndarray, faixa: FaixaClinica) -> list[Alerta]:
    """Emite um alerta imediato em toda leitura que ultrapassa o limite clínico, sem exigir persistência."""
    alertas: list[Alerta] = []
    for indice, valor in enumerate(sinal):
        if faixa.limite_alerta_alto is not None and valor > faixa.limite_alerta_alto:
            alertas.append(Alerta(algoritmo = NOME_ALGORITMO, sinal = faixa.nome, tipo_evento = faixa.evento_alto, leitura_indice = indice))
        elif faixa.limite_alerta_baixo is not None and valor < faixa.limite_alerta_baixo:
            alertas.append(Alerta(algoritmo = NOME_ALGORITMO, sinal = faixa.nome, tipo_evento = faixa.evento_baixo, leitura_indice = indice))
    return alertas
