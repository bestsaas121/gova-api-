"""
HTML structure analysis module
Analyzes semantic HTML elements, meta tags, headings, etc.
"""
from bs4 import BeautifulSoup
from typing import Dict, Any, List


def analyze_structure(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Analyze HTML structure for SEO and AI visibility.
    """
    result = {}
    
    # Title tag
    title_tag = soup.find('title')
    result['has_title'] = title_tag is not None and bool(title_tag.string)
    result['title'] = title_tag.string.strip() if title_tag and title_tag.string else ""
    result['title_length'] = len(result['title'])
    
    # Meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    desc_content = meta_desc.get('content', '') if meta_desc else ''
    result['has_description'] = bool(desc_content)
    result['description'] = desc_content
    result['description_length'] = len(desc_content)
    
    # Headings
    h1_tags = soup.find_all('h1')
    result['h1_count'] = len(h1_tags)
    result['h1_texts'] = [h.get_text(strip=True) for h in h1_tags[:5]]  # First 5
    
    h2_tags = soup.find_all('h2')
    result['h2_count'] = len(h2_tags)
    
    h3_tags = soup.find_all('h3')
    result['h3_count'] = len(h3_tags)
    
    # Semantic elements
    result['has_main'] = soup.find('main') is not None
    result['has_article'] = soup.find('article') is not None
    result['has_section'] = soup.find('section') is not None
    result['has_nav'] = soup.find('nav') is not None
    result['has_header'] = soup.find('header') is not None
    result['has_footer'] = soup.find('footer') is not None
    
    # Count semantic elements
    semantic_count = sum([
        result['has_main'],
        result['has_article'],
        result['has_section'],
        result['has_nav'],
        result['has_header'],
        result['has_footer']
    ])
    result['semantic_count'] = semantic_count
    
    # Images analysis
    images = soup.find_all('img')
    result['total_images'] = len(images)
    
    images_with_alt = [img for img in images if img.get('alt')]
    result['images_with_alt'] = len(images_with_alt)
    
    if len(images) > 0:
        result['images_alt_percentage'] = round((len(images_with_alt) / len(images)) * 100)
    else:
        result['images_alt_percentage'] = 100  # No images = no problem
    
    # Links
    links = soup.find_all('a', href=True)
    result['total_links'] = len(links)
    
    # Check for noai/noimageai meta
    robots_meta = soup.find('meta', attrs={'name': 'robots'})
    robots_content = robots_meta.get('content', '').lower() if robots_meta else ''
    result['has_noai'] = 'noai' in robots_content
    result['has_noimageai'] = 'noimageai' in robots_content
    
    return result
