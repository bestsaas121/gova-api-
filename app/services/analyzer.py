"""
Main URL analyzer service
Orchestrates all analysis modules and calculates final score
"""
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from typing import Dict, Any, List
import asyncio

from .content import extract_content, count_words
from .structure import analyze_structure
from .robots import analyze_robots
from .schema_detector import detect_schema
from .scoring import calculate_score, get_status
from .recommendations import generate_recommendations


# AI Crawler user agents
AI_CRAWLERS = [
    "GPTBot",
    "ChatGPT-User",
    "ClaudeBot",
    "anthropic-ai",
    "Google-Extended",
    "CCBot",
    "PerplexityBot",
    "Bytespider"
]

# Request headers simulating GPTBot
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GPTBot/1.0; +https://openai.com/gptbot)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}


async def fetch_url(url: str, timeout: int = 30) -> tuple[str, int]:
    """Fetch URL content without JavaScript execution"""
    async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
        response = await client.get(url, headers=HEADERS)
        return response.text, response.status_code


async def analyze_url(url: str) -> Dict[str, Any]:
    """
    Main analysis function.
    Fetches the URL and analyzes its visibility for AI crawlers.
    """
    # Fetch HTML content
    html_content, status_code = await fetch_url(url)
    
    if status_code >= 400:
        return {
            "score": 0,
            "status": "error",
            "emoji": "❌",
            "error": f"No se pudo acceder a la URL (código {status_code})",
            "summary": {},
            "breakdown": {},
            "recommendations": [],
            "preview_text": "",
            "crawlers": {}
        }
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'lxml')
    
    # Extract text content
    content_data = extract_content(soup)
    
    # Analyze HTML structure
    structure_data = analyze_structure(soup)
    
    # Check robots.txt
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    crawlers_status = await analyze_robots(robots_url, AI_CRAWLERS)
    
    # Detect Schema.org
    schema_data = detect_schema(soup)
    
    # Calculate scores
    scores = calculate_score(
        content_data=content_data,
        structure_data=structure_data,
        robots_data=crawlers_status,
        schema_data=schema_data
    )
    
    # Get overall status
    total_score = scores["total"]
    status_info = get_status(total_score)
    
    # Generate recommendations
    recommendations = generate_recommendations(
        content_data=content_data,
        structure_data=structure_data,
        robots_data=crawlers_status,
        schema_data=schema_data,
        scores=scores
    )
    
    # Create preview text (first 500 chars of visible content)
    preview_text = content_data.get("text", "")[:500]
    if len(content_data.get("text", "")) > 500:
        preview_text += "..."
    
    # Build response
    return {
        "score": total_score,
        "status": status_info["status"],
        "emoji": status_info["emoji"],
        "summary": {
            "word_count": content_data.get("word_count", 0),
            "has_title": structure_data.get("has_title", False),
            "has_description": structure_data.get("has_description", False),
            "h1_count": structure_data.get("h1_count", 0),
            "is_spa_empty": content_data.get("is_spa_empty", False),
            "robots_allows_ai": crawlers_status.get("allows_all", False),
            "has_schema": schema_data.get("has_schema", False),
            "images_with_alt": structure_data.get("images_alt_percentage", 0)
        },
        "breakdown": scores["breakdown"],
        "recommendations": recommendations,
        "preview_text": preview_text,
        "crawlers": crawlers_status.get("crawlers", {})
    }
