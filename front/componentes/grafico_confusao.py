import matplotlib.figure
import matplotlib.pyplot as plt
import pandas as pd
from src.ml.config import CLASSES


def montar_grafico_matriz_confusao(matriz_confusao: pd.DataFrame) -> matplotlib.figure.Figure:
    """Monta um mapa de calor da matriz de confusão do modelo de machine learning."""
    tabela_pivotada = matriz_confusao.pivot(index = "classe_real", columns = "classe_prevista", values = "quantidade").reindex(index = CLASSES, columns = CLASSES, fill_value = 0)

    figura, eixo = plt.subplots(figsize = (5.5, 4.5))
    imagem = eixo.imshow(tabela_pivotada.values, cmap = "Blues")

    eixo.set_xticks(range(len(CLASSES)))
    eixo.set_yticks(range(len(CLASSES)))
    eixo.set_xticklabels([classe.title() for classe in CLASSES], rotation = 35, ha = "right")
    eixo.set_yticklabels([classe.title() for classe in CLASSES])
    eixo.set_xlabel("Classe prevista pelo modelo")
    eixo.set_ylabel("Classe real (anotação médica)")

    valor_maximo = tabela_pivotada.values.max() if tabela_pivotada.values.size else 0
    for linha in range(len(CLASSES)):
        for coluna in range(len(CLASSES)):
            valor = tabela_pivotada.values[linha][coluna]
            cor_texto = "white" if valor > valor_maximo / 2 else "black"
            eixo.text(coluna, linha, str(valor), ha = "center", va = "center", color = cor_texto, fontsize = 9)

    figura.colorbar(imagem, ax = eixo, shrink = 0.8, label = "Quantidade de batimentos")
    figura.tight_layout()
    return figura
