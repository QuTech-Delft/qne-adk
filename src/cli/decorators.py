import functools
import logging
import typer
from typing import Any, Callable

from cli.exceptions import NotEnoughRoles, QneCliException


def catch_qne_cli_exceptions(func: Callable[..., Any]) -> Any:
    """ Decorator function to catch exceptions and print an error message """
    @functools.wraps(func)
    def catch_exceptions(*args: Any, **kwargs: Any) -> Any:
        try:
            func(*args, **kwargs)
        except QneCliException as qne_cli_exception:
            message = f"Error: {str(qne_cli_exception)}"
            typer.echo(message)
        except Exception as exception:
            message = f"Unhandled exception: {repr(exception)}"
            typer.echo(message)

    return catch_exceptions


def log_function(func: Callable[..., Any]) -> Any:
    def log_function_name(*args: Any, **kwargs: Any) -> Any:
        logging.debug("Method '%s' has been entered.", func.__name__)
        resp = func(*args, **kwargs)
        logging.debug("Method '%s' has been exited.", func.__name__)
        return resp

    return log_function_name
