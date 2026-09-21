from fpdf import FPDF

MARGEM_MM = 30
RECUO_PRIMEIRA_LINHA = "        "
COR_LINK = (37, 99, 235)


class RelatorioPDF(FPDF):
    """Documento em fonte serifada (Times), com margens generosas, recuo de parágrafo e formatação mínima."""

    def titulo_principal(self, texto: str) -> None:
        self.set_font("Times", "B", 16)
        self.multi_cell(w = 0, h = 8, text = texto, align = "C")
        self.ln(4)

    def subtitulo(self, texto: str) -> None:
        self.set_font("Times", "I", 11)
        self.set_text_color(90, 90, 90)
        self.multi_cell(w = 0, h = 6, text = texto, align = "C")
        self.set_text_color(0, 0, 0)
        self.ln(8)

    def titulo_secao(self, texto: str) -> None:
        self.set_font("Times", "B", 13)
        self.ln(4)
        self.multi_cell(w = 0, h = 8, text = texto)
        self.ln(1)

    def paragrafo(self, texto: str) -> None:
        self.set_font("Times", "", 12)
        self.multi_cell(w = 0, h = 6.5, text = RECUO_PRIMEIRA_LINHA + texto, align = "J", markdown = True)
        self.ln(2)

    def item_lista(self, texto: str) -> None:
        self.set_font("Times", "", 12)
        self.set_x(self.l_margin + 6)
        self.multi_cell(w = self.epw - 6, h = 6.5, text = f"- {texto}", markdown = True)
        self.ln(1)

    def referencia(self, texto: str, url: str) -> None:
        """Escreve uma referência bibliográfica (com o título em negrito) seguida do link clicável."""
        self.set_x(self.l_margin + 6)
        self.set_font("Times", "", 12)
        self.multi_cell(w = self.epw - 6, h = 6.5, text = f"- {texto}", markdown = True)
        self.set_x(self.l_margin + 6)
        self.set_font("Times", "U", 11)
        self.set_text_color(*COR_LINK)
        self.write(h = 6, text = f"Disponível em: {url}", link = url)
        self.set_text_color(0, 0, 0)
        self.ln(9)

    def caixa_destaque(self, texto: str) -> None:
        """Escreve um bloco com fundo suave, usado para respostas sugeridas de defesa."""
        self.set_fill_color(240, 244, 250)
        self.set_font("Times", "", 12)
        self.multi_cell(w = 0, h = 6.5, text = texto, align = "J", markdown = True, fill = True, padding = 4)
        self.ln(3)
