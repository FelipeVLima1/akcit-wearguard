import numpy as np
import wfdb
from src.logger import criar_logger
from src.ml.config import AMOSTRAS_ANTES_PICO, AMOSTRAS_DEPOIS_PICO, CAMINHO_CACHE_BATIMENTOS, CAMINHO_DADOS_BRUTOS, FREQUENCIA_AMOSTRAGEM, MAPEAMENTO_AAMI, REGISTROS_TESTE, REGISTROS_TREINO

logger = criar_logger(nome = "wearguard.ml")

INTERVALO_RR_PADRAO_EM_AMOSTRAS = AMOSTRAS_ANTES_PICO + AMOSTRAS_DEPOIS_PICO
REGISTROS_MITBIH = REGISTROS_TREINO + REGISTROS_TESTE


def garantir_dados_mitbih() -> None:
    """Baixa os registros MIT-BIH usados pelo treinamento quando necessário."""
    arquivos_ausentes = [
        registro
        for registro in REGISTROS_MITBIH
        if not all((CAMINHO_DADOS_BRUTOS / f"{registro}{extensao}").exists() for extensao in (".hea", ".dat", ".atr"))
    ]
    if not arquivos_ausentes:
        return

    CAMINHO_DADOS_BRUTOS.mkdir(parents = True, exist_ok = True)
    logger.info("baixando registros MIT-BIH ausentes: %s", ", ".join(arquivos_ausentes))
    try:
        wfdb.dl_database(
            "mitdb",
            dl_dir = str(CAMINHO_DADOS_BRUTOS),
            records = arquivos_ausentes,
            annotators = ["atr"],
            keep_subdirs = False,
        )
    except Exception as erro:
        raise RuntimeError(
            "Nao foi possivel obter os dados MIT-BIH automaticamente. "
            "Verifique sua conexao com a internet e tente novamente."
        ) from erro

    arquivos_ainda_ausentes = [
        registro
        for registro in arquivos_ausentes
        if not all((CAMINHO_DADOS_BRUTOS / f"{registro}{extensao}").exists() for extensao in (".hea", ".dat", ".atr"))
    ]
    if arquivos_ainda_ausentes:
        raise RuntimeError(f"Download MIT-BIH incompleto; faltam os registros: {', '.join(arquivos_ainda_ausentes)}")


def normalizar_segmento(segmento: np.ndarray) -> np.ndarray:
    """Normaliza a amplitude de um segmento de ECG (média zero, desvio padrão um)."""
    desvio_padrao = segmento.std()
    return (segmento - segmento.mean()) / desvio_padrao if desvio_padrao > 0 else segmento - segmento.mean()


def extrair_batimentos_do_registro(registro: str) -> tuple[np.ndarray, np.ndarray]:
    """Lê um registro do MIT-BIH e extrai, para cada batimento anotado, a forma do ECG ao redor do pico R
    somada aos intervalos RR (anterior e seguinte), seguindo de Chazal et al. (2004)."""
    caminho = str(CAMINHO_DADOS_BRUTOS / registro)
    sinal, _ = wfdb.rdsamp(caminho, channels = [0])
    anotacao = wfdb.rdann(caminho, extension = "atr")
    onda = sinal[:, 0]

    indices_de_batimentos = [indice for indice, simbolo in enumerate(anotacao.symbol) if simbolo in MAPEAMENTO_AAMI]
    amostras_dos_picos = anotacao.sample[indices_de_batimentos]
    simbolos_dos_picos = [anotacao.symbol[indice] for indice in indices_de_batimentos]

    segmentos = []
    classes = []
    for posicao, (amostra_pico, simbolo) in enumerate(zip(amostras_dos_picos, simbolos_dos_picos)):
        inicio = amostra_pico - AMOSTRAS_ANTES_PICO
        fim = amostra_pico + AMOSTRAS_DEPOIS_PICO
        if inicio < 0 or fim > len(onda):
            continue

        segmento_normalizado = normalizar_segmento(onda[inicio:fim])

        intervalo_rr_anterior = amostra_pico - amostras_dos_picos[posicao - 1] if posicao > 0 else INTERVALO_RR_PADRAO_EM_AMOSTRAS
        intervalo_rr_seguinte = amostras_dos_picos[posicao + 1] - amostra_pico if posicao < len(amostras_dos_picos) - 1 else INTERVALO_RR_PADRAO_EM_AMOSTRAS
        intervalos_rr_em_segundos = np.array([intervalo_rr_anterior, intervalo_rr_seguinte]) / FREQUENCIA_AMOSTRAGEM

        segmentos.append(np.concatenate([segmento_normalizado, intervalos_rr_em_segundos]))
        classes.append(MAPEAMENTO_AAMI[simbolo])

    return np.array(segmentos), np.array(classes)


def extrair_batimentos_de_varios_registros(registros: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Extrai e empilha os batimentos de uma lista de registros do MIT-BIH."""
    todos_segmentos = []
    todas_classes = []
    for registro in registros:
        segmentos, classes = extrair_batimentos_do_registro(registro)
        todos_segmentos.append(segmentos)
        todas_classes.append(classes)
        logger.info("registro %s: %s batimentos extraidos", registro, len(classes))
    return np.concatenate(todos_segmentos), np.concatenate(todas_classes)


def preparar_conjuntos_treino_teste(usar_cache: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Monta os conjuntos de treino e teste (split por paciente) a partir do MIT-BIH, com cache em disco."""
    if usar_cache and CAMINHO_CACHE_BATIMENTOS.exists():
        cache = np.load(CAMINHO_CACHE_BATIMENTOS)
        logger.info("conjuntos de treino/teste carregados do cache")
        return cache["x_treino"], cache["y_treino"], cache["x_teste"], cache["y_teste"]

    garantir_dados_mitbih()
    x_treino, y_treino = extrair_batimentos_de_varios_registros(REGISTROS_TREINO)
    x_teste, y_teste = extrair_batimentos_de_varios_registros(REGISTROS_TESTE)

    CAMINHO_CACHE_BATIMENTOS.parent.mkdir(parents = True, exist_ok = True)
    np.savez_compressed(CAMINHO_CACHE_BATIMENTOS, x_treino = x_treino, y_treino = y_treino, x_teste = x_teste, y_teste = y_teste)
    logger.info("conjuntos de treino/teste extraidos e salvos em cache")

    return x_treino, y_treino, x_teste, y_teste
