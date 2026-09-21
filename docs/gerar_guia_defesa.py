import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from front.dados.consultas import listar_execucoes, obter_gabarito, obter_metricas, obter_parametros
from front.dados.consultas_ml import obter_ultimo_resultado_ml
from front.dados.derivadas import calcular_comparacao_binaria_ml, calcular_indicadores_por_algoritmo
from pdf_utils import MARGEM_MM, RelatorioPDF

CAMINHO_SAIDA = Path(__file__).resolve().parent / "guia_defesa_tcc.pdf"


def obter_dados_regras() -> dict | None:
    """Busca os parâmetros, o gabarito e os indicadores da execução simulada mais recente."""
    execucoes = listar_execucoes()
    if not execucoes:
        return None
    execucao_id = execucoes[0][0]
    metricas = obter_metricas(execucao_id)
    return {"parametros": obter_parametros(execucao_id), "gabarito": obter_gabarito(execucao_id), "indicadores": calcular_indicadores_por_algoritmo(metricas)}


def montar_secao_capa(pdf: RelatorioPDF) -> None:
    pdf.titulo_principal("Guia de Defesa do TCC")
    pdf.subtitulo("WearGuard  - Uso de wearables e sensores no monitoramento remoto de pacientes")
    pdf.paragrafo("Este documento reúne, num só lugar, tudo que foi feito no projeto (as duas frentes: detecção por regras e machine learning), os números obtidos e como explicar cada decisão caso a banca pergunte. Não é um texto para ler na apresentação  - é um material de apoio para revisar antes e consultar durante a defesa.")


def montar_secao_visao_geral(pdf: RelatorioPDF) -> None:
    pdf.titulo_secao("1. Visão geral: duas frentes de trabalho")
    pdf.paragrafo("O projeto tem duas partes, com dados e objetivos diferentes:")
    pdf.item_lista("**Frente 1 (escopo original do projeto de pesquisa)**: um simulador gera sinais vitais fictícios (frequência cardíaca, SpO2 e temperatura corporal) e compara dois algoritmos de detecção de anomalias  - limiar simples e critério de persistência.")
    pdf.item_lista("**Frente 2 (extensão adicionada depois)**: um classificador de arritmias treinado com machine learning, usando eletrocardiograma (ECG) real de pacientes reais, de uma base pública. Esta frente não usa SpO2 nem temperatura  - só o sinal elétrico do coração.")
    pdf.paragrafo("As duas frentes respondem perguntas diferentes e usam dados diferentes. Isso é intencional e deve ficar claro na apresentação: a Frente 1 decide **quando alertar** a partir de um número resumido; a Frente 2 decide **que tipo de batimento** está acontecendo a partir da forma completa da onda.")


def montar_secao_frente_regras(pdf: RelatorioPDF, dados_regras: dict | None) -> None:
    pdf.titulo_secao("2. Frente 1  - Detecção por regras em sinais simulados")

    pdf.paragrafo("**Por que dados simulados, e não pacientes reais?** Dados de saúde são sensíveis pela Lei Geral de Proteção de Dados Pessoais (LGPD). Usar pacientes reais exigiria submissão e aprovação em Comitê de Ética em Pesquisa / Plataforma Brasil, processo que não seria viável dentro do prazo do TCC. Gerar dados sintéticos, com eventos e ruído controlados, permite testar e comparar os algoritmos com um gabarito conhecido (sabe-se exatamente onde cada evento foi inserido), o que também não seria possível com dados reais sem anotação prévia.")

    pdf.paragrafo("**Como o simulador funciona**: para cada sinal vital, gera-se primeiro uma série de valores dentro da faixa saudável (o \"sinal-base\"). Em seguida aplica-se ruído gaussiano pequeno, simulando a imprecisão natural de qualquer sensor. Por fim, em instantes sorteados, insere-se um evento anômalo real (por exemplo, 30 leituras seguidas de taquicardia), anotando exatamente onde ele começa e termina  - esse registro é o **gabarito**, a verdade contra a qual os algoritmos são avaliados.")

    pdf.paragrafo("**Os dois algoritmos e por que foram escolhidos**:")
    pdf.item_lista("**Limiar simples**: dispara alerta assim que uma única leitura ultrapassa o limite clínico. É o método mais comum na prática por ser simples de implementar, mas sensível a ruído  - um pico passageiro do sensor pode gerar alarme falso.")
    pdf.item_lista("**Critério de persistência**: só dispara alerta depois de 5 leituras seguidas fora da faixa normal. A ideia central da pesquisa é que ruído tende a ser passageiro, enquanto um evento clínico real se sustenta por várias leituras.")

    if dados_regras is not None and dados_regras["indicadores"]:
        pdf.paragrafo("**Resultados obtidos** (execução de referência, sinal com 600 leituras, 8 eventos anômalos inseridos: taquicardia, bradicardia, hipóxia e febre, 2 de cada):")
        for algoritmo, valores in dados_regras["indicadores"].items():
            nome = "Limiar simples" if algoritmo == "limiar_simples" else "Persistência"
            pdf.item_lista(f"**{nome}**: {valores['verdadeiros_positivos']} verdadeiros positivos, {valores['falsos_positivos']} falsos positivos, {valores['falsos_negativos']} falsos negativos, tempo médio de detecção {valores['tempo_medio_deteccao']} segundos, taxa de detecção {valores['taxa_deteccao'] * 100:.0f}%.")
        pdf.paragrafo("Nos testes rodados, os dois algoritmos detectaram 100% dos eventos reais (nenhum falso negativo). A diferença aparece nos falsos positivos: o limiar simples errou algumas vezes por causa de ruído; a persistência não errou nenhuma vez, ao custo de demorar mais (a média de tempo de detecção da persistência é maior, porque ela espera confirmar o padrão antes de alertar). Isso confirma a hipótese do projeto: o critério de persistência reduz falsos positivos ao custo de um tempo de detecção levemente maior.")
    else:
        pdf.paragrafo("Nenhuma execução de simulação foi encontrada no banco no momento da geração deste guia. Rode \"python -m src.main\" e gere este PDF de novo para incluir números reais aqui.")


def montar_secao_frente_ml(pdf: RelatorioPDF, resultado_ml: dict | None) -> None:
    pdf.titulo_secao("3. Frente 2  - Machine learning com ECG real")

    pdf.paragrafo("**Por que essa frente foi adicionada?** Para enriquecer a discussão do trabalho, comparando a filosofia de regras fixas (Frente 1) com uma abordagem que aprende padrões diretamente de dados reais anotados por especialistas. É importante deixar claro para a banca que esta frente **não estava no projeto de pesquisa original**  - foi um adicional proposto depois, e não usa SpO2 nem temperatura corporal, apenas o sinal de ECG.")

    pdf.paragrafo("**Base de dados**: MIT-BIH Arrhythmia Database, do PhysioNet, de acesso público e gratuito (não precisou de aprovação em Comitê de Ética porque os dados já são públicos e anonimizados, disponibilizados há décadas para pesquisa). É a base mais citada do mundo nesse tipo de estudo: 48 registros de ECG real de 47 pacientes, com cada batimento anotado por cardiologistas.")

    pdf.paragrafo("**Metodologia**: cada batimento é recortado como uma janela de sinal ao redor do pico R (o pico mais alto do batimento), normalizada em amplitude, mais dois números extras (os intervalos de tempo até o batimento anterior e seguinte). Os batimentos são agrupados em 5 categorias da norma AAMI EC57: normal, supraventricular, ventricular, fusão e desconhecido. O treino e o teste são separados **por paciente** (22 pacientes só no treino, 22 diferentes só no teste), técnica de de Chazal, O'Dwyer e Reilly (2004) que evita que o modelo \"decore\" características de um paciente específico.")

    pdf.paragrafo("**Algoritmo**: Random Forest (floresta aleatória), com balanceamento de classes. Escolhido por ser robusto, rápido de treinar, bem documentado na literatura de ECG, e mais fácil de explicar numa defesa do que uma rede neural profunda.")

    if resultado_ml is not None:
        total_treino = f"{resultado_ml['total_batimentos_treino']:,}".replace(",", ".")
        total_teste = f"{resultado_ml['total_batimentos_teste']:,}".replace(",", ".")
        pdf.paragrafo(f"**Resultados obtidos**: acurácia geral de {resultado_ml['acuracia'] * 100:.1f}% no conjunto de teste ({total_teste} batimentos de {total_treino} de treino), com macro-F1 de {resultado_ml['macro_f1']:.3f}.")

        tabela = resultado_ml["metricas_por_classe"]
        nomes = {"normal": "Normal", "supraventricular": "Supraventricular", "ventricular": "Ventricular", "fusao": "Fusão", "desconhecido": "Desconhecido"}
        for _, linha in tabela.iterrows():
            pdf.item_lista(f"**{nomes.get(linha['classe'], linha['classe'])}**: precisão {linha['precisao']:.3f}, recall {linha['recall']:.3f}, F1 {linha['f1']:.3f} ({int(linha['suporte'])} batimentos no teste)")

        pdf.paragrafo("O modelo vai muito bem em batimentos normais e ventriculares (as classes com mais exemplos de treino), e mal em supraventricular, fusão e desconhecido, que são raras na base e mais difíceis de distinguir só pela forma da onda. Isso é um resultado conhecido e documentado na literatura para esse tipo de avaliação (separação por paciente), não um erro de implementação  - e vale a pena apresentar isso com naturalidade: reconhecer a limitação é parte do rigor científico do trabalho.")
    else:
        pdf.paragrafo("Nenhum treinamento de ML foi encontrado no banco no momento da geração deste guia. Rode \"python -m src.ml.treinar\" e gere este PDF de novo para incluir números reais aqui.")


def montar_secao_comparacao(pdf: RelatorioPDF, dados_regras: dict | None, resultado_ml: dict | None) -> None:
    pdf.titulo_secao("4. Comparação entre as duas frentes")
    pdf.paragrafo("As duas frentes resolvem problemas diferentes sobre dados diferentes, então não dá para comparar \"acurácia\" com \"falsos positivos\" diretamente. Para tornar a comparação justa, as 4 classes de arritmia do ML foram agrupadas em \"anômalo\" contra \"normal\", reduzindo o problema à mesma pergunta binária que os algoritmos de regra respondem: das vezes que o sistema alertou, quantas estavam erradas (taxa de falso alarme)? Dos problemas reais, quantos foram detectados (taxa de detecção)?")

    if dados_regras is not None and dados_regras["indicadores"] and resultado_ml is not None:
        comparacao_ml = calcular_comparacao_binaria_ml(resultado_ml["matriz_confusao"])
        for algoritmo, valores in dados_regras["indicadores"].items():
            nome = "Limiar simples" if algoritmo == "limiar_simples" else "Persistência"
            pdf.item_lista(f"**{nome}**: taxa de falso alarme {valores['taxa_falsos_positivos'] * 100:.1f}%, taxa de detecção {valores['taxa_deteccao'] * 100:.1f}%")
        pdf.item_lista(f"**Machine learning (binarizado)**: taxa de falso alarme {comparacao_ml['taxa_falsos_positivos'] * 100:.1f}%, taxa de detecção {comparacao_ml['taxa_deteccao'] * 100:.1f}%")
        pdf.paragrafo("O ML sai pior nessa comparação binarizada porque sua tarefa original é mais difícil (classificar o tipo certo entre 5 categorias, não só decidir alerta sim/não sobre um número já resumido). Isso deve ser apresentado como um ponto de discussão do trabalho, não escondido: mostra que a escolha entre regra fixa e aprendizado de máquina depende do tipo de dado e da pergunta que se quer responder, não existe uma resposta universalmente melhor.")
    else:
        pdf.paragrafo("Números não disponíveis no momento da geração deste guia  - rode as duas frentes e gere o PDF de novo.")


def montar_secao_perguntas(pdf: RelatorioPDF) -> None:
    pdf.titulo_secao("5. Perguntas prováveis da banca e respostas sugeridas")

    perguntas_respostas = [
        ("Por que usar dados simulados em vez de pacientes reais na Frente 1?", "Dados de saúde são protegidos pela LGPD. Usar pacientes reais exigiria aprovação em Comitê de Ética / Plataforma Brasil, processo incompatível com o prazo do TCC. A simulação permite controlar exatamente onde cada evento acontece (o gabarito), o que é necessário para medir com precisão o tempo de detecção e a taxa de falsos positivos de cada algoritmo."),
        ("Por que comparar dois algoritmos, e não propor só um método novo?", "A pergunta de pesquisa do projeto é comparativa por definição: queríamos medir se o critério de persistência melhora a detecção em relação ao limiar simples. A comparação controlada, com os dois algoritmos rodando sobre o mesmo conjunto de dados, é o que permite responder essa pergunta com rigor."),
        ("A persistência demora mais para alertar  - isso não é uma desvantagem?", "É um custo aceito conscientemente. A literatura de monitoramento clínico (Van Rossum et al., 2022) documenta o problema da \"fadiga de alarme\": quando um sistema alerta demais por engano, a equipe de saúde passa a desconfiar e ignorar os alertas, inclusive os reais. Poucos segundos a mais de espera, em troca de menos alarmes falsos, tende a ser um trade-off vantajoso na prática."),
        ("O que motivou incluir machine learning se não estava no escopo original?", "A ideia foi enriquecer a discussão comparando duas filosofias de detecção: regras fixas definidas a priori versus um modelo que aprende padrões diretamente de dados reais anotados por especialistas. Isso mostra domínio de mais de uma abordagem e abre espaço para discutir quando cada uma faz sentido."),
        ("A acurácia do modelo de ML é 92%, mas o macro-F1 é só 0,37  - isso não é contraditório?", "Não, é esperado em dados desbalanceados. A classe \"normal\" tem dezenas de milhares de exemplos, contra poucas centenas nas classes raras. Um modelo que acerta quase tudo na classe majoritária já tem acurácia alta, mesmo errando bastante nas classes raras. O macro-F1 dá peso igual a todas as classes, por isso é a métrica mais honesta para julgar o modelo aqui  - e ela expõe justamente essa fraqueza nas classes raras."),
        ("Por que Random Forest, e não uma rede neural?", "Random Forest é um método robusto, rápido de treinar sem necessidade de GPU, amplamente documentado na literatura de ECG, e mais fácil de explicar e defender do que uma rede neural profunda. Redes neurais (como em Kachuee et al., 2018) são citadas no trabalho como direção de melhoria futura, não como algo que faltou fazer por falta de conhecimento."),
        ("Por que a Frente 1 usa dados simulados e a Frente 2 usa dados reais? Não é inconsistente?", "Não  - cada frente usa o tipo de dado mais adequado à sua pergunta. A Frente 1 precisa de controle total sobre quando cada evento acontece (o gabarito), algo que só a simulação garante. A Frente 2 tem à disposição uma base pública, real, já anotada por especialistas e amplamente validada pela literatura (MIT-BIH)  - não fazia sentido simular ECG quando existe um padrão-ouro real e de acesso livre para essa tarefa específica."),
        ("Os resultados são reprodutíveis?", "Sim. A simulação usa uma semente aleatória fixa (semente_aleatoria = 42), então roda sempre com o mesmo resultado. O treinamento de ML usa a mesma base pública e o mesmo protocolo de split de pacientes a cada execução. Todo o código está versionado e documentado."),
        ("O desempenho fraco do ML em algumas classes não enfraquece o trabalho?", "Ao contrário  - reconhecer e explicar uma limitação, com base na literatura da área, é rigor científico, não fraqueza. O documento de metodologia já discute isso e aponta caminhos concretos de melhoria (mais características morfológicas, redes neurais, técnicas para classes raras)."),
    ]

    for pergunta, resposta in perguntas_respostas:
        pdf.set_font("Times", "BI", 12)
        pdf.multi_cell(w = 0, h = 6.5, text = f"P: {pergunta}")
        pdf.ln(1)
        pdf.caixa_destaque(f"R: {resposta}")


def montar_secao_pontos_fortes(pdf: RelatorioPDF) -> None:
    pdf.titulo_secao("6. Pontos fortes para destacar na apresentação")
    pdf.item_lista("Uso de uma base de dados padrão-ouro da literatura (MIT-BIH) com a separação correta por paciente, evitando um erro metodológico comum em trabalhos que classificam ECG.")
    pdf.item_lista("Reprodutibilidade: semente aleatória fixa, código versionado, dataset público.")
    pdf.item_lista("Duas abordagens de detecção comparadas de forma controlada e justa, com métricas apropriadas para cada uma.")
    pdf.item_lista("Dashboard interativo para visualizar sinais, alertas e métricas das duas frentes.")
    pdf.item_lista("Discussão honesta das limitações, com caminhos concretos de trabalho futuro apontados na literatura.")


def montar_secao_referencias(pdf: RelatorioPDF) -> None:
    pdf.titulo_secao("7. Referências")
    pdf.referencia("GOLDBERGER, A. L. et al. **PhysioBank, PhysioToolkit, and PhysioNet: components of a new research resource for complex physiologic signals.** Circulation, v. 101, n. 23, p. e215-e220, 2000.", "https://doi.org/10.1161/01.CIR.101.23.e215")
    pdf.referencia("MOODY, G. B.; MARK, R. G. **The impact of the MIT-BIH Arrhythmia Database.** IEEE Engineering in Medicine and Biology Magazine, v. 20, n. 3, p. 45-50, 2001.", "https://doi.org/10.1109/51.932724")
    pdf.referencia("DE CHAZAL, P.; O'DWYER, M.; REILLY, R. B. **Automatic classification of heartbeats using ECG morphology and heartbeat interval features.** IEEE Transactions on Biomedical Engineering, v. 51, n. 7, p. 1196-1206, 2004.", "https://doi.org/10.1109/TBME.2004.827359")
    pdf.referencia("ASSOCIATION FOR THE ADVANCEMENT OF MEDICAL INSTRUMENTATION (AAMI). **ANSI/AAMI EC57: Testing and reporting performance results of cardiac rhythm and ST segment measurement algorithms.** 1998/2012.", "https://webstore.ansi.org/standards/aami/ansiaamiec572012r2020")
    pdf.referencia("KACHUEE, M.; FAZELI, S.; SARRAFZADEH, M. **ECG Heartbeat Classification: A Deep Transferable Representation.** In: IEEE International Conference on Healthcare Informatics (ICHI), 2018.", "https://arxiv.org/abs/1805.00794")
    pdf.referencia("PEDREGOSA, F. et al. **Scikit-learn: Machine Learning in Python.** Journal of Machine Learning Research, v. 12, p. 2825-2830, 2011.", "https://www.jmlr.org/papers/v12/pedregosa11a.html")
    pdf.referencia("VAN ROSSUM, M. C. et al. **Adaptive threshold-based alarm strategies for continuous vital signs monitoring.** Journal of Clinical Monitoring and Computing, v. 36, p. 407-417, 2022.", "https://doi.org/10.1007/s10877-021-00666-4")


def gerar_guia() -> None:
    """Gera o PDF completo do guia de defesa, com números reais das duas frentes do projeto."""
    dados_regras = obter_dados_regras()
    resultado_ml = obter_ultimo_resultado_ml()

    pdf = RelatorioPDF(format = "A4")
    pdf.set_margins(left = MARGEM_MM, top = MARGEM_MM, right = MARGEM_MM)
    pdf.set_auto_page_break(auto = True, margin = MARGEM_MM)
    pdf.add_page()

    montar_secao_capa(pdf)
    montar_secao_visao_geral(pdf)
    montar_secao_frente_regras(pdf, dados_regras)
    montar_secao_frente_ml(pdf, resultado_ml)
    montar_secao_comparacao(pdf, dados_regras, resultado_ml)
    montar_secao_perguntas(pdf)
    montar_secao_pontos_fortes(pdf)
    montar_secao_referencias(pdf)

    CAMINHO_SAIDA.parent.mkdir(parents = True, exist_ok = True)
    pdf.output(str(CAMINHO_SAIDA))
    print(f"Guia de defesa gerado em {CAMINHO_SAIDA}")


if __name__ == "__main__":
    gerar_guia()
