import time
import json
from typing import Dict, Tuple
import gspread
from google.oauth2.service_account import Credentials
from app.config.settings import settings
from app.config.logger import get_logger
from pathlib import Path

logger = get_logger("Google Sheets Prompts")

BASE_DIR = Path(__file__).resolve().parent
SA_FILE = BASE_DIR.parent / "credentials" / "service_account.json"

SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# Simple in-process cache to avoid hitting Sheets API for every request
_CACHE: Dict[str, Tuple[float, Dict[str, str]]] = {}
_CACHE_TTL = 60  # seconds

def _sheets_service():
    """
    Create a Google Sheets client using the service account JSON.
    """
    try:
        with open(SA_FILE, "r", encoding="utf-8") as f:
            sa_info = json.load(f)

        creds = Credentials.from_service_account_info(sa_info, scopes=SHEETS_SCOPES)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        logger.error(f"Failed to create Google Sheets service: {e}")
        raise RuntimeError("Failed to create Google Sheets service") from e

def _sheet_prompts(spreadsheet_id: str, sheet_name: str = "Psychologist_AI_Prompt") -> Dict[str, str]:
    """
    Reads prompts from the given Google Sheet.
    Expects two columns: 'Key' and 'Value'.
    Returns a dict {Key: Value}.
    """
    client = _sheets_service()
    sheet = client.open_by_key(spreadsheet_id)
    # print("Spreadsheet title:", sheet.title)
    title = [ws.title for ws in sheet.worksheets()]
    # print("Worksheet tabs:", [ws.title for ws in sheet.worksheets()])
    worksheet = sheet.worksheet(title[0]) 
    # headers = sheet.row_values(1)
    # print("Headers:", headers)  # debug
    records = worksheet.get_all_records()
    # print("Records:", records)  # debug
    # records = sheet.get_all_records()  # List[Dict[str, Any]]
    
    # prompts: Dict[str, str] = {}
    # for row in records:
    #     key = row.get("Key")
    #     value = row.get("Value")
    #     if key and value:
    #         prompts[key.strip().upper()] = value.strip()
    # return prompts
    return records[0]

def load_prompts(force_refresh: bool = False) -> Dict[str, str]:
    """
    Returns a dict with keys like "SYSTEM PROMPT", "USER PROMPT".
    Cached for _CACHE_TTL seconds.
    """
    try:
        assert settings.PROMPT_SHEET_ID, "PROMPT_SHEET_ID env var is required"
        now = time.time()
        cache_key = f"prompts:{settings.PROMPT_SHEET_ID}"
        if not force_refresh and cache_key in _CACHE:
            ts, data = _CACHE[cache_key]
            if now - ts < _CACHE_TTL:
                return data
        
        # Read prompts from Google Sheets
        sections = _sheet_prompts(settings.PROMPT_SHEET_ID, sheet_name="Psychologist_AI_Prompt")
        # logger.info(f"Loaded prompts from Google Sheet: {sections}")
        _CACHE[cache_key] = (now, sections)
        return sections

    except Exception as e:
        logger.error(f"Error loading prompts: {e}")
        raise RuntimeError(f"Failed to load prompts from Google Sheet: {e}") from e
