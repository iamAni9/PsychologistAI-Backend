import re
import json
import random
import asyncio
from pydantic import BaseModel
from app.ai.gemini import query_ai
from app.config.constants import MAX_RETRY_ATTEMPTS, INITIAL_RETRY_DELAY
from app.config.logger import get_logger
from app.config.google_docs_prompts import load_prompts

class QueryResponse(BaseModel): 
    intent: str
    risk_level: str
    suggested_action: str
    response_message: str

logger = get_logger("Helper Logger")

async def sleep_ms(ms: int):
    await asyncio.sleep(ms / 1000.0)

async def retry_operation(
    operation,
    operation_name: str,
    max_retries: int = MAX_RETRY_ATTEMPTS,
    initial_delay: int = INITIAL_RETRY_DELAY
):
    """Retry operation with exponential backoff"""
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            return await operation()
        except Exception as error:
            last_error = error
            delay = min(
                initial_delay * (2 ** (attempt - 1)) + random.randint(0, 1000),
                30000  # Max 30s delay
            )
            
            logger.warning(f"{operation_name} failed (attempt {attempt}/{max_retries}): {str(error)}")
            
            if attempt < max_retries:
                logger.info(f"Retrying {operation_name} in {delay}ms...")
                await sleep_ms(delay)
    
    raise Exception(f"{operation_name} failed after {max_retries} attempts. Last error: {str(last_error)}")

def clean_json_string(json_str: str) -> str:
    json_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', json_str)
    
    if json_match:
        json_str = json_match.group(1)
    
    
    json_str = (json_str
                .replace('\n', ' ')
                .replace('\r', ' ')
                .replace('  ', ' ')
                .strip())
    
    json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)', r'\1"\2"\3', json_str)
    
    return json_str

async def get_query_response(user_query: str, medium = None) -> QueryResponse: 
    try:
        sections = load_prompts()
        system_prompt = sections.get("SYSTEM PROMPT", "").strip()
        user_template = sections.get("USER PROMPT", "Classify: {user_query}").strip()
        user_prompt = user_template.replace("{user_query}", user_query)
        # logger.info(f"System Prompt: {system_prompt}")
        # logger.info(f"User Prompt: {user_prompt}")
    except Exception as e:
        logger.error(f"Error loading prompts: {e}")
        raise
    
    async def response_generation():
        query_response = await query_ai(user_prompt, system_prompt)
        json_str = clean_json_string(str(query_response))
        logger.info(f"Response: {query_response}")
        try:
            parsed = json.loads(json_str)
            logger.info(f"Parsed Response: {parsed}")
                        
            return QueryResponse(**parsed)
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f'Failed to parse classification response: {json_str}, {e}')
            return QueryResponse(
                message='Unable to generate a valid response. Please try again.',
            )
    
    return await retry_operation(response_generation, 'Query Response Generation')