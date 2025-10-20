# backend/report_generator.py

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.colors import HexColor

def generate_pdf_report(analyzed_df, summary, chart_path, output_path):
    """Generates a complete PDF report."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = Paragraph("Your Simplified Lab Report", styles['h1'])
    story.append(title)
    story.append(Spacer(1, 0.25*inch))

    # Summary
    summary_header = Paragraph("AI-Generated Summary", styles['h2'])
    story.append(summary_header)
    summary_text = Paragraph(summary.replace('\n', '<br/>'), styles['BodyText'])
    story.append(summary_text)
    story.append(Spacer(1, 0.25*inch))

    # Visualization
    if chart_path:
        img = Image(chart_path, width=6*inch, height=4*inch)
        story.append(img)
        story.append(Spacer(1, 0.25*inch))

    # Results Table
    table_header = Paragraph("Detailed Results", styles['h2'])
    story.append(table_header)
    
    # Define colors
    colors = {'Normal': HexColor('#28a745'), 'Low': HexColor('#ffc107'), 'High': HexColor('#dc3545')}

    # Convert DataFrame to list of lists for the table
    data = [analyzed_df.columns.tolist()] + analyzed_df.values.tolist()
    
    table = Table(data)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#4a4a4a')),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), HexColor('#f2f2f2')),
        ('GRID', (0,0), (-1,-1), 1, HexColor('#cccccc'))
    ])
    
    # Add color to rows based on status
    for i, row in enumerate(analyzed_df.itertuples(), 1):
        status_color = colors.get(row.Status)
        if status_color:
            style.add('BACKGROUND', (0, i), (-1, i), status_color)
            style.add('TEXTCOLOR', (0, i), (-1, i), HexColor('#ffffff'))
    
    table.setStyle(style)
    story.append(table)
    
    doc.build(story)