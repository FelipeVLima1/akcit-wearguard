from src.config import FAIXAS_CLINICAS
from src.database import criar_esquema, criar_execucao, obter_conexao, salvar_alertas_classificados, salvar_gabarito, salvar_leituras, salvar_metricas
from src.deteccao.limiar_simples import NOME_ALGORITMO as NOME_LIMIAR_SIMPLES, detectar_limiar_simples
from src.deteccao.persistencia import NOME_ALGORITMO as NOME_PERSISTENCIA, detectar_persistencia
from src.avaliacao.comparador import classificar_alertas, listar_eventos_nao_detectados
from src.avaliacao.metricas import calcular_metricas
from src.grafo.estado import EstadoWearGuard
from src.logger import criar_logger
from src.simulador.eventos import inserir_eventos
from src.simulador.gerador_sinais import gerar_sinal_base
from src.simulador.injetor_ruido import injetar_ruido

logger = criar_logger(nome = "wearguard.grafo")


def no_gerar_sinais_base(estado: EstadoWearGuard) -> dict:
    """Gera o sinal-base estável para cada sinal vital monitorado."""
    parametros = estado["parametros_simulacao"]
    sinais_base = {faixa.nome: gerar_sinal_base(faixa = faixa, numero_leituras = parametros.duracao_total_leituras, semente = parametros.semente_aleatoria + indice) for indice, faixa in enumerate(FAIXAS_CLINICAS)}
    logger.info("sinais-base gerados para %s sinais vitais", len(sinais_base))
    return {"sinais_base": sinais_base}


def no_injetar_ruido(estado: EstadoWearGuard) -> dict:
    """Aplica ruído gaussiano a cada sinal-base gerado."""
    parametros = estado["parametros_simulacao"]
    sinais_com_ruido = {nome_sinal: injetar_ruido(sinal = sinal, desvio_padrao = parametros.desvio_padrao_ruido, semente = parametros.semente_aleatoria + 100 + indice) for indice, (nome_sinal, sinal) in enumerate(estado["sinais_base"].items())}
    logger.info("ruido gaussiano aplicado com desvio padrao %s", parametros.desvio_padrao_ruido)
    return {"sinais_com_ruido": sinais_com_ruido}


def no_inserir_eventos(estado: EstadoWearGuard) -> dict:
    """Insere os eventos anômalos rotulados em cada sinal e monta o gabarito completo."""
    parametros = estado["parametros_simulacao"]
    sinais_finais = {}
    gabarito = []
    for indice, faixa in enumerate(FAIXAS_CLINICAS):
        sinal_final, eventos = inserir_eventos(sinal = estado["sinais_com_ruido"][faixa.nome], faixa = faixa, parametros = parametros, semente = parametros.semente_aleatoria + 200 + indice)
        sinais_finais[faixa.nome] = sinal_final
        gabarito.extend(eventos)
    logger.info("gabarito montado com %s eventos anomalos", len(gabarito))
    return {"sinais_finais": sinais_finais, "gabarito": gabarito}


def no_rodar_algoritmos(estado: EstadoWearGuard) -> dict:
    """Executa o algoritmo de limiar simples e o de persistência sobre o mesmo conjunto de dados."""
    alertas_limiar_simples = []
    alertas_persistencia = []
    for faixa in FAIXAS_CLINICAS:
        sinal = estado["sinais_finais"][faixa.nome]
        alertas_limiar_simples.extend(detectar_limiar_simples(sinal = sinal, faixa = faixa))
        alertas_persistencia.extend(detectar_persistencia(sinal = sinal, faixa = faixa, parametros = estado["parametros_deteccao"]))
    logger.info("limiar simples emitiu %s alertas, persistencia emitiu %s alertas", len(alertas_limiar_simples), len(alertas_persistencia))
    return {"alertas_limiar_simples": alertas_limiar_simples, "alertas_persistencia": alertas_persistencia}


def no_comparar_com_gabarito(estado: EstadoWearGuard) -> dict:
    """Classifica os alertas de cada algoritmo contra o gabarito e lista os eventos não detectados."""
    todos_alertas = estado["alertas_limiar_simples"] + estado["alertas_persistencia"]
    alertas_classificados = classificar_alertas(alertas = todos_alertas, eventos = estado["gabarito"])
    eventos_nao_detectados_limiar_simples = listar_eventos_nao_detectados(alertas = estado["alertas_limiar_simples"], eventos = estado["gabarito"])
    eventos_nao_detectados_persistencia = listar_eventos_nao_detectados(alertas = estado["alertas_persistencia"], eventos = estado["gabarito"])
    return {"alertas_classificados": alertas_classificados, "eventos_nao_detectados_limiar_simples": eventos_nao_detectados_limiar_simples, "eventos_nao_detectados_persistencia": eventos_nao_detectados_persistencia}


def no_calcular_metricas(estado: EstadoWearGuard) -> dict:
    """Calcula as métricas de desempenho de cada algoritmo por tipo de evento."""
    alertas_limiar_simples = [alerta for alerta in estado["alertas_classificados"] if alerta.algoritmo == NOME_LIMIAR_SIMPLES]
    alertas_persistencia = [alerta for alerta in estado["alertas_classificados"] if alerta.algoritmo == NOME_PERSISTENCIA]
    intervalo = estado["parametros_simulacao"].intervalo_leitura_segundos

    metricas_limiar_simples = calcular_metricas(algoritmo = NOME_LIMIAR_SIMPLES, alertas_classificados = alertas_limiar_simples, eventos = estado["gabarito"], eventos_nao_detectados = estado["eventos_nao_detectados_limiar_simples"], intervalo_leitura_segundos = intervalo)
    metricas_persistencia = calcular_metricas(algoritmo = NOME_PERSISTENCIA, alertas_classificados = alertas_persistencia, eventos = estado["gabarito"], eventos_nao_detectados = estado["eventos_nao_detectados_persistencia"], intervalo_leitura_segundos = intervalo)

    logger.info("metricas calculadas para os dois algoritmos")
    return {"metricas": metricas_limiar_simples + metricas_persistencia}


def no_persistir_resultados(estado: EstadoWearGuard) -> dict:
    """Salva sinais, gabarito, alertas classificados e métricas da execução no SQLite."""
    criar_esquema()
    conexao = obter_conexao()
    execucao_id = criar_execucao(conexao)
    salvar_leituras(conexao, execucao_id, estado["sinais_finais"])
    salvar_gabarito(conexao, execucao_id, estado["gabarito"])
    salvar_alertas_classificados(conexao, execucao_id, estado["alertas_classificados"])
    salvar_metricas(conexao, execucao_id, estado["metricas"])
    conexao.commit()
    conexao.close()
    logger.info("execucao %s persistida no banco", execucao_id)
    return {"execucao_id": execucao_id}
