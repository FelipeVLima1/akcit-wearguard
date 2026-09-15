import numpy as np
from src.config import FaixaClinica, ParametrosSimulacao
from src.modelos import EventoGabarito


def gerar_instantes_evento(numero_leituras: int, duracao_evento: int, numero_eventos: int, gerador: np.random.Generator) -> list[int]:
    """Sorteia instantes de início não sobrepostos para inserir eventos anômalos."""
    instantes: list[int] = []
    tentativas_maximas = numero_eventos * 50
    tentativa = 0
    while len(instantes) < numero_eventos and tentativa < tentativas_maximas:
        candidato = int(gerador.integers(low = 0, high = numero_leituras - duracao_evento))
        sobrepoe = any(abs(candidato - instante) < duracao_evento for instante in instantes)
        if not sobrepoe:
            instantes.append(candidato)
        tentativa += 1
    return sorted(instantes)


def inserir_evento_alto(sinal: np.ndarray, faixa: FaixaClinica, inicio: int, fim: int) -> None:
    """Eleva os valores do sinal no intervalo informado acima do limite de alerta alto."""
    sinal[inicio:fim] = faixa.limite_alerta_alto + np.abs(sinal[inicio:fim] - faixa.maximo_normal)


def inserir_evento_baixo(sinal: np.ndarray, faixa: FaixaClinica, inicio: int, fim: int) -> None:
    """Reduz os valores do sinal no intervalo informado abaixo do limite de alerta baixo."""
    sinal[inicio:fim] = faixa.limite_alerta_baixo - np.abs(sinal[inicio:fim] - faixa.minimo_normal)


def inserir_eventos(sinal: np.ndarray, faixa: FaixaClinica, parametros: ParametrosSimulacao, semente: int) -> tuple[np.ndarray, list[EventoGabarito]]:
    """Insere eventos anômalos rotulados no sinal e retorna o sinal modificado com o gabarito."""
    sinal_modificado = sinal.copy()
    gerador = np.random.default_rng(seed = semente)
    eventos: list[EventoGabarito] = []

    tipos_evento = []
    if faixa.evento_alto is not None:
        tipos_evento.append((faixa.evento_alto, inserir_evento_alto))
    if faixa.evento_baixo is not None:
        tipos_evento.append((faixa.evento_baixo, inserir_evento_baixo))

    for tipo_evento, funcao_insercao in tipos_evento:
        instantes = gerar_instantes_evento(numero_leituras = len(sinal), duracao_evento = parametros.duracao_evento_leituras, numero_eventos = parametros.numero_eventos_por_tipo, gerador = gerador)
        for inicio in instantes:
            fim = inicio + parametros.duracao_evento_leituras
            funcao_insercao(sinal_modificado, faixa, inicio, fim)
            eventos.append(EventoGabarito(sinal = faixa.nome, tipo_evento = tipo_evento, leitura_inicio = inicio, leitura_fim = fim))

    return sinal_modificado, sorted(eventos, key = lambda evento: evento.leitura_inicio)
