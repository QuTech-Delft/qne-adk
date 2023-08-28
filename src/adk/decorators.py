import sys
import functools
import logging
from typing import Any, Callable

import typer

from adk.exceptions import QneAdkException


def catch_qne_adk_exceptions(func: Callable[..., Any]) -> Any:
    """ Decorator function to catch exceptions and print an error message """
    @functools.wraps(func)
    def catch_exceptions(*args: Any, **kwargs: Any) -> Any:
        try:
            func(*args, **kwargs)
        except QneAdkException as qne_adk_exception:
            typer.echo(f"Error: {str(qne_adk_exception)}")
            sys.exit(1)
        except Exception as exception:
            typer.echo(f"Unhandled exception: {repr(exception)}")
            sys.exit(13)

    return catch_exceptions


def log_function(func: Callable[..., Any]) -> Any:
    """ Decorator function to log entry and exit of the method/function """
    def log_function_name(*args: Any, **kwargs: Any) -> Any:
        logging.debug("Method '%s' has been entered.", func.__name__)
        resp = func(*args, **kwargs)
        logging.debug("Method '%s' has been exited.", func.__name__)
        return resp

    return log_function_name
