# backend/utils/supabase_client.py
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        _client = create_client(url, key)
    return _client


def save_report(report_data: dict) -> dict:
    """Insert a detection report into Supabase"""
    sb = get_supabase()
    result = sb.table("detection_reports").insert(report_data).execute()
    return result.data[0] if result.data else {}


def get_reports(site_name: str = None, limit: int = 50) -> list:
    """Fetch recent detection reports"""
    sb = get_supabase()
    query = sb.table("detection_reports").select("*").order("created_at", desc=True).limit(limit)
    if site_name:
        query = query.eq("site_name", site_name)
    result = query.execute()
    return result.data or []


def update_report_status(report_id: int, status: str) -> dict:
    """Update status of a report"""
    sb = get_supabase()
    result = (
        sb.table("detection_reports")
        .update({"status": status})
        .eq("id", report_id)
        .execute()
    )
    return result.data[0] if result.data else {}
