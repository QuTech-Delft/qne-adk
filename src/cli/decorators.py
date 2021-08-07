import logging
from typing import Any, Callable


def log_function(func: Callable[..., Any]) -> Any:
    def log_function_name(*args: Any, **kwargs: Any) -> Any:
        logging.info("Method '%s' has been entered.", func.__name__)
        resp = func(*args, **kwargs)
        logging.info("Method '%s' has been exited.", func.__name__)
        return resp

    return log_function_name
