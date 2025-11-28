from requests import RequestException
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception
from fastapi import HTTPException
from email_validator import EmailNotValidError


def is_transient_error(exception: BaseException) -> bool:
    if isinstance(exception, HTTPException) and exception.status_code == 404:
        return False

    if isinstance(exception, EmailNotValidError):
        return False

    return True

retry_strategy = retry(
    wait=wait_exponential(multiplier=1, min=2, max=8),
    stop=stop_after_attempt(4),
    retry=retry_if_exception(is_transient_error)
)