import logging
from src.config import CAMINHO_LOG


def criar_logger(nome: str) -> logging.Logger:
    """Cria um logger configurado para gravar em arquivo e no console."""
    logger = logging.getLogger(nome)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formato = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    CAMINHO_LOG.parent.mkdir(parents = True, exist_ok = True)
    handler_arquivo = logging.FileHandler(CAMINHO_LOG, encoding = "utf-8")
    handler_arquivo.setFormatter(formato)

    handler_console = logging.StreamHandler()
    handler_console.setFormatter(formato)

    logger.addHandler(handler_arquivo)
    logger.addHandler(handler_console)
    return logger
