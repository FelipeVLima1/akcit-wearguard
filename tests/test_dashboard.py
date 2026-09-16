from streamlit.testing.v1 import AppTest
from src.config import ParametrosDeteccao, ParametrosSimulacao
from src.grafo.pipeline import montar_grafo


def garantir_execucao_no_banco() -> None:
    grafo = montar_grafo()
    grafo.invoke({"parametros_simulacao": ParametrosSimulacao(), "parametros_deteccao": ParametrosDeteccao()})


def test_dashboard_carrega_sem_excecoes():
    garantir_execucao_no_banco()
    app = AppTest.from_file("front/app.py", default_timeout = 30)
    app.run()
    assert not app.exception
