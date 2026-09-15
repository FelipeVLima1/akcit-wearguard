import numpy as np
from src.config import FaixaClinica


def gerar_sinal_base(faixa: FaixaClinica, numero_leituras: int, semente: int) -> np.ndarray:
    """Gera uma série temporal estável dentro da faixa de normalidade de um sinal vital."""
    gerador = np.random.default_rng(seed = semente)
    centro = (faixa.minimo_normal + faixa.maximo_normal) / 2
    margem = (faixa.maximo_normal - faixa.minimo_normal) / 4
    return gerador.uniform(low = centro - margem, high = centro + margem, size = numero_leituras)
