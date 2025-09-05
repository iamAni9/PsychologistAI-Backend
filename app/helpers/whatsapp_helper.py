from app.config.logger import get_logger
from app.config.whatsapp import whatsapp_channel

logger = get_logger("WhatsApp Helper Logger")

def send_whatsapp_message(recipient_no: str, message_text: str, logger):
    try:
        logger.info(f"Sending message to {recipient_no}: '{message_text}'")
        resp = whatsapp_channel.send_text_message(
            recipient_no=recipient_no,
            message_text=message_text
        )
        if resp:
            logger.info(f"Meta API response for message to {recipient_no}: {resp}")
        else:
            logger.warning(f"Failed to get a response from Meta API for message to {recipient_no}")

    except Exception as e:
        logger.error(f"Error sending message to {recipient_no}: {e}")


async def send_upload_status_to_whatsapp(userid, logger, receiver_no, msg):
    try:
        send_whatsapp_message(receiver_no, msg, logger)
        logger.info(f"Upload status sent successfully to WhatsApp user {userid}")
    except Exception as e:
        logger.error(f"Failed to send upload status to user {userid}: {e}")
        raise
    
async def mark_user_message_as_read(message_id: str, logger):
    try: 
        resp = whatsapp_channel.mark_message_as_read(message_id)
        if resp:
            logger.info(f"Successfully marked as read: {resp}")
        else:
            logger.warning(f"Failed to get a response from Meta API while performing mark as read.")
    except Exception as e:
        logger.error(f"Unable to mark message as read, {e}")

async def send_typing_indicator(message_id: str, logger):
    try: 
        resp = whatsapp_channel.send_typing_indicator(message_id)
        if resp:
            logger.info(f"Typing indicator is showing: {resp}")
        else:
            logger.warning(f"Failed to get a response from Meta API while sending typing indicator.")
    except Exception as e:
        logger.error(f"Unable to send the typing indicator, {e}")