"""
Schema.org detection module
Detects JSON-LD and Microdata structured data
"""
from bs4 import BeautifulSoup
import json
from typing import Dict, Any, List


def detect_schema(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Detect Schema.org structured data in JSON-LD and Microdata formats.
    """
    result = {
        "has_schema": False,
        "json_ld": [],
        "microdata": [],
        "types": []
    }
    
    # Detect JSON-LD
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    for script in json_ld_scripts:
        try:
            content = script.string
            if content:
                data = json.loads(content)
                
                # Handle both single objects and arrays
                if isinstance(data, list):
                    for item in data:
                        schema_type = item.get('@type', 'Unknown')
                        result['json_ld'].append({
                            'type': schema_type,
                            'data': item
                        })
                        if schema_type not in result['types']:
                            result['types'].append(schema_type)
                else:
                    schema_type = data.get('@type', 'Unknown')
                    result['json_ld'].append({
                        'type': schema_type,
                        'data': data
                    })
                    if schema_type not in result['types']:
                        result['types'].append(schema_type)
                        
        except json.JSONDecodeError:
            continue
    
    # Detect Microdata
    microdata_elements = soup.find_all(itemscope=True)
    
    for element in microdata_elements:
        item_type = element.get('itemtype', '')
        if item_type:
            # Extract type name from URL
            type_name = item_type.split('/')[-1] if '/' in item_type else item_type
            result['microdata'].append({
                'type': type_name,
                'itemtype': item_type
            })
            if type_name not in result['types']:
                result['types'].append(type_name)
    
    # Set has_schema flag
    result['has_schema'] = len(result['json_ld']) > 0 or len(result['microdata']) > 0
    result['total_schemas'] = len(result['json_ld']) + len(result['microdata'])
    
    return result
