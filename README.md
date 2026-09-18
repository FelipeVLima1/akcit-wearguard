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
python -m src.ml.treinar    # treina o classificador de arritmias (ECG real)
python -m pytest tests/     # roda os testes
```

Mais detalhes em `CHECKLIST.md`, `.init` e `docs/`.
