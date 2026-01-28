"""
Scoring system module
Calculates visibility score based on analysis results
"""
from typing import Dict, Any


# Score configuration
SCORE_CONFIG = {
    "content": {
        "max": 25,
        "thresholds": {
            "excellent": 500,  # >500 words
            "good": 200,       # 200-500 words
            "poor": 50         # <200 words
        }
    },
    "title": {
        "max": 10,
        "min_length": 10
    },
    "description": {
        "max": 10,
        "ideal_min": 120,
        "ideal_max": 160
    },
    "h1": {
        "max": 10
    },
    "structure": {
        "max": 10
    },
    "no_spa": {
        "max": 15
    },
    "robots": {
        "max": 10
    },
    "alt_text": {
        "max": 5,
        "threshold": 80  # 80% of images need alt
    },
    "schema": {
        "max": 5
    }
}


def calculate_score(
    content_data: Dict[str, Any],
    structure_data: Dict[str, Any],
    robots_data: Dict[str, Any],
    schema_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Calculate the overall visibility score.
    Returns breakdown by category and total.
    """
    breakdown = {}
    
    # 1. Content score (max 25)
    word_count = content_data.get("word_count", 0)
    if word_count >= 500:
        content_score = 25
        content_status = "excellent"
    elif word_count >= 200:
        content_score = 15
        content_status = "good"
    elif word_count >= 50:
        content_score = 8
        content_status = "warning"
    else:
        content_score = 2
        content_status = "critical"
    
    breakdown["content"] = {
        "score": content_score,
        "max": 25,
        "status": content_status,
        "detail": f"{word_count} palabras detectadas"
    }
    
    # 2. Title score (max 10)
    if structure_data.get("has_title") and structure_data.get("title_length", 0) >= 10:
        title_score = 10
        title_status = "excellent"
    elif structure_data.get("has_title"):
        title_score = 5
        title_status = "warning"
    else:
        title_score = 0
        title_status = "critical"
    
    breakdown["title"] = {
        "score": title_score,
        "max": 10,
        "status": title_status,
        "detail": structure_data.get("title", "No detectado")[:60]
    }
    
    # 3. Meta description score (max 10)
    desc_length = structure_data.get("description_length", 0)
    if 120 <= desc_length <= 160:
        desc_score = 10
        desc_status = "excellent"
    elif structure_data.get("has_description"):
        desc_score = 5
        desc_status = "warning"
    else:
        desc_score = 0
        desc_status = "critical"
    
    breakdown["description"] = {
        "score": desc_score,
        "max": 10,
        "status": desc_status,
        "detail": f"{desc_length} caracteres" if desc_length > 0 else "No detectado"
    }
    
    # 4. H1 score (max 10)
    h1_count = structure_data.get("h1_count", 0)
    if h1_count == 1:
        h1_score = 10
        h1_status = "excellent"
    elif h1_count > 1:
        h1_score = 5
        h1_status = "warning"
    else:
        h1_score = 0
        h1_status = "critical"
    
    breakdown["h1"] = {
        "score": h1_score,
        "max": 10,
        "status": h1_status,
        "detail": f"{h1_count} H1 detectado(s)"
    }
    
    # 5. Semantic structure score (max 10)
    semantic_count = structure_data.get("semantic_count", 0)
    if semantic_count >= 4:
        struct_score = 10
        struct_status = "excellent"
    elif semantic_count >= 2:
        struct_score = 6
        struct_status = "good"
    elif semantic_count >= 1:
        struct_score = 3
        struct_status = "warning"
    else:
        struct_score = 0
        struct_status = "critical"
    
    breakdown["structure"] = {
        "score": struct_score,
        "max": 10,
        "status": struct_status,
        "detail": f"{semantic_count} elementos semánticos"
    }
    
    # 6. Not empty SPA score (max 15)
    if not content_data.get("is_spa_empty", False) and content_data.get("has_content", False):
        spa_score = 15
        spa_status = "excellent"
    elif content_data.get("is_spa_empty", False):
        spa_score = 0
        spa_status = "critical"
    else:
        spa_score = 8
        spa_status = "warning"
    
    breakdown["no_spa"] = {
        "score": spa_score,
        "max": 15,
        "status": spa_status,
        "detail": "SPA vacía detectada" if content_data.get("is_spa_empty") else "Contenido visible sin JS"
    }
    
    # 7. robots.txt score (max 10)
    if robots_data.get("allows_all", False):
        robots_score = 10
        robots_status = "excellent"
    else:
        blocked_count = robots_data.get("blocked_count", 0)
        if blocked_count > 4:
            robots_score = 0
            robots_status = "critical"
        elif blocked_count > 0:
            robots_score = 5
            robots_status = "warning"
        else:
            robots_score = 10
            robots_status = "excellent"
    
    breakdown["robots"] = {
        "score": robots_score,
        "max": 10,
        "status": robots_status,
        "detail": f"{robots_data.get('blocked_count', 0)} crawlers bloqueados"
    }
    
    # 8. Image alt text score (max 5)
    alt_percentage = structure_data.get("images_alt_percentage", 100)
    if alt_percentage >= 80:
        alt_score = 5
        alt_status = "excellent"
    elif alt_percentage >= 50:
        alt_score = 3
        alt_status = "warning"
    else:
        alt_score = 0
        alt_status = "critical"
    
    breakdown["alt_text"] = {
        "score": alt_score,
        "max": 5,
        "status": alt_status,
        "detail": f"{alt_percentage}% de imágenes con alt"
    }
    
    # 9. Schema.org score (max 5)
    if schema_data.get("has_schema", False):
        schema_score = 5
        schema_status = "excellent"
    else:
        schema_score = 0
        schema_status = "warning"
    
    breakdown["schema"] = {
        "score": schema_score,
        "max": 5,
        "status": schema_status,
        "detail": ", ".join(schema_data.get("types", []))[:50] if schema_data.get("types") else "No detectado"
    }
    
    # Calculate total
    total = sum(item["score"] for item in breakdown.values())
    
    return {
        "total": total,
        "max": 100,
        "breakdown": breakdown
    }


def get_status(score: int) -> Dict[str, str]:
    """
    Get status label and emoji based on total score.
    """
    if score >= 85:
        return {"status": "excelente", "emoji": "✅", "color": "#22c55e"}
    elif score >= 70:
        return {"status": "bueno", "emoji": "🟢", "color": "#22c55e"}
    elif score >= 50:
        return {"status": "mejorable", "emoji": "🟡", "color": "#f59e0b"}
    elif score >= 30:
        return {"status": "deficiente", "emoji": "🟠", "color": "#f97316"}
    else:
        return {"status": "crítico", "emoji": "🔴", "color": "#ef4444"}
