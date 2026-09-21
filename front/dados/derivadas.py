import pandas as pd
from src.modelos import Metrica

NOME_LIMIAR_SIMPLES = "limiar_simples"
NOME_PERSISTENCIA = "persistencia"


def calcular_precisao(metrica: Metrica) -> float | None:
    """Calcula a precisão de um algoritmo: verdadeiros positivos sobre o total de alertas emitidos."""
    total_alertas = metrica.verdadeiros_positivos + metrica.falsos_positivos
    if total_alertas == 0:
        return None
    return round(metrica.verdadeiros_positivos / total_alertas, 3)


def calcular_indicadores_por_algoritmo(metricas: list[Metrica]) -> dict[str, dict]:
    """Agrega, por algoritmo, o total de VP/FP/FN, a precisão geral e o tempo médio de detecção."""
    indicadores: dict[str, dict] = {}
    for algoritmo in sorted({metrica.algoritmo for metrica in metricas}):
        metricas_do_algoritmo = [metrica for metrica in metricas if metrica.algoritmo == algoritmo]
        total_verdadeiros_positivos = sum(metrica.verdadeiros_positivos for metrica in metricas_do_algoritmo)
        total_falsos_positivos = sum(metrica.falsos_positivos for metrica in metricas_do_algoritmo)
        total_falsos_negativos = sum(metrica.falsos_negativos for metrica in metricas_do_algoritmo)
        total_alertas = total_verdadeiros_positivos + total_falsos_positivos

        tempos_validos = [metrica.tempo_medio_deteccao for metrica in metricas_do_algoritmo if metrica.tempo_medio_deteccao is not None]
        tempo_medio_geral = sum(tempos_validos) / len(tempos_validos) if tempos_validos else None

        total_eventos_reais = total_verdadeiros_positivos + total_falsos_negativos

        indicadores[algoritmo] = {
            "verdadeiros_positivos": total_verdadeiros_positivos,
            "falsos_positivos": total_falsos_positivos,
            "falsos_negativos": total_falsos_negativos,
            "precisao": round(total_verdadeiros_positivos / total_alertas, 3) if total_alertas > 0 else None,
            "taxa_falsos_positivos": round(total_falsos_positivos / total_alertas, 3) if total_alertas > 0 else None,
            "taxa_deteccao": round(total_verdadeiros_positivos / total_eventos_reais, 3) if total_eventos_reais > 0 else None,
            "tempo_medio_deteccao": round(tempo_medio_geral, 2) if tempo_medio_geral is not None else None,
        }
    return indicadores


def calcular_comparacao_binaria_ml(matriz_confusao: pd.DataFrame) -> dict:
    """Agrupa as 5 classes do ML em normal/anômalo e calcula taxa de falso alarme e de detecção,
    no mesmo formato usado para os algoritmos baseados em regra (para permitir comparação direta)."""
    tabela = matriz_confusao.copy()
    tabela["real_bin"] = tabela["classe_real"].apply(lambda classe: "normal" if classe == "normal" else "anomalo")
    tabela["previsto_bin"] = tabela["classe_prevista"].apply(lambda classe: "normal" if classe == "normal" else "anomalo")

    agregada = tabela.groupby(["real_bin", "previsto_bin"])["quantidade"].sum()
    verdadeiros_positivos = int(agregada.get(("anomalo", "anomalo"), 0))
    falsos_negativos = int(agregada.get(("anomalo", "normal"), 0))
    falsos_positivos = int(agregada.get(("normal", "anomalo"), 0))

    total_alertas = verdadeiros_positivos + falsos_positivos
    total_eventos_reais = verdadeiros_positivos + falsos_negativos

    return {
        "verdadeiros_positivos": verdadeiros_positivos,
        "falsos_positivos": falsos_positivos,
        "falsos_negativos": falsos_negativos,
        "taxa_falsos_positivos": round(falsos_positivos / total_alertas, 3) if total_alertas > 0 else None,
        "taxa_deteccao": round(verdadeiros_positivos / total_eventos_reais, 3) if total_eventos_reais > 0 else None,
    }


def montar_tabela_comparacao_geral(indicadores: dict[str, dict], comparacao_ml: dict | None) -> pd.DataFrame:
    """Monta a tabela final comparando taxa de falso alarme e taxa de detecção entre todas as abordagens."""
    nomes_em_portugues = {"limiar_simples": "Limiar Simples", "persistencia": "Persistência"}
    linhas = []
    for algoritmo, valores in indicadores.items():
        linhas.append({"Abordagem": nomes_em_portugues.get(algoritmo, algoritmo.title()), "Taxa de falso alarme": valores["taxa_falsos_positivos"], "Taxa de detecção": valores["taxa_deteccao"]})
    if comparacao_ml is not None:
        linhas.append({"Abordagem": "Machine Learning (binarizado)", "Taxa de falso alarme": comparacao_ml["taxa_falsos_positivos"], "Taxa de detecção": comparacao_ml["taxa_deteccao"]})
    return pd.DataFrame(linhas)


def montar_resumo_comparativo(metricas: list[Metrica]) -> pd.DataFrame:
    """Monta uma tabela lado a lado comparando os dois algoritmos por tipo de evento."""
    tipos_de_evento = sorted({metrica.tipo_evento for metrica in metricas})
    linhas = []

    for tipo_evento in tipos_de_evento:
        metrica_limiar_simples = next((metrica for metrica in metricas if metrica.algoritmo == NOME_LIMIAR_SIMPLES and metrica.tipo_evento == tipo_evento), None)
        metrica_persistencia = next((metrica for metrica in metricas if metrica.algoritmo == NOME_PERSISTENCIA and metrica.tipo_evento == tipo_evento), None)

        falsos_positivos_limiar_simples = metrica_limiar_simples.falsos_positivos if metrica_limiar_simples else 0
        falsos_positivos_persistencia = metrica_persistencia.falsos_positivos if metrica_persistencia else 0
        reducao_falsos_positivos = round((1 - falsos_positivos_persistencia / falsos_positivos_limiar_simples) * 100, 1) if falsos_positivos_limiar_simples > 0 else None

        linhas.append({
            "Tipo de evento": tipo_evento.replace("_", " ").title(),
            "FP limiar simples": falsos_positivos_limiar_simples,
            "FP persistência": falsos_positivos_persistencia,
            "Redução de FP (%)": reducao_falsos_positivos,
            "FN limiar simples": metrica_limiar_simples.falsos_negativos if metrica_limiar_simples else None,
            "FN persistência": metrica_persistencia.falsos_negativos if metrica_persistencia else None,
            "Tempo médio limiar simples (s)": metrica_limiar_simples.tempo_medio_deteccao if metrica_limiar_simples else None,
            "Tempo médio persistência (s)": metrica_persistencia.tempo_medio_deteccao if metrica_persistencia else None,
        })

    return pd.DataFrame(linhas)
