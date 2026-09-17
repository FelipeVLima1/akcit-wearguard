import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from src.ml.config import CAMINHO_MODELO

NOME_MODELO = "random_forest"


def treinar_modelo(x_treino: np.ndarray, y_treino: np.ndarray) -> RandomForestClassifier:
    """Treina um Random Forest para classificar batimentos cardíacos nas 5 categorias AAMI."""
    modelo = RandomForestClassifier(n_estimators = 200, class_weight = "balanced", random_state = 42, n_jobs = -1)
    modelo.fit(x_treino, y_treino)
    return modelo


def salvar_modelo(modelo: RandomForestClassifier) -> None:
    """Salva o modelo treinado em disco para uso posterior sem precisar retreinar."""
    CAMINHO_MODELO.parent.mkdir(parents = True, exist_ok = True)
    joblib.dump(modelo, CAMINHO_MODELO)


def carregar_modelo() -> RandomForestClassifier:
    """Carrega o modelo treinado salvo em disco."""
    return joblib.load(CAMINHO_MODELO)
