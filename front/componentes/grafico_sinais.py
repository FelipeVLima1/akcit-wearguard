import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
from front.estilo.tema import CORES
from src.config import FaixaClinica
from src.modelos import AlertaClassificado, EventoGabarito


def montar_grafico_sinal(faixa: FaixaClinica, valores: np.ndarray, eventos: list[EventoGabarito], alertas: list[AlertaClassificado]) -> matplotlib.figure.Figure:
    """Monta o gráfico de um sinal vital com a faixa normal, os eventos reais e os alertas dos dois algoritmos."""
    figura, eixo = plt.subplots(figsize = (4.6, 3.2))

    eixo.axhspan(faixa.minimo_normal, faixa.maximo_normal, color = CORES["faixa_normal"], zorder = 0, label = "Faixa normal")

    eventos_do_sinal = [evento for evento in eventos if evento.sinal == faixa.nome]
    for evento in eventos_do_sinal:
        eixo.axvspan(evento.leitura_inicio, evento.leitura_fim, color = CORES["evento"], alpha = 0.6, zorder = 1)

    eixo.plot(valores, color = CORES["texto"], linewidth = 1, zorder = 2)

    alertas_limiar_simples = [alerta for alerta in alertas if alerta.sinal == faixa.nome and alerta.algoritmo == "limiar_simples"]
    alertas_persistencia = [alerta for alerta in alertas if alerta.sinal == faixa.nome and alerta.algoritmo == "persistencia"]

    if alertas_limiar_simples:
        indices = [alerta.leitura_indice for alerta in alertas_limiar_simples]
        eixo.scatter(indices, valores[indices], color = CORES["limiar_simples"], marker = "o", s = 18, zorder = 3, label = "Alerta limiar simples")

    if alertas_persistencia:
        indices = [alerta.leitura_indice for alerta in alertas_persistencia]
        eixo.scatter(indices, valores[indices], color = CORES["persistencia"], marker = "D", s = 36, zorder = 4, label = "Alerta persistência")

    eixo.set_title(f"{faixa.nome.replace('_', ' ').title()} ({faixa.unidade})", fontsize = 10)
    eixo.set_xlabel("Leitura", fontsize = 8)
    eixo.set_ylabel(faixa.unidade, fontsize = 8)
    eixo.tick_params(labelsize = 7)
    eixo.legend(loc = "upper right", fontsize = 6, framealpha = 0.9)
    figura.tight_layout()
    return figura
