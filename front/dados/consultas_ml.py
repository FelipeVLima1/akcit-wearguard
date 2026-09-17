import pandas as pd
from src.ml.database import obter_matriz_confusao_ml, obter_metricas_ml, obter_ultimo_modelo_ml


def obter_ultimo_resultado_ml() -> dict | None:
    """Recupera o treinamento de ML mais recente, com métricas por classe e matriz de confusão."""
    modelo = obter_ultimo_modelo_ml()
    if modelo is None:
        return None

    metricas = obter_metricas_ml(modelo["id"])
    matriz = obter_matriz_confusao_ml(modelo["id"])

    return {
        "id": modelo["id"],
        "criado_em": modelo["criado_em"],
        "algoritmo": modelo["algoritmo"],
        "acuracia": modelo["acuracia"],
        "macro_f1": modelo["macro_f1"],
        "total_batimentos_treino": modelo["total_batimentos_treino"],
        "total_batimentos_teste": modelo["total_batimentos_teste"],
        "metricas_por_classe": pd.DataFrame([dict(linha) for linha in metricas]),
        "matriz_confusao": pd.DataFrame([dict(linha) for linha in matriz]),
    }
