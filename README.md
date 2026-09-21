# WearGuard

## Como rodar

```bash
cd akcit-wearguard
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run front/app.py
```

Se o `.venv` não existir ainda, crie primeiro com `python -m venv .venv` antes de ativar.

## Outros comandos úteis

```bash
python -m src.main          # roda o pipeline de simulação (limiar simples / persistência)
python -m src.ml.treinar    # baixa a base MIT-BIH na primeira vez e treina o classificador
python -m pytest tests/     # roda os testes
```

O treinamento baixa automaticamente os registros necessários do MIT-BIH quando eles ainda não
existem em `data/mitbih_raw/`. A primeira execução exige conexão com a internet; depois, os dados
extraídos são reutilizados pelo cache em `data/mitbih_batimentos.npz`.

Mais detalhes em `CHECKLIST.md`, `.init` e `docs/`.
