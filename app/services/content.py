"""
Content extraction module
Extracts visible text from HTML without JavaScript
"""
from bs4 import BeautifulSoup, Tag
import re
from typing import Dict, Any


# SPA framework markers (empty divs that indicate client-side rendering)
SPA_MARKERS = [
    ("div", {"id": "root"}),       # React
    ("div", {"id": "app"}),        # Vue
    ("div", {"id": "__next"}),     # Next.js CSR
    ("div", {"id": "__nuxt"}),     # Nuxt CSR
    ("app-root", {}),              # Angular
    ("div", {"id": "gatsby-focus-wrapper"}),  # Gatsby
]

# Tags to exclude from text extraction
EXCLUDE_TAGS = [
    'script', 'style', 'noscript', 'iframe', 'svg', 
    'canvas', 'video', 'audio', 'head', 'meta', 'link'
]


def extract_content(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extract visible text content from HTML.
    Detects if it's an empty SPA shell.
    """
    # Check for SPA markers
    is_spa_empty = check_spa_empty(soup)
    
    # Remove unwanted tags
    for tag in soup(EXCLUDE_TAGS):
        tag.decompose()
    
    # Extract text
    text = soup.get_text(separator=' ', strip=True)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Count words
    word_count = count_words(text)
    
    return {
        "text": text,
        "word_count": word_count,
        "is_spa_empty": is_spa_empty,
        "has_content": word_count > 50  # Minimum threshold
    }


def check_spa_empty(soup: BeautifulSoup) -> bool:
    """
    Check if the page is an empty SPA shell (content loaded via JS).
    """
    for tag_name, attrs in SPA_MARKERS:
        elements = soup.find_all(tag_name, attrs)
        for elem in elements:
            if isinstance(elem, Tag):
                # Get text content of the container
                inner_text = elem.get_text(strip=True)
                # If the container has very little text, it's likely empty SPA
                if len(inner_text) < 100:
                    # Check if there are meaningful children
                    children = [c for c in elem.children if isinstance(c, Tag)]
                    if len(children) <= 3:
                        return True
    return False


def count_words(text: str) -> int:
    """Count words in text"""
    if not text:
        return 0
    words = text.split()
    return len(words)
