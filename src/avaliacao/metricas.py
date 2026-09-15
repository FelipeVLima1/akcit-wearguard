from src.avaliacao.comparador import FALSO_POSITIVO, VERDADEIRO_POSITIVO, evento_correspondente
from src.modelos import AlertaClassificado, EventoGabarito, Metrica


def calcular_tempo_deteccao(alerta: AlertaClassificado, eventos: list[EventoGabarito], intervalo_leitura_segundos: float) -> float:
    """Calcula o tempo entre o início do evento real e a leitura em que o alerta foi emitido."""
    evento = evento_correspondente(alerta, eventos)
    return (alerta.leitura_indice - evento.leitura_inicio) * intervalo_leitura_segundos


def calcular_metricas(algoritmo: str, alertas_classificados: list[AlertaClassificado], eventos: list[EventoGabarito], eventos_nao_detectados: list[EventoGabarito], intervalo_leitura_segundos: float) -> list[Metrica]:
    """Agrupa alertas e eventos por tipo de evento e calcula as métricas de desempenho do algoritmo."""
    tipos_de_evento = sorted({evento.tipo_evento for evento in eventos})
    metricas: list[Metrica] = []

    for tipo_evento in tipos_de_evento:
        alertas_do_tipo = [alerta for alerta in alertas_classificados if alerta.tipo_evento == tipo_evento]
        verdadeiros_positivos = [alerta for alerta in alertas_do_tipo if alerta.classificacao == VERDADEIRO_POSITIVO]
        falsos_positivos = [alerta for alerta in alertas_do_tipo if alerta.classificacao == FALSO_POSITIVO]
        falsos_negativos = [evento for evento in eventos_nao_detectados if evento.tipo_evento == tipo_evento]

        tempos_deteccao = [calcular_tempo_deteccao(alerta, eventos, intervalo_leitura_segundos) for alerta in verdadeiros_positivos]
        tempo_medio = sum(tempos_deteccao) / len(tempos_deteccao) if tempos_deteccao else None

        metricas.append(Metrica(algoritmo = algoritmo, tipo_evento = tipo_evento, verdadeiros_positivos = len(verdadeiros_positivos), falsos_positivos = len(falsos_positivos), falsos_negativos = len(falsos_negativos), tempo_medio_deteccao = tempo_medio))

    return metricas
