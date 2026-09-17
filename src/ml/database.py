import sqlite3
from datetime import datetime, timezone
from src.database import obter_conexao

ESQUEMA_SQL_ML = """
CREATE TABLE IF NOT EXISTS modelos_ml (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    criado_em TEXT NOT NULL,
    algoritmo TEXT NOT NULL,
    acuracia REAL NOT NULL,
    macro_f1 REAL NOT NULL,
    total_batimentos_treino INTEGER NOT NULL,
    total_batimentos_teste INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS metricas_ml (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modelo_id INTEGER NOT NULL,
    classe TEXT NOT NULL,
    precisao REAL NOT NULL,
    recall REAL NOT NULL,
    f1 REAL NOT NULL,
    suporte INTEGER NOT NULL,
    FOREIGN KEY (modelo_id) REFERENCES modelos_ml(id)
);

CREATE TABLE IF NOT EXISTS matriz_confusao_ml (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modelo_id INTEGER NOT NULL,
    classe_real TEXT NOT NULL,
    classe_prevista TEXT NOT NULL,
    quantidade INTEGER NOT NULL,
    FOREIGN KEY (modelo_id) REFERENCES modelos_ml(id)
);
"""


def criar_esquema_ml() -> None:
    """Cria as tabelas de resultados de machine learning caso ainda não existam."""
    conexao = obter_conexao()
    conexao.executescript(ESQUEMA_SQL_ML)
    conexao.commit()
    conexao.close()


def salvar_resultado_ml(algoritmo: str, resultado: dict, total_batimentos_treino: int, total_batimentos_teste: int) -> int:
    """Salva o resultado de um treinamento (métricas gerais, por classe e matriz de confusão) e retorna o id do modelo."""
    conexao = obter_conexao()

    cursor = conexao.execute("INSERT INTO modelos_ml (criado_em, algoritmo, acuracia, macro_f1, total_batimentos_treino, total_batimentos_teste) VALUES (?, ?, ?, ?, ?, ?)", (datetime.now(timezone.utc).isoformat(), algoritmo, resultado["acuracia"], resultado["macro_f1"], total_batimentos_treino, total_batimentos_teste))
    modelo_id = cursor.lastrowid

    linhas_metricas = [(modelo_id, metrica["classe"], metrica["precisao"], metrica["recall"], metrica["f1"], metrica["suporte"]) for metrica in resultado["metricas_por_classe"]]
    conexao.executemany("INSERT INTO metricas_ml (modelo_id, classe, precisao, recall, f1, suporte) VALUES (?, ?, ?, ?, ?, ?)", linhas_metricas)

    classes = resultado["classes"]
    matriz = resultado["matriz_confusao"]
    linhas_matriz = [(modelo_id, classes[indice_real], classes[indice_previsto], int(matriz[indice_real][indice_previsto])) for indice_real in range(len(classes)) for indice_previsto in range(len(classes))]
    conexao.executemany("INSERT INTO matriz_confusao_ml (modelo_id, classe_real, classe_prevista, quantidade) VALUES (?, ?, ?, ?)", linhas_matriz)

    conexao.commit()
    conexao.close()
    return modelo_id


def obter_ultimo_modelo_ml() -> sqlite3.Row | None:
    """Recupera o registro do treinamento de ML mais recente."""
    conexao = obter_conexao()
    conexao.row_factory = sqlite3.Row
    linha = conexao.execute("SELECT * FROM modelos_ml ORDER BY id DESC LIMIT 1").fetchone()
    conexao.close()
    return linha


def obter_metricas_ml(modelo_id: int) -> list[sqlite3.Row]:
    """Recupera as métricas por classe de um treinamento de ML."""
    conexao = obter_conexao()
    conexao.row_factory = sqlite3.Row
    linhas = conexao.execute("SELECT * FROM metricas_ml WHERE modelo_id = ?", (modelo_id,)).fetchall()
    conexao.close()
    return linhas


def obter_matriz_confusao_ml(modelo_id: int) -> list[sqlite3.Row]:
    """Recupera a matriz de confusão de um treinamento de ML."""
    conexao = obter_conexao()
    conexao.row_factory = sqlite3.Row
    linhas = conexao.execute("SELECT * FROM matriz_confusao_ml WHERE modelo_id = ?", (modelo_id,)).fetchall()
    conexao.close()
    return linhas
