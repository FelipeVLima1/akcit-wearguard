import numpy as np
from src.database import obter_conexao
from src.modelos import AlertaClassificado, EventoGabarito, Metrica


def listar_execucoes() -> list[tuple[int, str]]:
    """Lista todas as execuções salvas no banco, da mais recente para a mais antiga."""
    conexao = obter_conexao()
    linhas = conexao.execute("SELECT id, criado_em FROM execucoes ORDER BY id DESC").fetchall()
    conexao.close()
    return linhas


def obter_leituras(execucao_id: int) -> dict[str, np.ndarray]:
    """Recupera as leituras finais de cada sinal vital de uma execução, em ordem de leitura."""
    conexao = obter_conexao()
    linhas = conexao.execute("SELECT sinal, indice_leitura, valor FROM leituras WHERE execucao_id = ? ORDER BY sinal, indice_leitura", (execucao_id,)).fetchall()
    conexao.close()

    valores_por_sinal: dict[str, list[float]] = {}
    for sinal, _, valor in linhas:
        valores_por_sinal.setdefault(sinal, []).append(valor)
    return {sinal: np.array(valores) for sinal, valores in valores_por_sinal.items()}


def obter_gabarito(execucao_id: int) -> list[EventoGabarito]:
    """Recupera os eventos anômalos rotulados (gabarito) de uma execução."""
    conexao = obter_conexao()
    linhas = conexao.execute("SELECT sinal, tipo_evento, leitura_inicio, leitura_fim FROM eventos_gabarito WHERE execucao_id = ?", (execucao_id,)).fetchall()
    conexao.close()
    return [EventoGabarito(sinal = sinal, tipo_evento = tipo_evento, leitura_inicio = leitura_inicio, leitura_fim = leitura_fim) for sinal, tipo_evento, leitura_inicio, leitura_fim in linhas]


def obter_alertas(execucao_id: int) -> list[AlertaClassificado]:
    """Recupera todos os alertas já classificados emitidos numa execução."""
    conexao = obter_conexao()
    linhas = conexao.execute("SELECT algoritmo, sinal, tipo_evento, leitura_indice, classificacao FROM alertas WHERE execucao_id = ?", (execucao_id,)).fetchall()
    conexao.close()
    return [AlertaClassificado(algoritmo = algoritmo, sinal = sinal, tipo_evento = tipo_evento, leitura_indice = leitura_indice, classificacao = classificacao) for algoritmo, sinal, tipo_evento, leitura_indice, classificacao in linhas]


def obter_execucao(execucao_id: int) -> tuple[int, str] | None:
    """Recupera o id e a data de criação de uma execução específica."""
    conexao = obter_conexao()
    linha = conexao.execute("SELECT id, criado_em FROM execucoes WHERE id = ?", (execucao_id,)).fetchone()
    conexao.close()
    return linha


def obter_parametros(execucao_id: int) -> dict:
    """Recupera os parâmetros de simulação e detecção usados numa execução."""
    conexao = obter_conexao()
    linha = conexao.execute("SELECT duracao_total_leituras, intervalo_leitura_segundos, desvio_padrao_ruido, duracao_evento_leituras, numero_eventos_por_tipo, semente_aleatoria, leituras_consecutivas_para_alerta FROM parametros_execucao WHERE execucao_id = ?", (execucao_id,)).fetchone()
    conexao.close()
    if linha is None:
        return {}
    campos = ["duracao_total_leituras", "intervalo_leitura_segundos", "desvio_padrao_ruido", "duracao_evento_leituras", "numero_eventos_por_tipo", "semente_aleatoria", "leituras_consecutivas_para_alerta"]
    return dict(zip(campos, linha))


def obter_metricas(execucao_id: int) -> list[Metrica]:
    """Recupera as métricas finais de desempenho de cada algoritmo numa execução."""
    conexao = obter_conexao()
    linhas = conexao.execute("SELECT algoritmo, tipo_evento, verdadeiros_positivos, falsos_positivos, falsos_negativos, tempo_medio_deteccao FROM metricas WHERE execucao_id = ?", (execucao_id,)).fetchall()
    conexao.close()
    return [Metrica(algoritmo = algoritmo, tipo_evento = tipo_evento, verdadeiros_positivos = verdadeiros_positivos, falsos_positivos = falsos_positivos, falsos_negativos = falsos_negativos, tempo_medio_deteccao = tempo_medio_deteccao) for algoritmo, tipo_evento, verdadeiros_positivos, falsos_positivos, falsos_negativos, tempo_medio_deteccao in linhas]
