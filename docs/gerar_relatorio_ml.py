import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from front.dados.consultas_ml import obter_ultimo_resultado_ml
from pdf_utils import MARGEM_MM, RelatorioPDF

CAMINHO_SAIDA = Path(__file__).resolve().parent / "machine_learning_relatorio.pdf"

NOMES_CLASSES_EM_PORTUGUES = {"normal": "Normal", "supraventricular": "Supraventricular", "ventricular": "Ventricular", "fusao": "Fusão", "desconhecido": "Desconhecido"}


def montar_secao_resultados(pdf: RelatorioPDF) -> None:
    """Monta a seção de resultados usando os números reais do último treinamento salvo no banco."""
    resultado = obter_ultimo_resultado_ml()

    pdf.titulo_secao("6. Resultados obtidos")

    if resultado is None:
        pdf.paragrafo("Nenhum treinamento havia sido executado no momento da geração deste relatório.")
        return

    total_treino = f"{resultado['total_batimentos_treino']:,}".replace(",", ".")
    total_teste = f"{resultado['total_batimentos_teste']:,}".replace(",", ".")
    pdf.paragrafo(f"**Acurácia geral** no conjunto de teste: {resultado['acuracia'] * 100:.1f} por cento. **Macro-F1** (média das 5 classes com peso igual): {resultado['macro_f1']:.3f}. Batimentos de treino: {total_treino}. Batimentos de teste: {total_teste}.")

    tabela = resultado["metricas_por_classe"]
    for _, linha in tabela.iterrows():
        nome_classe = NOMES_CLASSES_EM_PORTUGUES.get(linha["classe"], linha["classe"])
        pdf.item_lista(f"**{nome_classe}**: precisão {linha['precisao']:.3f}, recall {linha['recall']:.3f}, F1 {linha['f1']:.3f}, suporte no teste {int(linha['suporte'])} batimentos")

    pdf.paragrafo("O desempenho é forte nas classes normal e ventricular, que possuem mais exemplos de treino. É fraco em supraventricular, fusão e desconhecido, que são raras na base e mais difíceis de distinguir apenas pela forma da onda. Este é um resultado consistente com a literatura da área para o mesmo tipo de avaliação (separação por paciente), e não um defeito de implementação.")


def gerar_relatorio() -> None:
    """Gera o PDF completo do relatório de machine learning."""
    pdf = RelatorioPDF(format = "A4")
    pdf.set_margins(left = MARGEM_MM, top = MARGEM_MM, right = MARGEM_MM)
    pdf.set_auto_page_break(auto = True, margin = MARGEM_MM)
    pdf.add_page()

    pdf.titulo_principal("Classificação de Arritmias com Machine Learning")
    pdf.subtitulo("Complemento ao projeto WearGuard - Uso de wearables e sensores no monitoramento remoto de pacientes")

    pdf.titulo_secao("1. Introdução e motivação")
    pdf.paragrafo("O projeto **WearGuard**, conforme definido no projeto de pesquisa original, compara duas estratégias de detecção de anomalias fisiológicas em dados simulados de wearables: um método de **limiar simples** e um método com **critério de persistência**. Essas duas estratégias avaliam apenas valores numéricos resumidos (frequência cardíaca, saturação de oxigênio e temperatura corporal) contra faixas de referência clínica.")
    pdf.paragrafo("Este relatório documenta uma extensão do projeto, realizada após a entrega do escopo original: a adição de um classificador de arritmias baseado em **machine learning**, treinado com sinais reais de eletrocardiograma (ECG). O objetivo é comparar, de forma conceitual, uma abordagem baseada em regras fixas com uma abordagem que aprende padrões diretamente de dados anotados por especialistas.")

    pdf.titulo_secao("2. Base de dados utilizada")
    pdf.paragrafo("Foi utilizada a base **MIT-BIH Arrhythmia Database**, disponibilizada publicamente pelo **PhysioNet**, de acesso aberto e gratuito. Trata-se da base de dados mais citada na literatura científica de detecção de arritmia por ECG, com registros desde a década de 1980.")
    pdf.paragrafo("A base contém 48 registros de ECG de meia hora, provenientes de 47 pacientes distintos, com cada batimento cardíaco anotado individualmente por cardiologistas quanto ao seu tipo. Por convenção da literatura, quatro registros (102, 104, 107 e 217) foram excluídos da análise por conterem predominantemente batimentos de marca-passo, que distorcem a comparação entre classes.")

    pdf.titulo_secao("3. Metodologia")
    pdf.paragrafo("Para cada batimento anotado, foi extraído um segmento do sinal de ECG centrado no pico R (90 amostras antes e 110 amostras depois, a uma frequência de amostragem de 360 Hz), normalizado em amplitude. A esse segmento foram adicionados dois valores: os **intervalos RR** (tempo até o batimento anterior e até o batimento seguinte), pois arritmias supraventriculares frequentemente possuem forma de onda semelhante à de um batimento normal, sendo o ritmo, e não a forma, o fator que as distingue.")
    pdf.paragrafo("Os batimentos foram agrupados nas cinco categorias definidas pela norma **AAMI EC57**, padrão adotado pela maior parte dos trabalhos científicos da área:")
    pdf.item_lista("**Normal**: batimento comum, sem alteração relevante")
    pdf.item_lista("**Supraventricular**: origem acima dos ventrículos (por exemplo, extrassístole atrial)")
    pdf.item_lista("**Ventricular**: origem no ventrículo, geralmente de maior relevância clínica")
    pdf.item_lista("**Fusão**: mistura de um batimento normal com um ventricular")
    pdf.item_lista("**Desconhecido**: batimento de marca-passo ou não classificável")
    pdf.paragrafo("A separação entre treino e teste foi feita por paciente, e não por batimento isolado, seguindo o protocolo estabelecido por de Chazal, O'Dwyer e Reilly (2004): 22 pacientes compõem o conjunto de treino e outros 22 pacientes, nunca vistos durante o treinamento, compõem o conjunto de teste. Essa separação evita que o modelo memorize características individuais de um paciente e superestime seu próprio desempenho, problema comum quando batimentos do mesmo paciente aparecem tanto no treino quanto no teste.")

    pdf.titulo_secao("4. Algoritmo de machine learning utilizado")
    pdf.paragrafo("O modelo escolhido foi uma **Random Forest** (floresta aleatória), um método clássico de aprendizado supervisionado que combina o voto de múltiplas árvores de decisão treinadas sobre subamostras distintas dos dados. A escolha se justifica por ser um método robusto, rápido de treinar sem necessidade de hardware especializado, amplamente documentado na literatura de classificação de ECG, e mais interpretável do que redes neurais profundas.")
    pdf.paragrafo("Como os batimentos normais são muito mais frequentes que os demais tipos na base de dados, o treinamento utilizou a opção de **balanceamento de classes** (class_weight=balanced) da biblioteca scikit-learn, que ajusta a importância de cada classe durante o treinamento na proporção inversa de sua frequência, evitando que o modelo simplesmente preveja sempre a classe majoritária.")

    pdf.titulo_secao("5. Métricas de avaliação")
    pdf.paragrafo("Foram utilizadas as métricas padrão de classificação multiclasse:")
    pdf.item_lista("**Acurácia**: proporção geral de batimentos classificados corretamente")
    pdf.item_lista("**Precisão** (por classe): dentre os batimentos que o modelo previu como pertencentes a uma classe, quantos realmente pertencem a ela")
    pdf.item_lista("**Recall** (por classe): dentre os batimentos que realmente pertencem a uma classe, quantos o modelo conseguiu identificar")
    pdf.item_lista("**F1** (por classe): média harmônica entre precisão e recall")
    pdf.item_lista("**Macro-F1**: média do F1 das cinco classes com peso igual, métrica mais adequada para dados desbalanceados do que a acurácia isolada")
    pdf.item_lista("**Matriz de confusão**: tabela cruzando a classe real (anotada pelo cardiologista) com a classe prevista pelo modelo")

    montar_secao_resultados(pdf)

    pdf.titulo_secao("7. Comparação com a abordagem baseada em regras")
    pdf.paragrafo("A comparação entre as duas frentes do projeto é **conceitual**, e não uma medição direta sob o mesmo protocolo, pois avaliam problemas distintos sobre dados distintos. A abordagem baseada em regras (limiar simples e persistência) opera sobre valores numéricos resumidos, simulados artificialmente, e decide entre alertar ou não alertar. Já o classificador de machine learning opera sobre a forma completa do sinal de ECG real, decidindo entre cinco categorias distintas de batimento.")
    pdf.paragrafo("A conclusão que se pode extrair dessa comparação é que regras fixas sobre um único valor numérico são adequadas quando o critério de decisão é simples e conhecido a priori (por exemplo, frequência cardíaca acima de cem batimentos por minuto), mas tornam-se insuficientes quando o padrão a ser identificado está na morfologia do sinal, caso em que o aprendizado a partir de dados anotados por especialistas se torna necessário.")

    pdf.titulo_secao("8. Limitações e trabalhos futuros")
    pdf.paragrafo("O desempenho reduzido nas classes supraventricular, fusão e desconhecido é uma limitação conhecida deste tipo de abordagem quando restrita a características simples de forma de onda e intervalo RR. Trabalhos futuros poderiam incorporar características morfológicas adicionais (por exemplo, detecção da onda P e do complexo QRS), técnicas de aumento de dados para as classes raras, ou modelos de aprendizado profundo, como o proposto por Kachuee, Fazeli e Sarrafzadeh (2018), que reportam ganhos nessas classes com redes neurais convolucionais.")

    pdf.titulo_secao("9. Referências")
    pdf.referencia("GOLDBERGER, A. L. et al. **PhysioBank, PhysioToolkit, and PhysioNet: components of a new research resource for complex physiologic signals.** Circulation, v. 101, n. 23, p. e215-e220, 2000.", "https://doi.org/10.1161/01.CIR.101.23.e215")
    pdf.referencia("MOODY, G. B.; MARK, R. G. **The impact of the MIT-BIH Arrhythmia Database.** IEEE Engineering in Medicine and Biology Magazine, v. 20, n. 3, p. 45-50, 2001.", "https://doi.org/10.1109/51.932724")
    pdf.referencia("DE CHAZAL, P.; O'DWYER, M.; REILLY, R. B. **Automatic classification of heartbeats using ECG morphology and heartbeat interval features.** IEEE Transactions on Biomedical Engineering, v. 51, n. 7, p. 1196-1206, 2004.", "https://doi.org/10.1109/TBME.2004.827359")
    pdf.referencia("ASSOCIATION FOR THE ADVANCEMENT OF MEDICAL INSTRUMENTATION (AAMI). **ANSI/AAMI EC57: Testing and reporting performance results of cardiac rhythm and ST segment measurement algorithms.** 1998/2012.", "https://webstore.ansi.org/standards/aami/ansiaamiec572012r2020")
    pdf.referencia("KACHUEE, M.; FAZELI, S.; SARRAFZADEH, M. **ECG Heartbeat Classification: A Deep Transferable Representation.** In: IEEE International Conference on Healthcare Informatics (ICHI), 2018.", "https://arxiv.org/abs/1805.00794")
    pdf.referencia("PEDREGOSA, F. et al. **Scikit-learn: Machine Learning in Python.** Journal of Machine Learning Research, v. 12, p. 2825-2830, 2011.", "https://www.jmlr.org/papers/v12/pedregosa11a.html")

    CAMINHO_SAIDA.parent.mkdir(parents = True, exist_ok = True)
    pdf.output(str(CAMINHO_SAIDA))
    print(f"Relatorio gerado em {CAMINHO_SAIDA}")


if __name__ == "__main__":
    gerar_relatorio()
