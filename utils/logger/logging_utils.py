import time

from utils.logger.logging_config import logger



def log_action_time(action_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            logger.info(f"Start {action_name}")
            result = func(*args, **kwargs)
            end = time.time()
            elapsed_ms = (end - start) * 1000
            logger.info(f"End {action_name}, duration: {elapsed_ms:.2f} ms")
            return result
        return wrapper
    return decorator

# ------------------------------------------------------------------
# ------------------------------------------------------------------
