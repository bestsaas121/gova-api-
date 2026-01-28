"""
Database module for storing leads
Uses Supabase for storage
"""
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Try to import supabase, but don't fail if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_supabase_client() -> Optional[Any]:
    """Get Supabase client if configured."""
    if not SUPABASE_AVAILABLE:
        return None
    
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_KEY", "").strip()
    
    if not url or not key:
        print("Supabase credentials not found in environment")
        return None
    
    try:
        print(f"Initializing Supabase with URL: {url[:20]}...")
        return create_client(url, key)
    except Exception as e:
        print(f"Error initializing Supabase client: {str(e)}")
        return None


async def save_lead(
    url: str,
    email: str,
    name: Optional[str],
    score: int,
    analysis_data: Dict[str, Any]
) -> str:
    """
    Save lead and analysis data to Supabase.
    Returns the lead ID.
    """
    lead_id = str(uuid.uuid4())
    
    client = get_supabase_client()
    
    if client:
        try:
            data = {
                "id": lead_id,
                "url": url,
                "email": email,
                "name": name,
                "score": score,
                "status": analysis_data.get("status"),
                "analysis_data": analysis_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            client.table("visibility_leads").insert(data).execute()
            
        except Exception as e:
            print(f"Error saving to Supabase: {e}")
            # Don't fail the request if DB save fails
    else:
        # Log locally if Supabase not configured
        print(f"Lead captured: {email} - {url} - Score: {score}")
    
    return lead_id


async def get_lead(lead_id: str) -> Optional[Dict[str, Any]]:
    """Get lead by ID."""
    client = get_supabase_client()
    
    if not client:
        return None
    
    try:
        response = client.table("visibility_leads").select("*").eq("id", lead_id).single().execute()
        return response.data
    except Exception as e:
        print(f"Error fetching lead: {e}")
        return None
