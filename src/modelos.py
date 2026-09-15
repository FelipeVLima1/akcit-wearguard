from pydantic import BaseModel


class EventoGabarito(BaseModel):
    """Representa um evento anômalo inserido no sinal, com início e fim conhecidos."""
    sinal: str
    tipo_evento: str
    leitura_inicio: int
    leitura_fim: int


class Alerta(BaseModel):
    """Representa um alerta emitido por um algoritmo de detecção em uma leitura."""
    algoritmo: str
    sinal: str
    tipo_evento: str
    leitura_indice: int


class Metrica(BaseModel):
    """Resume o desempenho de um algoritmo para um tipo de evento em uma execução."""
    algoritmo: str
    tipo_evento: str
    verdadeiros_positivos: int
    falsos_positivos: int
    falsos_negativos: int
    tempo_medio_deteccao: float | None
