import pandas as pd
from src.modelos import AlertaClassificado

NOMES_COLUNAS = {"algoritmo": "Algoritmo", "sinal": "Sinal", "tipo_evento": "Tipo de evento", "leitura_indice": "Leitura", "classificacao": "Classificação"}


def montar_tabela_alertas(alertas: list[AlertaClassificado]) -> pd.DataFrame:
    """Monta uma tabela com todos os alertas emitidos, pronta para exibição no dashboard."""
    linhas = [alerta.model_dump() for alerta in alertas]
    tabela = pd.DataFrame(linhas)
    if tabela.empty:
        return tabela
    return tabela.rename(columns = NOMES_COLUNAS).sort_values(by = ["Algoritmo", "Sinal", "Leitura"]).reset_index(drop = True)
