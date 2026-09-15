import numpy as np


def injetar_ruido(sinal: np.ndarray, desvio_padrao: float, semente: int) -> np.ndarray:
    """Aplica ruído gaussiano ao sinal, simulando oscilações naturais de sensores."""
    gerador = np.random.default_rng(seed = semente)
    ruido = gerador.normal(loc = 0, scale = desvio_padrao, size = sinal.shape)
    return sinal + ruido
