import os
from datetime import datetime
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

# Define cohesive corporate color palette
PRIMARY_COLOR = colors.HexColor("#0f172a")    # Deep Slate
SECONDARY_COLOR = colors.HexColor("#4f46e5")  # Indigo
ACCENT_COLOR = colors.HexColor("#0d9488")     # Teal
TEXT_DARK = colors.HexColor("#334155")        # Charcoal
TEXT_LIGHT = colors.HexColor("#64748b")       # Gray text
BG_LIGHT = colors.HexColor("#f8fafc")         # Light blue-gray background
BORDER_COLOR = colors.HexColor("#e2e8f0")     # Light border gray

class NumberedCanvas(canvas.Canvas):
    """Canvas for dynamically calculating total pages and drawing header/footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Suppress running header/footer on Page 1 (Cover Page)
        if self._pageNumber > 1:
            # Running Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(PRIMARY_COLOR)
            self.drawString(54, 750, "VOICE OF CUSTOMER AI")
            
            self.setFont("Helvetica", 8)
            self.setFillColor(TEXT_LIGHT)
            self.drawRightString(558, 750, "EXECUTIVE INSIGHTS REPORT")
            
            # Header rule
            self.setStrokeColor(BORDER_COLOR)
            self.setLineWidth(0.75)
            self.line(54, 742, 558, 742)
            
            # Running Footer
            self.line(54, 48, 558, 48)
            
            self.setFont("Helvetica", 8)
            self.setFillColor(TEXT_LIGHT)
            self.drawString(54, 32, "CONFIDENTIAL — INTERNAL USE ONLY")
            
            page_str = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 32, page_str)
            
        self.restoreState()

def generate_pdf_report(report_id, filename, stats, summary_data, df_feedback, output_path):
    """Generates a professional executive PDF report."""
    # Ensure reports directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=72,  # Give room for running header
        bottomMargin=72  # Give room for running footer
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=PRIMARY_COLOR,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=SECONDARY_COLOR,
        spaceAfter=40
    )
    
    h1_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SubSectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY_COLOR,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK,
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=6
    )
    
    metadata_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=PRIMARY_COLOR
    )
    
    metadata_value = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=TEXT_DARK
    )

    story = []
    
    # ------------------ COVER PAGE ------------------
    story.append(Spacer(1, 100))
    story.append(Paragraph("Voice of Customer AI", title_style))
    story.append(Paragraph("AI Customer Feedback Analyzer & Strategic Intelligence Report", subtitle_style))
    
    # Divider line
    story.append(Table([[""]], colWidths=[504], rowHeights=[4], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SECONDARY_COLOR),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ])))
    story.append(Spacer(1, 40))
    
    # Metadata block
    meta_data = [
        [Paragraph("Report ID:", metadata_label), Paragraph(f"VOC-REP-{report_id:04d}", metadata_value)],
        [Paragraph("Source File:", metadata_label), Paragraph(filename, metadata_value)],
        [Paragraph("Generated At:", metadata_label), Paragraph(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), metadata_value)],
        [Paragraph("Total Feedback Analyzed:", metadata_label), Paragraph(f"{stats['total_feedback']:,} entries", metadata_value)],
    ]
    meta_table = Table(meta_data, colWidths=[150, 354])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    
    # Wrap in a light gray panel
    wrapper_table = Table([[meta_table]], colWidths=[504])
    wrapper_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 15),
    ]))
    
    story.append(wrapper_table)
    story.append(PageBreak())
    
    # ------------------ SECTION 1: EXECUTIVE SUMMARY ------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph("<b>Overall Sentiment Summary</b>", h2_style))
    story.append(Paragraph(summary_data.get('overall_sentiment_summary', ''), body_style))
    
    story.append(Paragraph("<b>Top Key Findings</b>", h2_style))
    for finding in summary_data.get('key_findings', []):
        story.append(Paragraph(f"• {finding}", bullet_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Top Complaints & Pain Points Summary</b>", h2_style))
    story.append(Paragraph(summary_data.get('top_complaints_summary', ''), body_style))
    
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 2: SENTIMENT ANALYSIS ------------------
    story.append(Paragraph("2. Sentiment Analysis", h1_style))
    story.append(Paragraph(
        "A breakdown of user sentiment classifications within the uploaded feedback dataset. Sentiment ranges from Positive to Negative, indicating overall customer brand perception.", 
        body_style
    ))
    
    # Sentiment distribution table
    sent_dist = stats['sentiment_distribution']
    total = sum(sent_dist.values()) or 1
    
    table_data = [[
        Paragraph("<b>Sentiment</b>", metadata_label), 
        Paragraph("<b>Count</b>", metadata_label), 
        Paragraph("<b>Percentage</b>", metadata_label)
    ]]
    for sent, count in sent_dist.items():
        pct = (count / total) * 100
        table_data.append([
            Paragraph(sent, metadata_value),
            Paragraph(f"{count:,}", metadata_value),
            Paragraph(f"{pct:.1f}%", metadata_value)
        ])
        
    sent_table = Table(table_data, colWidths=[168, 168, 168])
    sent_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(sent_table)
    story.append(Spacer(1, 20))

    # ------------------ SECTION 3: TOP PAIN POINTS & TOPICS ------------------
    story.append(Paragraph("3. Customer Pain Points & Topic Distribution", h1_style))
    story.append(Paragraph(
        "AI categorizes customer feedback into thematic groups and aggregates the frequency of specific underlying pain points.",
        body_style
    ))
    
    # Category Distribution table
    cat_dist = stats['category_distribution']
    cat_data = [[
        Paragraph("<b>Thematic Topic Category</b>", metadata_label),
        Paragraph("<b>Count</b>", metadata_label),
        Paragraph("<b>Percentage</b>", metadata_label)
    ]]
    for cat, count in cat_dist.items():
        pct = (count / total) * 100
        cat_data.append([
            Paragraph(cat, metadata_value),
            Paragraph(f"{count:,}", metadata_value),
            Paragraph(f"{pct:.1f}%", metadata_value)
        ])
    cat_table = Table(cat_data, colWidths=[204, 150, 150])
    cat_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), BG_LIGHT),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 8),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(cat_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Top 5 Specific Complaints / Pain Points</b>", h2_style))
    pain_points = stats['top_pain_points']
    for idx, (pain, count) in enumerate(pain_points[:5], 1):
        story.append(Paragraph(f"<b>{idx}. {pain}</b> (Mentioned {count} times)", bullet_style))
        
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 4: FEATURE REQUESTS & OPPORTUNITIES ------------------
    story.append(KeepTogether([
        Paragraph("4. Feature Requests & Opportunity Discovery", h1_style),
        Paragraph(
            "Customer feature requests are extracted, ranked, and scored against business viability metrics. "
            "The Opportunity Score reflects value gaps where users express significant dissatisfaction or unmet needs.",
            body_style
        )
    ]))
    
    # Top Feature Requests
    story.append(Paragraph("<b>Highly Requested Product Features</b>", h2_style))
    feat_requests = stats['top_feature_requests']
    for idx, (feat, count) in enumerate(feat_requests[:5], 1):
        story.append(Paragraph(f"<b>{idx}. {feat}</b> (Requested {count} times)", bullet_style))
        
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>Growth & Opportunity Highlights</b>", h2_style))
    for opt in summary_data.get('growth_opportunities', []):
        story.append(Paragraph(f"• {opt}", bullet_style))
        
    story.append(PageBreak())
    
    # ------------------ SECTION 5: CUSTOMER PERSONAS ------------------
    story.append(Paragraph("5. Customer Persona Insights", h1_style))
    story.append(Paragraph(
        "Personas generated dynamically by analyzing recurring complaint profiles, motivations, and usage blockers.",
        body_style
    ))
    
    for persona in summary_data.get('personas', []):
        p_name = persona.get('name', '')
        p_desc = persona.get('description', '')
        p_pains = persona.get('pain_points', [])
        p_needs = persona.get('needs', [])
        
        # Render a structured persona card
        pains_html = "".join([f"<li>{p}</li>" for p in p_pains])
        needs_html = "".join([f"<li>{n}</li>" for n in p_needs])
        
        card_content = [
            [Paragraph(f"<b>Persona: {p_name}</b>", h2_style)],
            [Paragraph(f"<i>{p_desc}</i>", body_style)],
            [Paragraph("<b>Key Pain Points:</b>", metadata_label)],
            [Paragraph(f"<ul>{pains_html}</ul>", body_style)],
            [Paragraph("<b>Core Customer Needs:</b>", metadata_label)],
            [Paragraph(f"<ul>{needs_html}</ul>", body_style)]
        ]
        
        card_table = Table(card_content, colWidths=[484])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('PADDING', (0,0), (-1,-1), 12),
            ('LINELEFT', (0,0), (0,-1), 3, SECONDARY_COLOR),  # Indigo accent border on the left
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        
        story.append(card_table)
        story.append(Spacer(1, 15))
        
    story.append(Spacer(1, 15))
    
    # ------------------ SECTION 6: STRATEGIC RECOMMENDATIONS ------------------
    story.append(KeepTogether([
        Paragraph("6. Strategic Recommendations & Action Plan", h1_style),
        Paragraph(
            "Concrete, actionable steps recommended to address key customer complaints and seize market opportunities.",
            body_style
        )
    ]))
    
    for idx, rec in enumerate(summary_data.get('product_recommendations', []), 1):
        story.append(Paragraph(f"<b>Action {idx}: {rec}</b>", bullet_style))
        
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
