from tenacity import retry, wait_exponential, stop_after_attempt


retry_strategy = retry(
    wait=wait_exponential(multiplier=1, min=2, max=8),
    stop=stop_after_attempt(4),
)