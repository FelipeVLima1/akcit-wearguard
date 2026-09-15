# Checklist de Desenvolvimento — AKCIT WearGuard

Plano passo a passo. Cada item marcado é testado antes de seguir para o próximo.
Frontend fica propositalmente por último.

## Fase 0 — Setup do projeto

- [x] Criar estrutura de pastas (src, tests, data, logs)
- [x] Criar .init explicando o projeto
- [x] Criar este checklist
- [x] Criar requirements.txt
- [x] Criar .gitignore
- [x] Inicializar git local (sem remoto ainda)
- [x] Criar config.py (limites clínicos, caminhos, parâmetros do simulador)
- [x] Criar logger.py (logging em arquivo e console)
- [x] Criar database.py (schema SQLite: sinais, eventos, alertas, métricas)
- [x] Criar ambiente virtual (.venv) isolado e instalar requirements.txt

## Fase 1 — Simulador de sinais vitais

- [x] gerador_sinais.py — gera série temporal-base dentro da faixa de normalidade
      para frequência cardíaca, SpO2 e temperatura corporal
- [x] injetor_ruido.py — aplica ruído gaussiano controlado sobre os períodos normais
- [x] eventos.py — insere os quatro eventos anômalos rotulados (taquicardia,
      bradicardia, hipóxia, febre) em instantes controlados e registra o gabarito
- [x] Testes unitários do simulador

## Fase 2 — Algoritmos de detecção

- [x] limiar_simples.py — baseline: alerta imediato ao ultrapassar o limite clínico
- [x] persistencia.py — alerta somente após N leituras consecutivas fora da faixa
- [x] Testes unitários dos dois algoritmos com casos de borda

## Fase 3 — Orquestração com LangGraph

- [x] estado.py — schema do estado do grafo (TypedDict)
- [x] nos.py — funções de cada nó (simular, ruído, eventos, limiar simples,
      persistência, comparar, métricas, persistir)
- [x] pipeline.py — monta o StateGraph e as arestas entre os nós
- [x] Teste de execução ponta a ponta do grafo

## Fase 4 — Avaliação e métricas

- [x] comparador.py — classifica cada alerta contra o gabarito (verdadeiro
      positivo, falso positivo, falso negativo)
- [x] metricas.py — calcula tempo médio de detecção e taxa de falsos
      positivos/negativos por algoritmo e por tipo de evento
- [x] Testes unitários com conjunto de dados conhecido

## Fase 5 — Persistência dos resultados

- [x] Salvar sinais simulados, gabarito, alertas e métricas no SQLite
- [ ] Função de consulta para recuperar uma execução completa por id (adiado até
      ser necessário para o dashboard, na Fase 7)

## Fase 6 — Execução ponta a ponta

- [x] main.py — roda o pipeline completo via LangGraph e imprime/loga o resumo
- [x] Rodar pipeline completo pelo menos uma vez e validar resultados manualmente
- [ ] Ajustar parâmetros do simulador/algoritmos (ex: desvio padrão do ruído) para
      gerar mais falsos positivos no limiar simples e evidenciar melhor o ganho do
      critério de persistência — discutir com o usuário antes de mudar o padrão

## Fase 7 — Frontend (dashboard) — por último

- [ ] Definir estrutura da pasta front/ (componentes separados, não um único
      arquivo streamlit gigante)
- [ ] Tela de visão geral: sinais vitais simulados ao longo do tempo
- [ ] Tela de alertas: comparação limiar simples vs persistência
- [ ] Tela de métricas: tempo médio de detecção e taxa de falsos positivos/negativos
- [ ] Revisão visual (não usar tema padrão "cru" do Streamlit)

## Observações

- Cada fase concluída gera commit(s) próprio(s) em português, formato
  `tipo: descrição` (feat, fix, refactor, chore, delete).
- Dúvidas de escopo, parâmetros ou prioridade voltam para o autor antes de assumir.
