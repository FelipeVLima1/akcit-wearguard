import sqlite3
from datetime import datetime, timezone
import numpy as np
from src.config import CAMINHO_BANCO, ParametrosDeteccao, ParametrosSimulacao
from src.modelos import AlertaClassificado, EventoGabarito, Metrica

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

CREATE TABLE IF NOT EXISTS parametros_execucao (
    execucao_id INTEGER PRIMARY KEY,
    duracao_total_leituras INTEGER NOT NULL,
    intervalo_leitura_segundos INTEGER NOT NULL,
    desvio_padrao_ruido REAL NOT NULL,
    duracao_evento_leituras INTEGER NOT NULL,
    numero_eventos_por_tipo INTEGER NOT NULL,
    semente_aleatoria INTEGER NOT NULL,
    leituras_consecutivas_para_alerta INTEGER NOT NULL,
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


def criar_execucao(conexao: sqlite3.Connection) -> int:
    """Registra uma nova execução do pipeline e retorna o seu id."""
    cursor = conexao.execute("INSERT INTO execucoes (criado_em) VALUES (?)", (datetime.now(timezone.utc).isoformat(),))
    return cursor.lastrowid


def salvar_leituras(conexao: sqlite3.Connection, execucao_id: int, sinais: dict[str, np.ndarray]) -> None:
    """Salva todas as leituras finais de cada sinal vital simulado."""
    linhas = [(execucao_id, sinal, indice, float(valor)) for sinal, serie in sinais.items() for indice, valor in enumerate(serie)]
    conexao.executemany("INSERT INTO leituras (execucao_id, sinal, indice_leitura, valor) VALUES (?, ?, ?, ?)", linhas)


def salvar_gabarito(conexao: sqlite3.Connection, execucao_id: int, eventos: list[EventoGabarito]) -> None:
    """Salva os eventos anômalos rotulados que formam o gabarito da execução."""
    linhas = [(execucao_id, evento.sinal, evento.tipo_evento, evento.leitura_inicio, evento.leitura_fim) for evento in eventos]
    conexao.executemany("INSERT INTO eventos_gabarito (execucao_id, sinal, tipo_evento, leitura_inicio, leitura_fim) VALUES (?, ?, ?, ?, ?)", linhas)


def salvar_alertas_classificados(conexao: sqlite3.Connection, execucao_id: int, alertas: list[AlertaClassificado]) -> None:
    """Salva os alertas emitidos pelos algoritmos já classificados contra o gabarito."""
    linhas = [(execucao_id, alerta.algoritmo, alerta.sinal, alerta.tipo_evento, alerta.leitura_indice, alerta.classificacao) for alerta in alertas]
    conexao.executemany("INSERT INTO alertas (execucao_id, algoritmo, sinal, tipo_evento, leitura_indice, classificacao) VALUES (?, ?, ?, ?, ?, ?)", linhas)


def salvar_parametros(conexao: sqlite3.Connection, execucao_id: int, parametros_simulacao: ParametrosSimulacao, parametros_deteccao: ParametrosDeteccao) -> None:
    """Salva os parâmetros de simulação e detecção usados numa execução."""
    conexao.execute("INSERT INTO parametros_execucao (execucao_id, duracao_total_leituras, intervalo_leitura_segundos, desvio_padrao_ruido, duracao_evento_leituras, numero_eventos_por_tipo, semente_aleatoria, leituras_consecutivas_para_alerta) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (execucao_id, parametros_simulacao.duracao_total_leituras, parametros_simulacao.intervalo_leitura_segundos, parametros_simulacao.desvio_padrao_ruido, parametros_simulacao.duracao_evento_leituras, parametros_simulacao.numero_eventos_por_tipo, parametros_simulacao.semente_aleatoria, parametros_deteccao.leituras_consecutivas_para_alerta))


def salvar_metricas(conexao: sqlite3.Connection, execucao_id: int, metricas: list[Metrica]) -> None:
    """Salva as métricas finais de desempenho de cada algoritmo por tipo de evento."""
    linhas = [(execucao_id, metrica.algoritmo, metrica.tipo_evento, metrica.verdadeiros_positivos, metrica.falsos_positivos, metrica.falsos_negativos, metrica.tempo_medio_deteccao) for metrica in metricas]
    conexao.executemany("INSERT INTO metricas (execucao_id, algoritmo, tipo_evento, verdadeiros_positivos, falsos_positivos, falsos_negativos, tempo_medio_deteccao) VALUES (?, ?, ?, ?, ?, ?, ?)", linhas)


if __name__ == "__main__":
    criar_esquema()
