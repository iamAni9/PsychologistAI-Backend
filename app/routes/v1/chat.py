from fastapi import APIRouter, Request, Response, BackgroundTasks, Query
from app.controllers import whatsapp_controller
from app.config.logger import get_logger

logger = get_logger("API Logger")
router = APIRouter()

@router.get("/")
async def hello_chat():
    logger.info("Chat route accessed")
    return {
        "status": "success",
        "message": "User can send chat."
        }

# @router.post("/query")
# async def query_analysis(request: Request, response: Response):
#     return await chat_controller.response_user_query(request, response)

@router.api_route("/whatsapp", methods=["GET", "POST"])
async def whatsapp_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """
    Endpoint to handle Meta WhatsApp webhooks.
    - GET: For webhook verification.
    - POST: For incoming message notifications.
    """
    return await whatsapp_controller.whatsapp_handler_meta(
        request,
        background_tasks,
        hub_mode,
        hub_challenge,
        hub_verify_token
    )