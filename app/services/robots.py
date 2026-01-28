"""
robots.txt analysis module
Checks if AI crawlers are allowed or blocked
"""
import httpx
from typing import Dict, List, Any
import re


async def analyze_robots(robots_url: str, ai_crawlers: List[str]) -> Dict[str, Any]:
    """
    Fetch and analyze robots.txt for AI crawler permissions.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(robots_url)
            
            if response.status_code == 404:
                # No robots.txt = all allowed
                return {
                    "exists": False,
                    "allows_all": True,
                    "crawlers": {crawler: "allowed" for crawler in ai_crawlers}
                }
            
            if response.status_code != 200:
                return {
                    "exists": False,
                    "allows_all": True,
                    "error": f"Could not fetch robots.txt (status {response.status_code})",
                    "crawlers": {crawler: "unknown" for crawler in ai_crawlers}
                }
            
            robots_content = response.text
            return parse_robots(robots_content, ai_crawlers)
            
    except Exception as e:
        return {
            "exists": False,
            "allows_all": True,
            "error": str(e),
            "crawlers": {crawler: "unknown" for crawler in ai_crawlers}
        }


def parse_robots(content: str, ai_crawlers: List[str]) -> Dict[str, Any]:
    """
    Parse robots.txt content and check each AI crawler.
    """
    lines = content.lower().split('\n')
    
    # Build rules per user-agent
    current_agents = []
    rules = {}  # {user-agent: [rules]}
    
    for line in lines:
        line = line.strip()
        
        # Skip comments and empty lines
        if not line or line.startswith('#'):
            continue
        
        if line.startswith('user-agent:'):
            agent = line.split(':', 1)[1].strip()
            current_agents = [agent]
            if agent not in rules:
                rules[agent] = []
        elif line.startswith('disallow:') and current_agents:
            path = line.split(':', 1)[1].strip()
            for agent in current_agents:
                if agent not in rules:
                    rules[agent] = []
                rules[agent].append(('disallow', path))
        elif line.startswith('allow:') and current_agents:
            path = line.split(':', 1)[1].strip()
            for agent in current_agents:
                if agent not in rules:
                    rules[agent] = []
                rules[agent].append(('allow', path))
    
    # Check each AI crawler
    crawlers_status = {}
    blocked_count = 0
    
    for crawler in ai_crawlers:
        crawler_lower = crawler.lower()
        
        # Check specific rules for this crawler
        if crawler_lower in rules:
            # Check if disallowed
            for rule_type, path in rules[crawler_lower]:
                if rule_type == 'disallow' and path in ['/', '']:
                    crawlers_status[crawler] = "blocked"
                    blocked_count += 1
                    break
            else:
                crawlers_status[crawler] = "allowed"
        # Check wildcard rules
        elif '*' in rules:
            for rule_type, path in rules['*']:
                if rule_type == 'disallow' and path in ['/', '']:
                    crawlers_status[crawler] = "blocked"
                    blocked_count += 1
                    break
            else:
                crawlers_status[crawler] = "allowed"
        else:
            crawlers_status[crawler] = "allowed"
    
    # Check if specific crawler names are blocked
    for crawler in ai_crawlers:
        if crawler not in crawlers_status:
            crawlers_status[crawler] = "allowed"
    
    return {
        "exists": True,
        "allows_all": blocked_count == 0,
        "blocked_count": blocked_count,
        "crawlers": crawlers_status
    }
