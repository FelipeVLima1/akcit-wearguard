from pathlib import Path
from pydantic import BaseModel

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = RAIZ_PROJETO / "data" / "wearguard.db"
CAMINHO_LOG = RAIZ_PROJETO / "logs" / "wearguard.log"


class FaixaClinica(BaseModel):
    """Representa a faixa de normalidade e o limite de alerta de um sinal vital."""
    nome: str
    unidade: str
    minimo_normal: float
    maximo_normal: float
    limite_alerta_baixo: float | None = None
    limite_alerta_alto: float | None = None
    evento_baixo: str | None = None
    evento_alto: str | None = None


FREQUENCIA_CARDIACA = FaixaClinica(nome = "frequencia_cardiaca", unidade = "bpm", minimo_normal = 60, maximo_normal = 100, limite_alerta_baixo = 60, limite_alerta_alto = 100, evento_baixo = "bradicardia", evento_alto = "taquicardia")
SPO2 = FaixaClinica(nome = "spo2", unidade = "%", minimo_normal = 95, maximo_normal = 100, limite_alerta_baixo = 90, limite_alerta_alto = None, evento_baixo = "hipoxia", evento_alto = None)
TEMPERATURA_CORPORAL = FaixaClinica(nome = "temperatura_corporal", unidade = "C", minimo_normal = 36.1, maximo_normal = 37.2, limite_alerta_baixo = None, limite_alerta_alto = 37.8, evento_baixo = None, evento_alto = "febre")

FAIXAS_CLINICAS = [FREQUENCIA_CARDIACA, SPO2, TEMPERATURA_CORPORAL]


class ParametrosSimulacao(BaseModel):
    """Parâmetros gerais usados pelo simulador de sinais vitais."""
    duracao_total_leituras: int = 600
    intervalo_leitura_segundos: int = 1
    desvio_padrao_ruido: float = 0.5
    duracao_evento_leituras: int = 30
    numero_eventos_por_tipo: int = 2
    semente_aleatoria: int = 42


class ParametrosDeteccao(BaseModel):
    """Parâmetros dos algoritmos de detecção de anomalias."""
    leituras_consecutivas_para_alerta: int = 5
