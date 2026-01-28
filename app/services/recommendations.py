"""
Recommendations generator module
Creates prioritized recommendations based on analysis results
"""
from typing import Dict, Any, List


def generate_recommendations(
    content_data: Dict[str, Any],
    structure_data: Dict[str, Any],
    robots_data: Dict[str, Any],
    schema_data: Dict[str, Any],
    scores: Dict[str, Any],
    is_ai_blocked: bool = False
) -> List[Dict[str, Any]]:
    """
    Generate prioritized recommendations based on analysis results.
    """
    recommendations = []
    breakdown = scores.get("breakdown", {})
    
    # 0. AI Bot Blocking (WAF/Cloudflare) - CRITICAL
    if is_ai_blocked:
        recommendations.append({
            "priority": "critical",
            "title": "Tu servidor bloquea activamente a las IAs",
            "description": "Hemos detectado que tu WAF (como Cloudflare) bloquea el User-Agent de GPTBot. Esto hace que seas invisible para ChatGPT.",
            "impact": "Acceso totalmente denegado para la mayoría de modelos de IA."
        })
    
    # 1. Check SPA/Empty content - CRITICAL
    if content_data.get("is_spa_empty", False):
        recommendations.append({
            "priority": "critical",
            "title": "Tu web usa Client-Side Rendering (SPA vacía)",
            "description": "Los crawlers de IA no pueden ejecutar JavaScript. Tu contenido no es visible para ChatGPT, Gemini ni Claude. Considera usar Server-Side Rendering (SSR) o Static Site Generation (SSG).",
            "impact": "Las IAs no ven prácticamente nada de tu contenido."
        })
    
    # 2. Check robots.txt blocking - HIGH
    if not robots_data.get("allows_all", True):
        blocked = [k for k, v in robots_data.get("crawlers", {}).items() if v == "blocked"]
        if blocked:
            recommendations.append({
                "priority": "high",
                "title": "Tu robots.txt bloquea crawlers de IA",
                "description": f"Los siguientes crawlers están bloqueados: {', '.join(blocked)}. Esto impide que indexen tu contenido.",
                "impact": "Estas IAs no pueden acceder a tu web."
            })
    
    # 3. Check content amount - HIGH/MEDIUM
    word_count = content_data.get("word_count", 0)
    if word_count < 200:
        recommendations.append({
            "priority": "high",
            "title": "Contenido insuficiente detectado",
            "description": f"Solo se detectaron {word_count} palabras. Las IAs necesitan más contenido para entender tu negocio. Añade más texto descriptivo sobre tus servicios, productos o propuesta de valor.",
            "impact": "Contenido mínimo dificulta la comprensión de tu marca."
        })
    elif word_count < 500:
        recommendations.append({
            "priority": "medium",
            "title": "Contenido limitado",
            "description": f"Se detectaron {word_count} palabras. Considera añadir más contenido para mejorar la comprensión de tu negocio por parte de las IAs.",
            "impact": "Más contenido mejora el entendimiento de tu marca."
        })
    
    # 4. Check meta description - MEDIUM
    if breakdown.get("description", {}).get("status") != "excellent":
        desc_length = structure_data.get("description_length", 0)
        if desc_length == 0:
            recommendations.append({
                "priority": "medium",
                "title": "Falta meta description",
                "description": "Añade una meta description de 120-160 caracteres que resuma claramente tu propuesta de valor.",
                "impact": "Las IAs usan la descripción para entender tu web."
            })
        else:
            recommendations.append({
                "priority": "low",
                "title": "Meta description fuera del rango óptimo",
                "description": f"Tu meta description tiene {desc_length} caracteres. El rango ideal es 120-160 caracteres.",
                "impact": "Una descripción óptima mejora la comprensión."
            })
    
    # 5. Check H1 - MEDIUM
    h1_count = structure_data.get("h1_count", 0)
    if h1_count == 0:
        recommendations.append({
            "priority": "medium",
            "title": "Falta encabezado H1",
            "description": "Añade exactamente un H1 que describa claramente el contenido principal de la página.",
            "impact": "El H1 es clave para la comprensión del tema principal."
        })
    elif h1_count > 1:
        recommendations.append({
            "priority": "low",
            "title": "Múltiples H1 detectados",
            "description": f"Se encontraron {h1_count} H1. Usa solo uno por página y estructúralo con H2/H3.",
            "impact": "Múltiples H1 confunden la jerarquía de contenido."
        })
    
    # 6. Check Schema.org - LOW/MEDIUM
    if not schema_data.get("has_schema", False):
        recommendations.append({
            "priority": "medium",
            "title": "No se detectaron datos estructurados",
            "description": "Implementa Schema.org con JSON-LD para definir tu entidad (Organization, LocalBusiness, etc.). Esto ayuda a las IAs a entender qué eres y qué haces.",
            "impact": "Los datos estructurados mejoran la precisión de la IA."
        })
    
    # 7. Check image alt text - LOW
    alt_percentage = structure_data.get("images_alt_percentage", 100)
    if alt_percentage < 80 and structure_data.get("total_images", 0) > 0:
        missing = structure_data.get("total_images", 0) - structure_data.get("images_with_alt", 0)
        recommendations.append({
            "priority": "low",
            "title": "Imágenes sin texto alternativo",
            "description": f"{missing} imágenes no tienen atributo alt. Las IAs no pueden interpretar imágenes sin descripción textual.",
            "impact": "El contenido visual no es accesible para las IAs."
        })
    
    # 8. Check semantic structure - LOW
    if structure_data.get("semantic_count", 0) < 3:
        recommendations.append({
            "priority": "low",
            "title": "Estructura semántica limitada",
            "description": "Usa más elementos semánticos HTML5 como <article>, <section>, <main>, <header> y <footer> para estructurar mejor tu contenido.",
            "impact": "La estructura semántica mejora la comprensión del layout."
        })
    
    # 9. Check noai meta - INFO
    if structure_data.get("has_noai", False):
        recommendations.append({
            "priority": "info",
            "title": "Meta tag 'noai' detectado",
            "description": "Tu web tiene la etiqueta <meta name='robots' content='noai'>. Esto indica que no quieres ser indexado por IAs. Si no es intencional, elimínalo.",
            "impact": "Las IAs que respetan esta etiqueta no te indexarán."
        })
    
    # Sort by priority
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 5))
    
    return recommendations
