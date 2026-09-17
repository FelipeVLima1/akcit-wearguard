from src.config import RAIZ_PROJETO

CAMINHO_DADOS_BRUTOS = RAIZ_PROJETO / "data" / "mitbih_raw"
CAMINHO_CACHE_BATIMENTOS = RAIZ_PROJETO / "data" / "mitbih_batimentos.npz"
CAMINHO_MODELO = RAIZ_PROJETO / "data" / "modelo_arritmia.joblib"

FREQUENCIA_AMOSTRAGEM = 360
AMOSTRAS_ANTES_PICO = 90
AMOSTRAS_DEPOIS_PICO = 110

CLASSES = ["normal", "supraventricular", "ventricular", "fusao", "desconhecido"]

MAPEAMENTO_AAMI = {
    "N": "normal", "L": "normal", "R": "normal", "e": "normal", "j": "normal",
    "A": "supraventricular", "a": "supraventricular", "J": "supraventricular", "S": "supraventricular",
    "V": "ventricular", "E": "ventricular",
    "F": "fusao",
    "/": "desconhecido", "f": "desconhecido", "Q": "desconhecido",
}

# Registros 102, 104, 107 e 217 sao excluidos por convencao da literatura (de Chazal et al., 2004)
# por conterem predominantemente batimentos de marca-passo, que distorcem a comparacao entre classes.
REGISTROS_TREINO = ["101", "106", "108", "109", "112", "114", "115", "116", "118", "119", "122", "124", "201", "203", "205", "207", "208", "209", "215", "220", "223", "230"]
REGISTROS_TESTE = ["100", "103", "105", "111", "113", "117", "121", "123", "200", "202", "210", "212", "213", "214", "219", "221", "222", "228", "231", "232", "233", "234"]
