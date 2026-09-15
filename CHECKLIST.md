# Checklist de Desenvolvimento — AKCIT WearGuard

Plano passo a passo. Cada item marcado é testado antes de seguir para o próximo.
Frontend fica propositalmente por último.

## Fase 0 — Setup do projeto

- [x] Criar estrutura de pastas (src, tests, data, logs)
- [x] Criar .init explicando o projeto
- [x] Criar este checklist
- [ ] Criar requirements.txt
- [ ] Criar .gitignore
- [ ] Inicializar git local (sem remoto ainda)
- [ ] Criar config.py (limites clínicos, caminhos, parâmetros do simulador)
- [ ] Criar logger.py (logging em arquivo e console)
- [ ] Criar database.py (schema SQLite: sinais, eventos, alertas, métricas)

## Fase 1 — Simulador de sinais vitais

- [ ] gerador_sinais.py — gera série temporal-base dentro da faixa de normalidade
      para frequência cardíaca, SpO2 e temperatura corporal
- [ ] injetor_ruido.py — aplica ruído gaussiano controlado sobre os períodos normais
- [ ] eventos.py — insere os quatro eventos anômalos rotulados (taquicardia,
      bradicardia, hipóxia, febre) em instantes controlados e registra o gabarito
- [ ] Testes unitários do simulador

## Fase 2 — Algoritmos de detecção

- [ ] limiar_simples.py — baseline: alerta imediato ao ultrapassar o limite clínico
- [ ] persistencia.py — alerta somente após N leituras consecutivas fora da faixa
- [ ] Testes unitários dos dois algoritmos com casos de borda

## Fase 3 — Orquestração com LangGraph

- [ ] estado.py — schema do estado do grafo (Pydantic)
- [ ] nos.py — funções de cada nó (simular, ruído, eventos, limiar simples,
      persistência, comparar, métricas, persistir)
- [ ] pipeline.py — monta o StateGraph e as arestas entre os nós
- [ ] Teste de execução ponta a ponta do grafo

## Fase 4 — Avaliação e métricas

- [ ] comparador.py — classifica cada alerta contra o gabarito (verdadeiro
      positivo, falso positivo, falso negativo)
- [ ] metricas.py — calcula tempo médio de detecção e taxa de falsos
      positivos/negativos por algoritmo e por tipo de evento
- [ ] Testes unitários com conjunto de dados conhecido

## Fase 5 — Persistência dos resultados

- [ ] Salvar sinais simulados, gabarito, alertas e métricas no SQLite
- [ ] Função de consulta para recuperar uma execução completa por id

## Fase 6 — Execução ponta a ponta

- [ ] main.py — roda o pipeline completo via LangGraph e imprime/loga o resumo
- [ ] Rodar pipeline completo pelo menos uma vez e validar resultados manualmente
- [ ] Ajustar parâmetros do simulador/algoritmos se necessário

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
