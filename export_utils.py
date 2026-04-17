from fpdf import FPDF
from datetime import datetime


class PDFExport(FPDF):
    def header(self):
        """En-tête du PDF"""
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(10, 60, 120)
        self.cell(0, 10, "Assistant IA Souverain - DGAC", align="C")
        self.ln(6)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", align="C")
        self.ln(4)
        self.set_draw_color(0, 180, 216)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        """Pied de page du PDF"""
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Mistral AI FR | 100% Souverain", align="C")


def export_conversation_pdf(messages: list) -> bytes:
    """Exporte la conversation au format PDF"""
    pdf = PDFExport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    question_num = 1
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        sources = msg.get("sources", [])

        if role == "user":
            # Bloc question
            pdf.set_fill_color(230, 241, 251)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(10, 60, 120)
            pdf.cell(0, 8, f"Question {question_num}", fill=True, ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            # Nettoyer les caractères spéciaux
            clean = content.encode("latin-1", errors="replace").decode("latin-1")
            pdf.multi_cell(0, 6, clean)
            pdf.ln(3)
            question_num += 1

        elif role == "assistant":
            # Bloc réponse
            pdf.set_fill_color(240, 255, 240)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(5, 80, 40)
            pdf.cell(0, 8, "Réponse IA", fill=True, ln=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            clean = content.encode("latin-1", errors="replace").decode("latin-1")
            pdf.multi_cell(0, 6, clean)

            # Ajouter les sources si présentes
            if sources:
                pdf.ln(2)
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 6, "Sources consultées :", ln=True)
                for src in sources:
                    pdf.cell(0, 5, f"  - {src['file']} - Page {src['page']}", ln=True)

            pdf.ln(5)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)

    return bytes(pdf.output())