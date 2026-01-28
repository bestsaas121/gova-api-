"""
PDF generator module
Generates professional PDF reports using WeasyPrint
"""
from weasyprint import HTML, CSS
from typing import Dict, Any, Optional
from datetime import datetime
import io


def generate_pdf(url: str, name: Optional[str], analysis: Dict[str, Any]) -> bytes:
    """
    Generate a PDF report from analysis results.
    Returns PDF as bytes.
    """
    html_content = render_pdf_html(url, name, analysis)
    
    # Generate PDF
    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    return pdf_file.read()


def render_pdf_html(url: str, name: Optional[str], analysis: Dict[str, Any]) -> str:
    """
    Render HTML template for PDF.
    """
    score = analysis.get("score", 0)
    status = analysis.get("status", "")
    emoji = analysis.get("emoji", "")
    breakdown = analysis.get("breakdown", {})
    recommendations = analysis.get("recommendations", [])
    crawlers = analysis.get("crawlers", {})
    preview_text = analysis.get("preview_text", "")
    
    today = datetime.now().strftime("%d de %B de %Y")
    prepared_for = name if name else "Usuario"
    
    # Build breakdown table rows
    breakdown_rows = ""
    for key, data in breakdown.items():
        status_emoji = "✅" if data["status"] == "excellent" else "🟡" if data["status"] in ["good", "warning"] else "❌"
        breakdown_rows += f"""
        <tr>
            <td>{get_category_name(key)}</td>
            <td class="center">{data['score']}/{data['max']}</td>
            <td class="center">{status_emoji} {get_status_spanish(data['status'])}</td>
        </tr>
        """
    
    # Build crawlers table rows
    crawler_rows = ""
    for crawler, status in crawlers.items():
        status_emoji = "✅ Permitido" if status == "allowed" else "❌ Bloqueado"
        crawler_rows += f"""
        <tr>
            <td>{crawler}</td>
            <td class="center">{status_emoji}</td>
        </tr>
        """
    
    # Build recommendations
    recs_html = ""
    for i, rec in enumerate(recommendations[:5], 1):
        priority_emoji = "🔴" if rec["priority"] in ["critical", "high"] else "🟡" if rec["priority"] == "medium" else "🟢"
        recs_html += f"""
        <div class="recommendation">
            <h4>{priority_emoji} {rec['title']}</h4>
            <p>{rec['description']}</p>
        </div>
        """
    
    # Score color
    if score >= 70:
        score_color = "#22c55e"
    elif score >= 50:
        score_color = "#f59e0b"
    else:
        score_color = "#ef4444"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 11pt;
                line-height: 1.5;
                color: #333;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 2px solid #6366f1;
            }}
            .logo {{
                max-width: 100px;
                margin-bottom: 10px;
            }}
            h1 {{
                color: #6366f1;
                font-size: 24pt;
                margin: 10px 0;
            }}
            h2 {{
                color: #1a1a1a;
                font-size: 14pt;
                margin-top: 30px;
                padding-bottom: 8px;
                border-bottom: 1px solid #e5e7eb;
            }}
            h3 {{
                font-size: 12pt;
                color: #374151;
            }}
            .meta {{
                color: #666;
                font-size: 10pt;
            }}
            .score-box {{
                text-align: center;
                padding: 30px;
                margin: 20px 0;
                background: #f8f9fa;
                border-radius: 12px;
            }}
            .score {{
                font-size: 60pt;
                font-weight: 700;
                color: {score_color};
            }}
            .score-max {{
                font-size: 20pt;
                color: #666;
            }}
            .status {{
                font-size: 16pt;
                margin-top: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th, td {{
                padding: 10px;
                border: 1px solid #e5e7eb;
                text-align: left;
            }}
            th {{
                background: #f8f9fa;
                font-weight: 600;
            }}
            .center {{
                text-align: center;
            }}
            .recommendation {{
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #6366f1;
            }}
            .recommendation h4 {{
                margin: 0 0 8px 0;
                font-size: 11pt;
            }}
            .recommendation p {{
                margin: 0;
                font-size: 10pt;
                color: #555;
            }}
            .preview {{
                background: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                font-size: 10pt;
                color: #555;
                font-style: italic;
            }}
            .cta-box {{
                margin-top: 40px;
                padding: 25px;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                border-radius: 12px;
                color: white;
                text-align: center;
            }}
            .cta-box h3 {{
                color: white;
                margin-top: 0;
            }}
            .cta-box a {{
                color: white;
                font-weight: 600;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                font-size: 9pt;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68f4b4cc4cb80c1c1c673731/5febdb421_LOGOGOVA.png" alt="GOVA" class="logo">
            <h1>INFORME DE VISIBILIDAD IA</h1>
            <p class="meta">
                <strong>URL Analizada:</strong> {url}<br>
                <strong>Fecha:</strong> {today}<br>
                <strong>Preparado para:</strong> {prepared_for}
            </p>
        </div>
        
        <h2>📊 PUNTUACIÓN GLOBAL</h2>
        <div class="score-box">
            <div class="score">{score}<span class="score-max">/100</span></div>
            <div class="status">{emoji} {status.upper()}</div>
        </div>
        
        <h2>📈 DESGLOSE POR CATEGORÍAS</h2>
        <table>
            <tr>
                <th>Categoría</th>
                <th class="center">Puntos</th>
                <th class="center">Estado</th>
            </tr>
            {breakdown_rows}
        </table>
        
        <h2>🤖 COMPATIBILIDAD CON CRAWLERS DE IA</h2>
        <table>
            <tr>
                <th>Crawler</th>
                <th class="center">Estado</th>
            </tr>
            {crawler_rows}
        </table>
        
        <h2>💡 RECOMENDACIONES PRIORITARIAS</h2>
        {recs_html if recs_html else '<p>No se detectaron problemas importantes. ¡Excelente trabajo!</p>'}
        
        <h2>👁️ VISTA PREVIA: LO QUE VEN LAS IAs</h2>
        <div class="preview">
            "{preview_text}"
        </div>
        
        <div class="cta-box">
            <h3>¿QUIERES MEJORAR TU VISIBILIDAD EN IA?</h3>
            <p>En GOVA somos especialistas en optimizar la presencia<br>
            de marcas en ChatGPT, Gemini, Claude y Perplexity.</p>
            <p style="margin-top: 15px;">
                📞 Solicita tu auditoría gratuita:<br>
                <a href="https://govarank.com/#formulario">https://govarank.com/#formulario</a>
            </p>
        </div>
        
        <div class="footer">
            <p><strong>GOVA</strong> - SEO para IA y Modelos de Lenguaje<br>
            Bentaberri Plaza, 3, 1º izquierda · 20008 Donostia / San Sebastián<br>
            📱 +34 843 754 301 · 🌐 govarank.com</p>
        </div>
    </body>
    </html>
    """
    
    return html


def get_category_name(key: str) -> str:
    """Map category keys to Spanish names."""
    names = {
        "content": "Contenido visible",
        "title": "Title tag",
        "description": "Meta description",
        "h1": "Encabezado H1",
        "structure": "Estructura semántica",
        "no_spa": "Renderizado sin JS",
        "robots": "robots.txt",
        "alt_text": "Imágenes con alt",
        "schema": "Datos estructurados"
    }
    return names.get(key, key)


def get_status_spanish(status: str) -> str:
    """Map status to Spanish."""
    statuses = {
        "excellent": "Excelente",
        "good": "Bueno",
        "warning": "Mejorable",
        "critical": "Crítico",
        "missing": "No detectado"
    }
    return statuses.get(status, status)
