from src.ml.avaliacao import avaliar_modelo
from src.ml.dados import preparar_conjuntos_treino_teste
from src.ml.database import criar_esquema_ml, salvar_resultado_ml
from src.ml.modelo import NOME_MODELO, salvar_modelo, treinar_modelo
from src.logger import criar_logger

logger = criar_logger(nome = "wearguard.ml")


def executar_treinamento() -> dict:
    """Extrai os batimentos do MIT-BIH, treina o classificador, avalia e persiste o resultado."""
    criar_esquema_ml()

    x_treino, y_treino, x_teste, y_teste = preparar_conjuntos_treino_teste()
    logger.info("batimentos de treino: %s, batimentos de teste: %s", len(y_treino), len(y_teste))

    modelo = treinar_modelo(x_treino, y_treino)
    salvar_modelo(modelo)

    resultado = avaliar_modelo(modelo, x_teste, y_teste)
    modelo_id = salvar_resultado_ml(algoritmo = NOME_MODELO, resultado = resultado, total_batimentos_treino = len(y_treino), total_batimentos_teste = len(y_teste))
    logger.info("modelo %s salvo com acuracia %.3f e macro-f1 %.3f", modelo_id, resultado["acuracia"], resultado["macro_f1"])

    return resultado


def imprimir_resumo(resultado: dict) -> None:
    """Imprime um resumo legível do desempenho do modelo treinado."""
    print(f"Acuracia geral: {resultado['acuracia']:.3f}")
    print(f"Macro-F1: {resultado['macro_f1']:.3f}")
    for metrica in resultado["metricas_por_classe"]:
        print(f"[{metrica['classe']}] precisao={metrica['precisao']:.3f} recall={metrica['recall']:.3f} f1={metrica['f1']:.3f} suporte={metrica['suporte']}")


if __name__ == "__main__":
    resultado = executar_treinamento()
    imprimir_resumo(resultado)
