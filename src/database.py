import sqlite3
from src.config import CAMINHO_BANCO

ESQUEMA_SQL = """
CREATE TABLE IF NOT EXISTS execucoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    criado_em TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leituras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execucao_id INTEGER NOT NULL,
    sinal TEXT NOT NULL,
    indice_leitura INTEGER NOT NULL,
    valor REAL NOT NULL,
    FOREIGN KEY (execucao_id) REFERENCES execucoes(id)
);

CREATE TABLE IF NOT EXISTS eventos_gabarito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execucao_id INTEGER NOT NULL,
    sinal TEXT NOT NULL,
    tipo_evento TEXT NOT NULL,
    leitura_inicio INTEGER NOT NULL,
    leitura_fim INTEGER NOT NULL,
    FOREIGN KEY (execucao_id) REFERENCES execucoes(id)
);

CREATE TABLE IF NOT EXISTS alertas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execucao_id INTEGER NOT NULL,
    algoritmo TEXT NOT NULL,
    sinal TEXT NOT NULL,
    tipo_evento TEXT NOT NULL,
    leitura_indice INTEGER NOT NULL,
    classificacao TEXT NOT NULL,
    FOREIGN KEY (execucao_id) REFERENCES execucoes(id)
);

CREATE TABLE IF NOT EXISTS metricas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execucao_id INTEGER NOT NULL,
    algoritmo TEXT NOT NULL,
    tipo_evento TEXT NOT NULL,
    verdadeiros_positivos INTEGER NOT NULL,
    falsos_positivos INTEGER NOT NULL,
    falsos_negativos INTEGER NOT NULL,
    tempo_medio_deteccao REAL,
    FOREIGN KEY (execucao_id) REFERENCES execucoes(id)
);
"""


def obter_conexao() -> sqlite3.Connection:
    """Abre uma conexão SQLite com o banco do projeto, criando a pasta se necessário."""
    CAMINHO_BANCO.parent.mkdir(parents = True, exist_ok = True)
    return sqlite3.connect(CAMINHO_BANCO)


def criar_esquema() -> None:
    """Cria as tabelas do banco caso ainda não existam."""
    conexao = obter_conexao()
    conexao.executescript(ESQUEMA_SQL)
    conexao.commit()
    conexao.close()


if __name__ == "__main__":
    criar_esquema()
