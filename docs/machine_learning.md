# Machine Learning para detecção de arritmias — guia sem jargão

Este documento explica, do zero, a parte de Machine Learning (ML) adicionada ao WearGuard.
Ela **não estava no PDF original do TCC** — foi incluída depois, para comparar a abordagem
baseada em regras (limiar simples / persistência, sobre sinais simulados) com uma abordagem
baseada em aprendizado de máquina treinada com **ECG real de pacientes**.

Se você não conhece nada de ML, comece por aqui antes de olhar o código.

---

## 1. Qual é o problema, em uma frase

Dado um pedaço de sinal de ECG (o "batimento"), o modelo tenta responder: **esse batimento é
normal ou é um tipo de arritmia — e qual tipo?**

Isso é diferente da parte de regras do WearGuard, que olha só para números resumidos
(frequência cardíaca, SpO2, temperatura) e decide "alerta" ou "não alerta". Aqui o modelo olha
para o **formato da onda do ECG em si** — é um problema mais rico e mais próximo do que
cardiologistas realmente fazem ao olhar um ECG.

## 2. De onde vieram os dados

Usamos o **MIT-BIH Arrhythmia Database**, baixado diretamente do PhysioNet
(https://physionet.org/content/mitdb/1.0.0/), de acesso público e gratuito, sem precisar de
cadastro. É a base de dados mais citada do mundo em pesquisa de detecção de arritmia por ECG,
usada em centenas de artigos científicos desde os anos 2000. Ela tem 48 registros de ECG de
meia hora cada, de 47 pacientes diferentes, cada batimento **anotado por cardiologistas** (ou
seja, o gabarito não é sintético — é uma opinião médica real).

Baixamos os arquivos com a biblioteca `wfdb` (a biblioteca oficial em Python para ler o formato
de arquivo do PhysioNet) e guardamos em `data/mitbih_raw/` (não vai para o Git, é pesado).

## 3. O que é um "batimento" pra gente, tecnicamente

Cada arquivo de anotação já marca o instante exato de cada **pico R** (o pico mais alto de
cada batimento no ECG) e o **tipo daquele batimento**, segundo o cardiologista que revisou o
exame. Para cada pico R, recortamos uma janela de sinal ao redor dele: 90 amostras antes e 110
depois (a 360 amostras por segundo, isso é pouco mais de meio segundo de sinal, cobrindo um
batimento inteiro). Isso vira um "segmento" — uma lista de ~200 números que representa a forma
daquele batimento.

Além da forma da onda, adicionamos 2 números por batimento: o **intervalo RR anterior** (tempo
desde o batimento anterior) e o **intervalo RR seguinte** (tempo até o próximo batimento). Essa
é a mesma técnica usada por de Chazal et al. (2004): batimentos supraventriculares muitas vezes
têm o MESMO formato de onda que um batimento normal — o que trai eles é o **ritmo** (vêm mais
cedo ou mais tarde do que deveriam), não o formato. Sem essa informação de tempo, o modelo fica
praticamente cego para esse tipo de arritmia.

Ver `src/ml/dados.py`, função `extrair_batimentos_do_registro`.

## 4. As 5 categorias (padrão AAMI)

Os cardiologistas usam dezenas de códigos diferentes para anotar batimentos (ex: `N`, `L`, `R`,
`A`, `V`, `F`...). Isso é detalhe demais para um primeiro modelo, então agrupamos nos 5 grupos
padronizados pela norma **AAMI EC57** (usada por praticamente todo artigo científico da área):

| Grupo (código interno) | Nome              | O que significa, em termos simples                                  |
|-------------------------|-------------------|-----------------------------------------------------------------------|
| `normal`                | Normal            | Batimento comum, sem nada de anormal                                  |
| `supraventricular`      | Supraventricular  | Nasce "acima" dos ventrículos (ex: extrassístole atrial)               |
| `ventricular`           | Ventricular       | Nasce no ventrículo, geralmente mais preocupante (ex: PVC)             |
| `fusao`                 | Fusão             | Mistura de um batimento normal com um ventricular ao mesmo tempo       |
| `desconhecido`          | Desconhecido      | Batimento de marca-passo ou não classificável                         |

Esse mapeamento está em `src/ml/config.py`, na variável `MAPEAMENTO_AAMI`.

## 5. Como separamos treino e teste (e por que isso importa)

**Erro comum em ML médico**: se você pegar todos os batimentos de todos os pacientes,
embaralhar tudo e separar aleatoriamente em treino/teste, o modelo pode "decorar" o jeito que
o ECG de um paciente específico se parece (cada pessoa tem um ECG levemente diferente) e
depois "reconhecer" esse mesmo paciente no teste — dando uma acurácia ótima e enganosa, que
não se sustenta em um paciente novo.

O jeito certo, usado no artigo de referência da área (**de Chazal et al., 2004**), é separar
por **paciente**: um grupo de 22 pacientes só aparece no treino (chamado `DS1`), outro grupo de
22 pacientes, totalmente diferente, só aparece no teste (`DS2`). Assim, o teste mede o que
realmente importa: **o modelo funciona em gente que ele nunca viu?**

Os 4 registros restantes (102, 104, 107, 217) são excluídos por convenção da literatura, porque
têm predominantemente batimentos de marca-passo, que distorcem a comparação. Ver
`src/ml/config.py`, listas `REGISTROS_TREINO` e `REGISTROS_TESTE`.

## 6. O modelo: Random Forest

Escolhemos um **Random Forest** (floresta aleatória), um dos modelos clássicos de ML mais
usados e mais fáceis de confiar:

- Ele treina várias "árvores de decisão" (cada uma é tipo um fluxograma de perguntas do tipo
  "esse ponto do sinal é maior que X?"), cada árvore vendo uma amostra um pouco diferente dos
  dados, e no final todas "votam" na resposta.
- Não precisa de GPU, treina em segundos/minutos, e é bem documentado na literatura de ECG
  (é uma alternativa clássica às redes neurais profundas usadas em trabalhos mais recentes,
  como o de Kachuee et al., 2018).
- É mais fácil de explicar numa banca de TCC do que uma rede neural — dá pra dizer exatamente
  "o modelo olhou o formato da onda e comparou com padrões que viu no treino", sem precisar
  entrar em camadas e pesos.

Um detalhe técnico importante: batimentos `normal` são MUITO mais comuns que os outros tipos
(desbalanceamento de classes). Se ignorássemos isso, o modelo poderia "trapacear" chutando
sempre `normal` e ainda parecer ter acurácia alta. Por isso usamos `class_weight = "balanced"`
no treino, que faz o modelo prestar mais atenção nas classes raras — e por isso também
olhamos o **macro-F1** (explicado abaixo), não só a acurácia, para julgar o modelo de verdade.

Ver `src/ml/modelo.py`.

## 7. Como ler as métricas (sem jargão)

- **Acurácia**: de todos os batimentos do teste, quantos % o modelo acertou. Fácil de entender,
  mas engana em dados desbalanceados (ver acima).
- **Precisão** (por classe): das vezes que o modelo disse "isso é ventricular", quantas vezes
  ele realmente acertou? Precisão baixa = o modelo grita alerta demais à toa.
- **Recall** (por classe): de todos os batimentos que EREM realmente ventriculares, quantos o
  modelo pegou? Recall baixo = o modelo deixa passar casos reais.
- **F1**: uma média que só fica alta se precisão E recall estiverem altos ao mesmo tempo (não
  dá pra "trapacear" o F1 focando só em um dos dois).
- **Macro-F1**: a média do F1 das 5 classes, dando o mesmo peso pra cada uma (não deixa a
  classe `normal`, que tem muito mais exemplos, dominar a média). É a métrica mais justa pra
  julgar esse modelo, e a que recomendamos citar como "resultado principal" no TCC.
- **Matriz de confusão**: uma tabela onde a linha é o que o cardiologista anotou e a coluna é o
  que o modelo previu. A diagonal principal é o que o modelo acertou; fora da diagonal são os
  erros — e essa tabela mostra especificamente COM O QUÊ o modelo confunde cada classe (ex: se
  ele confunde muito `supraventricular` com `normal`, por exemplo).

Ver `src/ml/avaliacao.py`.

## 8. Como essa parte se conecta com o resto do WearGuard

Ela é **independente** do pipeline de simulação (LangGraph, sinais sintéticos, limiar simples
vs. persistência) — usa dados reais diferentes, resolve um problema diferente (classificar o
formato da onda vs. decidir se um número resumido está fora da faixa). As duas partes ficam
lado a lado no dashboard, e a comparação que faz sentido para o TCC é conceitual:

> "A abordagem baseada em regras é simples e funciona bem quando o dado é um único número
> (frequência cardíaca, SpO2, temperatura) — mas para identificar o TIPO de arritmia a partir
> do formato de onda do ECG, é necessário aprendizado de máquina, que aprende os padrões
> diretamente dos dados anotados por especialistas."

Isso é uma seção adicional honesta pro TCC: mostra que o grupo foi além do escopo original e
comparou a filosofia "regra fixa" com a filosofia "aprender com dados reais".

## 9. Resultado obtido nesta execução (referência)

Com os parâmetros padrão do projeto, o treinamento chegou a:

| Classe            | Precisão | Recall | F1    | Quantidade no teste |
|-------------------|----------|--------|-------|----------------------|
| Normal             | 0.949    | 0.967  | 0.958 | 44.245                |
| Supraventricular   | 0.606    | 0.034  | 0.065 | 1.837                 |
| Ventricular        | 0.714    | 0.922  | 0.805 | 3.220                 |
| Fusão              | 0.008    | 0.008  | 0.008 | 388                   |
| Desconhecido       | 0.000    | 0.000  | 0.000 | 7                     |

Acurácia geral: 92,2%. Macro-F1: 0,367.

**Como interpretar isso honestamente pro TCC**: o modelo ficou muito bom em `normal` e bom em
`ventricular` (as duas classes com mais exemplos de treino). Ficou fraco em `supraventricular`
(recall baixo — perde a maioria dos casos reais) e muito fraco em `fusão`/`desconhecido`, que
têm poucos exemplos no teste (388 e 7, respectivamente — qualquer erro pesa muito na métrica).
Isso **não é um bug**: é um resultado consistente com a literatura da área nesse mesmo tipo de
avaliação (inter-paciente, sem features adicionais de morfologia mais sofisticadas). É,
inclusive, um achado citável: mostra que classificar arritmia supraventricular por ECG é
genuinamente difícil, e abre espaço pra sugerir, na seção de "trabalhos futuros" do TCC, o uso
de mais características (ex: posição do complexo QRS, ondas P) ou modelos mais sofisticados
(redes neurais, como em Kachuee et al., 2018).

## 10. Como rodar

```powershell
.venv\Scripts\Activate.ps1
python -m src.ml.treinar
```

Na primeira vez, ele extrai os batimentos de todos os registros e salva um cache em
`data/mitbih_batimentos.npz` (demora um pouco). Nas próximas vezes, usa o cache e é bem mais
rápido. O modelo treinado fica salvo em `data/modelo_arritmia.joblib`, e o resultado
(acurácia, métricas por classe, matriz de confusão) fica salvo no mesmo banco SQLite do
projeto, em tabelas próprias (`modelos_ml`, `metricas_ml`, `matriz_confusao_ml`).

O resultado aparece automaticamente na aba **Machine Learning** do dashboard
(`streamlit run front/app.py`).

## 11. Referências para citar no TCC

- MOODY, G. B.; MARK, R. G. The impact of the MIT-BIH Arrhythmia Database. **IEEE Engineering
  in Medicine and Biology Magazine**, v. 20, n. 3, p. 45-50, 2001.
- DE CHAZAL, P.; O'DWYER, M.; REILLY, R. B. Automatic classification of heartbeats using ECG
  morphology and heartbeat interval features. **IEEE Transactions on Biomedical Engineering**,
  v. 51, n. 7, p. 1196-1206, 2004. (fonte do split de pacientes DS1/DS2 usado aqui)
- ASSOCIATION FOR THE ADVANCEMENT OF MEDICAL INSTRUMENTATION (AAMI). **ANSI/AAMI EC57:
  Testing and reporting performance results of cardiac rhythm and ST segment measurement
  algorithms**. 1998/2012. (fonte das 5 categorias de batimento)
- KACHUEE, M.; FAZELI, S.; SARRAFZADEH, M. ECG Heartbeat Classification: A Deep Transferable
  Representation. In: **IEEE International Conference on Healthcare Informatics (ICHI)**,
  2018. (trabalho de referência mais recente na mesma linha, usando redes neurais)
