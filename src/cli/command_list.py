"""
Entry point for the qne command-line.
Creates the Typer app and its commands
"""

import logging
from pathlib import Path
from typing import List, Optional
from tabulate import tabulate

import typer
from typer import Typer

from cli.api.local_api import LocalApi
from cli.api.remote_api import RemoteApi
from cli.command_processor import CommandProcessor
from cli.decorators import catch_qne_cli_exceptions
from cli.exceptions import NotEnoughRoles, RolesNotUnique, CommandNotImplemented
from cli.managers.config_manager import ConfigManager
from cli.settings import Settings
from cli.type_aliases import ErrorDictType
from cli.utils import reorder_data, validate_path_name

app = Typer()
applications_app = Typer()
app.add_typer(applications_app, name="application", help="Manage applications")
experiments_app = Typer()
app.add_typer(experiments_app, name="experiment", help="Manage experiments")
results_app = Typer()
app.add_typer(results_app, name="result", help="Manage results")

settings = Settings()
config_manager = ConfigManager(config_dir=settings.config_dir)
local_api = LocalApi(config_manager=config_manager)
remote_api = RemoteApi(config_manager=config_manager)
processor = CommandProcessor(local_api=local_api, remote_api=remote_api)

logging.basicConfig(level=logging.INFO)


@app.command("login")
@catch_qne_cli_exceptions
def login(
    host: str = typer.Argument(None),
    username: str = typer.Option(..., prompt=True, help="Username of the remote user"),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password of the remote user"
    ),
) -> None:
    """
    Log in to a Quantum Network Explorer.
    """
    raise CommandNotImplemented


@app.command("logout")
@catch_qne_cli_exceptions
def logout(host: str = typer.Argument(None)) -> None:
    """
    Log out from a Quantum Network Explorer.
    """
    raise CommandNotImplemented

@applications_app.command("create")
@catch_qne_cli_exceptions
def applications_create(
    application_name: str = typer.Argument(..., help="Name of the application"),
    roles: List[str] = typer.Argument(..., help="Names of the roles to be created"),
) -> None:
    """
    Create new application.

    For example: qne application create my_application Alice Bob
    """

    # Check roles
    if len(roles) <= 1:
        raise NotEnoughRoles()
    # Lowercase roles
    roles = [role.lower() for role in roles]
    if not all(roles.count(role) == 1 for role in roles):
        raise RolesNotUnique()

    validate_path_name("Application", application_name)
    for role in roles:
        validate_path_name("Role", role)

    cwd = Path.cwd()
    processor.applications_create(application_name=application_name, roles=roles, path=cwd)
    typer.echo(f"Application '{application_name}' created successfully in directory '{str(cwd)}'")


@applications_app.command("delete")
@catch_qne_cli_exceptions
def applications_delete() -> None:
    """
    Delete remote application.
    """
    raise CommandNotImplemented


@applications_app.command("init")
@catch_qne_cli_exceptions
def applications_init() -> None:
    """
    Initialize an existing application.
    """
    raise CommandNotImplemented

@applications_app.command("upload")
@catch_qne_cli_exceptions
def applications_upload() -> None:
    """
    Create or update a remote application.
    """
    raise CommandNotImplemented

@applications_app.command("list")
@catch_qne_cli_exceptions
def applications_list(
    local: Optional[bool] = typer.Option(
        False, "--local", help="List local applications"
    ),
) -> None:
    """
    List applications available to the user.
    """
    # Temporary force local only
    remote = False

    if not remote and not local:
        local = True

    applications = processor.applications_list(remote=remote, local=local)

    if local:
        if len(applications['local']) == 0:
            typer.echo("There are no local applications available")
        else:
            desired_order_columns = ['name', 'application_id', 'path']
            local_app_list = reorder_data(applications['local'], desired_order_columns)
            typer.echo(tabulate(local_app_list, headers='keys'))
            typer.echo(f"{len(applications['local'])} local application(s)")
            typer.echo()

    if remote:
        if len(applications['remote']) == 0:
            typer.echo("There are no remote applications available")
        else:
            desired_order_columns = ['name', 'application_id', 'path']
            remote_app_list = reorder_data(applications['remote'], desired_order_columns)
            typer.echo(tabulate(remote_app_list, headers='keys'))
            typer.echo(f"{len(applications['remote'])} remote application(s)")


@applications_app.command("publish")
@catch_qne_cli_exceptions
def applications_publish() -> None:
    """
    Request the application to be published online.
    """
    raise CommandNotImplemented


def show_validation_messages(validation_dict: ErrorDictType) -> None:
    """
    Show the error, warnings and info messages collected during validation.
    """
    for key in validation_dict:
        if validation_dict[key]:
            for item in validation_dict[key]:
                typer.echo(f"{key.upper()}: {item}")


@applications_app.command("validate")
@catch_qne_cli_exceptions
def applications_validate() -> None:
    """
    Validate the application.
    """
    cwd = Path.cwd()
    application_name, _ = config_manager.get_application_from_path(cwd)
    typer.echo(f"Validate application '{application_name}'")
    error_dict = processor.applications_validate(application_name=application_name)

    show_validation_messages(error_dict)

    if error_dict["error"] or error_dict["warning"]:
        typer.echo("Application is invalid")
    else:
        typer.echo("Application is valid")


@experiments_app.command("create")
@catch_qne_cli_exceptions
def experiments_create(
    experiment_name: str = typer.Argument(..., help="Name of the experiment"),
    application_name: str = typer.Argument(..., help="Name of the application"),
    network_name: str = typer.Argument(..., help="Name of the network to use"),
    local: bool = typer.Option(
        True, "--local", help="Run the application locally"
    ),
) -> None:
    """
    Create new experiment.
    """
    # Temporary force local only
    if not local:
        local = True
    validate_path_name("Experiment", experiment_name)

    cwd = Path.cwd()

    validate_dict = processor.applications_validate(application_name)
    if validate_dict["error"] or validate_dict["warning"]:
        show_validation_messages(validate_dict)
        typer.echo(f"Application '{application_name}' is invalid. Experiment not created.")
    else:
        processor.experiments_create(experiment_name=experiment_name, application_name=application_name,
                                     network_name=network_name, local=local, path=cwd)
        typer.echo(f"Experiment '{experiment_name}' created successfully in directory '{cwd}'")


@experiments_app.command("list")
@catch_qne_cli_exceptions
def experiments_list() -> None:
    """
    List experiments.
    """
    raise CommandNotImplemented

@experiments_app.command("delete")
@catch_qne_cli_exceptions
def experiments_delete() -> None:
    """
    Delete local and remote experiment files.
    """
    raise CommandNotImplemented

@experiments_app.command("run")
@catch_qne_cli_exceptions
def experiments_run(
    block: bool = typer.Option(
        False, "--block", help="Wait for the result to be returned"
    )
) -> None:
    """
    Execute a run of the experiment.
    """
    cwd = Path.cwd()

    # Validate the experiment before executing the run command
    # processor.experiments_validate(path=cwd)

    results = processor.experiments_run(path=cwd, block=block)
    # if block:
    #     typer.echo("Experiment has run successfully.")
    # else:
    #     typer.echo("Experiment has been created successfully.")


@experiments_app.command("validate")
@catch_qne_cli_exceptions
def experiments_validate() -> None:
    """
    Validate the experiment configuration.
    """
    cwd = Path.cwd()
    experiment_name = cwd.name
    typer.echo(f"Validate experiment '{experiment_name}'\n")
    error_dict = processor.experiments_validate(path=cwd)
    show_validation_messages(error_dict)

    if error_dict["error"] or error_dict["warning"]:
        typer.echo("Experiment is invalid")
    else:
        typer.echo("Experiment is valid")


@experiments_app.command("results")
@catch_qne_cli_exceptions
def experiments_results(
    all_results: bool = typer.Option(
        False, "--all", help="Get all results for this experiment"
    ),
    show: bool = typer.Option(
        False, "--show", help="Show the results on screen instead of saving to file"
    ),
) -> None:
    """
    Get results for an experiment.
    """
    result_noun = "results" if all_results else "result"
    typer.echo(f"Get {result_noun} for this experiment")
    cwd = Path.cwd()
    results = processor.experiments_results(all_results=all_results, show=show, path=cwd)
    if show:
        for result in results:
            typer.echo(result)
    else:
        typer.echo(f"{result_noun.title()} stored successfully")
