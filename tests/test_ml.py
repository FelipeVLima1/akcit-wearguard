import numpy as np
from src.ml.avaliacao import avaliar_modelo
from src.ml.modelo import treinar_modelo


def montar_dados_sinteticos_separaveis() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    gerador = np.random.default_rng(seed = 1)
    centros = {"normal": 0.0, "supraventricular": 5.0, "ventricular": 10.0, "fusao": 15.0, "desconhecido": 20.0}

    segmentos = []
    classes = []
    for classe, centro in centros.items():
        for _ in range(40):
            segmentos.append(gerador.normal(loc = centro, scale = 0.2, size = 20))
            classes.append(classe)

    x = np.array(segmentos)
    y = np.array(classes)
    metade = len(y) // 2
    indices = gerador.permutation(len(y))
    indices_treino, indices_teste = indices[:metade], indices[metade:]
    return x[indices_treino], y[indices_treino], x[indices_teste], y[indices_teste]


def test_modelo_treina_e_classifica_bem_dados_bem_separados():
    x_treino, y_treino, x_teste, y_teste = montar_dados_sinteticos_separaveis()
    modelo = treinar_modelo(x_treino, y_treino)
    resultado = avaliar_modelo(modelo, x_teste, y_teste)

    assert resultado["acuracia"] > 0.9
    assert resultado["macro_f1"] > 0.9
    assert len(resultado["metricas_por_classe"]) == 5
    assert resultado["matriz_confusao"].shape == (5, 5)
