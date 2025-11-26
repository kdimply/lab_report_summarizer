# backend/report_generator.py

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor

def generate_pdf_report(analyzed_df, summary, chart_path, output_path):
    """Generates a complete PDF report using a chart IMAGE FILE, not a figure."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # ---------- Title ----------
    story.append(Paragraph("Your Simplified Lab Report", styles['h1']))
    story.append(Spacer(1, 0.25 * inch))

    # ---------- Summary ----------
    story.append(Paragraph("AI-Generated Summary", styles['h2']))
    story.append(Paragraph(summary.replace("\n", "<br/>"), styles['BodyText']))
    story.append(Spacer(1, 0.25 * inch))

    # ---------- Chart (IMAGE file) ----------
    if chart_path and isinstance(chart_path, str):
        try:
            story.append(Image(chart_path, width=6 * inch, height=4 * inch))
            story.append(Spacer(1, 0.25 * inch))
        except Exception as e:
            story.append(Paragraph(f"(Chart could not be loaded: {e})", styles['BodyText']))

    # ---------- Results Table ----------
    story.append(Paragraph("Detailed Results", styles['h2']))

    colors = {
        'Normal': HexColor('#28a745'),
        'Low': HexColor('#ffc107'),
        'High': HexColor('#dc3545'),
        'Slightly Low': HexColor('#ffc107'),
        'Slightly High': HexColor('#ff6f61'),
        'Moderately High': HexColor('#ff3b3b'),
        'Severely High': HexColor('#c82333'),
        'Severely Low': HexColor('#ffb347'),
    }

    data = [analyzed_df.columns.tolist()] + analyzed_df.values.tolist()

    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4a4a4a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), HexColor('#ffffff')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f2f2f2')),
        ('GRID', (0, 0), (-1, -1), 1, HexColor('#cccccc')),
    ])

    # Highlight rows based on status
    for i, row in enumerate(analyzed_df.itertuples(), 1):
        color = colors.get(row.Status)
        if color:
            style.add('BACKGROUND', (0, i), (-1, i), color)
            style.add('TEXTCOLOR', (0, i), (-1, i), HexColor('#ffffff'))

    table.setStyle(style)
    story.append(table)

    # ---------- Build PDF ----------
    doc.build(story)
