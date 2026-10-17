from typing import Any


TOKEN_ERROR_PATTERNS = [
    "token habis",
    "insufficient_quota",
    "rate_limit_exceeded",
    "quota exceeded",
    "token limit",
    "resource_exhausted",
    "resourceexhausted",
    "too many requests",
    "sistem sibuk",
    "rate limit exceeded",
    "exceeded your current quota",
    "429",
]


class TokenExhaustedError(Exception):
    """Raised when LLM quota or token limit is reached."""
    pass


def is_token_or_quota_error(target: Any) -> bool:
    """
    Checks if a given string, Exception, or response object contains
    indications of token or quota exhaustion.
    """
    if target is None:
        return False
    msg = str(target).lower()
    return any(pattern in msg for pattern in TOKEN_ERROR_PATTERNS)
