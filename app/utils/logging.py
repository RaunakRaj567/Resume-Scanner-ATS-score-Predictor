import logging
import re
import sys

def mask_pii(message: str) -> str:
    """Mask emails and phone numbers in log messages for privacy compliance."""
    if not isinstance(message, str):
        return str(message)
    # Mask emails
    masked = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL_MASKED]', message)
    # Mask phones
    masked = re.sub(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', '[PHONE_MASKED]', masked)
    return masked

class SafeLogger(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return mask_pii(str(msg)), kwargs

def get_logger(name: str) -> SafeLogger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return SafeLogger(logger, {})
