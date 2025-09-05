from fastapi import Request, Response, status, BackgroundTasks, Query
from app.config.logger import get_logger
from app.helpers.whatsapp_helper import send_whatsapp_message, send_typing_indicator, mark_user_message_as_read
from app.config.settings import settings
from app.helpers.query_response_helper import get_query_response

logger = get_logger("Whatsapp Logger")

def update_msg_format(msg):
    msg = dict(msg)
    message_lines = []
    for key, value in msg.items():
        message_lines.append(f"*{key.replace('_', ' ').title()}*: {value}")
    
    return "\n".join(message_lines)

async def process_and_reply(payload: dict):
    try:
        changes = payload.get("entry", [{}])[0].get("changes", [{}])[0]
        value = changes.get("value", {})
        
        if "messages" in value:
            message = value["messages"][0]
            from_number = message["from"]
            metadata = value.get("metadata", {})
            to_number = metadata.get("display_phone_number")

            try: 
                message_type = message.get("type")
                message_id = message.get("id")
                
                await mark_user_message_as_read(message_id, logger)

                if message_type == "text":
                    await send_typing_indicator(message_id, logger)
                    body = message["text"]["body"]
                    logger.info(f"From: {from_number}, To: {to_number}, Body: {body}")
                    msg = await get_query_response(body)
                    final_msg = update_msg_format(msg)
                    send_whatsapp_message(from_number, final_msg, logger)
                else:
                    logger.warning(f"Received unsupported message type: {message_type}")
                    send_whatsapp_message(from_number, "This message type is not supported.", logger)
            except Exception as e:
                send_whatsapp_message(from_number, "Error occurred while processing your message.", logger)
                logger.error(f"Error occurred while sending reply: {e}")
    except Exception as e:
        logger.error(f"Error processing webhook payload: {e}", exc_info=True)
        raise

async def whatsapp_handler_meta(
    request: Request,
    background_tasks: BackgroundTasks,
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
) -> Response:
   
    if hub_mode == "subscribe" and hub_verify_token:
        if hub_verify_token == settings.META_VERIFY_TOKEN:
            logger.info("Webhook verified successfully!")
            return Response(content=hub_challenge, status_code=status.HTTP_200_OK)
        else:
            logger.warning("Webhook verification failed: Invalid verify token.")
            return Response(status_code=status.HTTP_403_FORBIDDEN)

    if request.method == "POST":
        try:
            payload = await request.json()
            logger.info(f"Received Meta payload: {payload}")
            
            background_tasks.add_task(process_and_reply, payload)
            
            return Response(status_code=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred in Meta handler: {e}")
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)