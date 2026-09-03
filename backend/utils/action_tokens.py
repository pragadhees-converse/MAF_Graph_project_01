# backend/utils/action_tokens.py
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from core.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)

TOKEN_MAX_AGE_SECONDS = 24 * 60 * 60  # 24 hours — a recipient may not respond instantly


def _get_serializer() -> URLSafeTimedSerializer:
    settings = get_settings()
    return URLSafeTimedSerializer(settings.SESSION_SECRET_KEY, salt="teams-card-action")


def create_action_token(payload: dict) -> str:
    serializer = _get_serializer()
    return serializer.dumps(payload)


def verify_action_token(token: str) -> dict | None:
    serializer = _get_serializer()
    try:
        return serializer.loads(token, max_age=TOKEN_MAX_AGE_SECONDS)
    except SignatureExpired:
        logger.warning("Action token expired.")
        return None
    except BadSignature as e:
        logger.error(f"Action token signature invalid: {e}")
        return None