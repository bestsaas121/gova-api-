"""
Email sender module
Sends PDF reports using Resend API
"""
import os
import resend
from typing import Dict, Any, Optional
import base64

from ..pdf.generator import generate_pdf


async def send_report_email(
    email: str,
    name: Optional[str],
    url: str,
    analysis: Dict[str, Any]
) -> bool:
    """
    Generate PDF report and send via Resend.
    """
    resend.api_key = os.getenv("RESEND_API_KEY")
    
    if not resend.api_key:
        print("Warning: RESEND_API_KEY not set, skipping email")
        return False
    
    try:
        # Generate PDF
        pdf_bytes = generate_pdf(
            url=url,
            name=name,
            analysis=analysis
        )
        
        # Encode PDF for attachment
        pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Extract domain for filename
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "")
        filename = f"Informe-Visibilidad-IA-{domain}.pdf"
        
        # Prepare email content
        score = analysis.get("score", 0)
        status = analysis.get("status", "")
        emoji = analysis.get("emoji", "")
        
        greeting = f"Hola {name}" if name else "Hola"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Inter', -apple-system, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ max-width: 120px; }}
                .score-box {{ background: #f8f9fa; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0; }}
                .score {{ font-size: 48px; font-weight: 700; color: #6366f1; }}
                .status {{ font-size: 18px; margin-top: 8px; }}
                .cta {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 14px 28px; border-radius: 8px; text-decoration: none; display: inline-block; margin: 20px 0; font-weight: 600; }}
                .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 14px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <img src="https://qtrypzzcjebvfcihiynt.supabase.co/storage/v1/object/public/base44-prod/public/68f4b4cc4cb80c1c1c673731/5febdb421_LOGOGOVA.png" alt="GOVA" class="logo">
                </div>
                
                <p>{greeting},</p>
                
                <p>Aquí tienes el análisis de visibilidad IA de tu web <strong>{url}</strong>.</p>
                
                <div class="score-box">
                    <div class="score">{score}/100</div>
                    <div class="status">{emoji} {status.upper()}</div>
                </div>
                
                <p><strong>Resumen rápido:</strong></p>
                <ul>
                    <li>Contenido detectado: {analysis.get('summary', {}).get('word_count', 0)} palabras</li>
                    <li>Estructura HTML: {len([s for s in analysis.get('breakdown', {}).values() if s.get('status') == 'excellent'])} elementos excelentes</li>
                    <li>Schema.org: {"✅ Detectado" if analysis.get('summary', {}).get('has_schema') else "❌ No detectado"}</li>
                </ul>
                
                <p>Adjunto encontrarás el <strong>informe completo en PDF</strong> con:</p>
                <ul>
                    <li>✓ Desglose detallado por categorías</li>
                    <li>✓ Lista de problemas detectados</li>
                    <li>✓ Recomendaciones prioritarias</li>
                    <li>✓ Vista previa de lo que ven las IAs</li>
                </ul>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                
                <p><strong>¿Quieres que las IAs reconozcan y recomienden tu marca?</strong></p>
                
                <p>En GOVA te ayudamos a mejorar tu visibilidad en ChatGPT, Gemini, Claude y Perplexity.</p>
                
                <p style="text-align: center;">
                    <a href="https://govarank.com/#formulario" class="cta">Solicita tu Auditoría Gratuita</a>
                </p>
                
                <p>Te mostramos en persona qué sabe la IA sobre tu marca.</p>
                
                <div class="footer">
                    <p>Un saludo,<br>
                    <strong>Julen Oruesagasti</strong><br>
                    CEO & Fundador de GOVA</p>
                    
                    <p>📱 +34 843 754 301<br>
                    🌐 <a href="https://govarank.com">govarank.com</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email via Resend
        try:
            resend.Emails.send(params)
            return True
        except Exception as e:
            print(f"Resend error: {e}")
            return False
        
    except Exception as e:
        print(f"Error preparing or sending email: {e}")
        return False
