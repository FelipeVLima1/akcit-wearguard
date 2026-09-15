from src.modelos import Alerta, AlertaClassificado, EventoGabarito

VERDADEIRO_POSITIVO = "verdadeiro_positivo"
FALSO_POSITIVO = "falso_positivo"


def evento_correspondente(alerta: Alerta, eventos: list[EventoGabarito]) -> EventoGabarito | None:
    """Procura no gabarito um evento do mesmo sinal e tipo que contenha a leitura do alerta."""
    for evento in eventos:
        mesmo_sinal_e_tipo = evento.sinal == alerta.sinal and evento.tipo_evento == alerta.tipo_evento
        dentro_do_intervalo = evento.leitura_inicio <= alerta.leitura_indice < evento.leitura_fim
        if mesmo_sinal_e_tipo and dentro_do_intervalo:
            return evento
    return None


def classificar_alertas(alertas: list[Alerta], eventos: list[EventoGabarito]) -> list[AlertaClassificado]:
    """Classifica cada alerta como verdadeiro positivo (dentro de um evento real) ou falso positivo."""
    alertas_classificados: list[AlertaClassificado] = []
    for alerta in alertas:
        classificacao = VERDADEIRO_POSITIVO if evento_correspondente(alerta, eventos) is not None else FALSO_POSITIVO
        alertas_classificados.append(AlertaClassificado(**alerta.model_dump(), classificacao = classificacao))
    return alertas_classificados


def listar_eventos_nao_detectados(alertas: list[Alerta], eventos: list[EventoGabarito]) -> list[EventoGabarito]:
    """Retorna os eventos do gabarito para os quais nenhum alerta caiu dentro do intervalo (falsos negativos)."""
    eventos_nao_detectados: list[EventoGabarito] = []
    for evento in eventos:
        detectado = any(
            alerta.sinal == evento.sinal and alerta.tipo_evento == evento.tipo_evento and evento.leitura_inicio <= alerta.leitura_indice < evento.leitura_fim
            for alerta in alertas
        )
        if not detectado:
            eventos_nao_detectados.append(evento)
    return eventos_nao_detectados
