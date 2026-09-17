import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, precision_recall_fscore_support
from src.ml.config import CLASSES


def avaliar_modelo(modelo: RandomForestClassifier, x_teste: np.ndarray, y_teste: np.ndarray) -> dict:
    """Avalia o modelo no conjunto de teste: acurácia, métricas por classe e matriz de confusão."""
    previsoes = modelo.predict(x_teste)
    acuracia = float((previsoes == y_teste).mean())

    precisao, recall, f1, suporte = precision_recall_fscore_support(y_teste, previsoes, labels = CLASSES, zero_division = 0)
    metricas_por_classe = [{"classe": classe, "precisao": float(precisao[indice]), "recall": float(recall[indice]), "f1": float(f1[indice]), "suporte": int(suporte[indice])} for indice, classe in enumerate(CLASSES)]

    matriz = confusion_matrix(y_teste, previsoes, labels = CLASSES)
    macro_f1 = float(np.mean([metrica["f1"] for metrica in metricas_por_classe]))

    return {"acuracia": acuracia, "macro_f1": macro_f1, "metricas_por_classe": metricas_por_classe, "matriz_confusao": matriz, "classes": CLASSES}
