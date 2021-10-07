"""
Entry point for the qne command-line.
Creates the typer app and its commands
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
from cli.managers.config_manager import ConfigManager
from cli.settings import Settings
from cli.utils import reorder_data, validate_path_name
from cli.exceptions import NotEnoughRoles

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
def login(
    host: str = typer.Argument(None),
    username: str = typer.Option(..., prompt=True, help="Username of the remote user."),
    password: str = typer.Option(
        ..., prompt=True, hide_input=True, help="Password of the remote user."
    ),
) -> None:
    """
    Log in to a Quantum Network Explorer.
    """
    typer.echo(f"Log in to '{host}', as user '{username}'.")
    processor.login(host=host, username=username, password=password)
    typer.echo("Log in succeeded.")


@app.command("logout")
def logout(host: str = typer.Argument(None)) -> None:
    """
    Log out from a Quantum Network Explorer.
    """
    logout_host = "active" if host is None else f"'{host}'"
    typer.echo(f"Logging out from {logout_host} host.")
    processor.logout(host=host)
    typer.echo("Log out succeeded.")


@applications_app.command("create")
def applications_create(
    application_name: str = typer.Argument(..., help="Name of the application."),
    roles: List[str] = typer.Argument(..., help="Names of the roles to be created."),
) -> None:
    """
    Create new application. e.g.: qne application create application_name role1 role2
    """

    if len(roles) <= 1:
        raise NotEnoughRoles()

    validate_path_name("Application", application_name)
    for role in roles:
        validate_path_name("Role", role)

    # Lowercase roles
    roles = [role.lower() for role in roles]

    cwd = Path.cwd()
    typer.echo(f"Create application '{application_name}' in directory '{cwd}'.")
    processor.applications_create(application_name=application_name, roles=roles, path=cwd)
    typer.echo("Application successfully created.")


@applications_app.command("delete")
def applications_delete() -> None:
    """
    Delete remote application.
    """
    cwd = Path.cwd()
    application_name, _ = config_manager.get_application_from_path(cwd)
    typer.echo(f"Delete application '{application_name}'.")
    processor.applications_delete(application_name=application_name)
    typer.echo("Application deleted successfully.")


@applications_app.command("init")
def applications_init() -> None:
    """
    Initialize an existing application.
    """
    cwd = Path.cwd()
    typer.echo(
        f"Initialize directory '{cwd}' as a Quantum Network Explorer application."
    )
    processor.applications_init(cwd)
    typer.echo("Directory successfully initialized.")


@applications_app.command("upload")
def applications_upload() -> None:
    """
    Create or update a remote application.
    """
    cwd = Path.cwd()
    application_name, _ = config_manager.get_application_from_path(cwd)
    typer.echo(f"Upload application '{application_name}' to Quantum Network Explorer.")
    processor.applications_upload(application_name=application_name)
    typer.echo("Application successfully uploaded.")


@applications_app.command("list")
def applications_list(
    remote: Optional[bool] = typer.Option(
        False, "--remote", help="List remote applications."
    ),
    local: Optional[bool] = typer.Option(
        False, "--local", help="List local applications."
    ),
) -> None:
    """
    List applications available to the user.

    Args:
        remote: Boolean flag to list remote applications
        local: Boolean flag to list local applications
    """
    if not remote and not local:
        remote = local = True

    applications = processor.applications_list(remote=remote, local=local)

    if local:
        if len(applications['local']) == 0:
            typer.echo("There are no local applications available.")
        else:
            typer.echo(f"{len(applications['local'])} local application(s).")
            desired_order_columns = ['name', 'application_id', 'path']
            local_app_list = reorder_data(applications['local'], desired_order_columns)
            typer.echo(tabulate(local_app_list, headers='keys'))
            typer.echo()

    if remote:
        if len(applications['remote']) == 0:
            typer.echo("There are no remote applications available.")
        else:
            typer.echo(f"{len(applications['remote'])} remote application(s).")
            desired_order_columns = ['name', 'application_id', 'path']
            remote_app_list = reorder_data(applications['remote'], desired_order_columns)
            typer.echo(tabulate(remote_app_list, headers='keys'))


@applications_app.command("publish")
def applications_publish() -> None:
    """
    Request the application to be published online.
    """
    cwd = Path.cwd()
    application_name, _ = config_manager.get_application_from_path(cwd)
    typer.echo(f"Publish application '{application_name}'.")
    processor.applications_publish(application_name=application_name)
    typer.echo("Request to publish application sent successfully.")


@applications_app.command("validate")
def applications_validate() -> None:
    """
    Validate the application.
    """
    cwd = Path.cwd()
    application_name, _ = config_manager.get_application_from_path(cwd)
    typer.echo(f"Validate application '{application_name}'.\n")
    error_dict = processor.applications_validate(application_name=application_name)

    for key in error_dict:
        if error_dict[key]:
            for item in error_dict[key]:
                typer.echo(f"{key.upper()}: {item}")
            print("\n")

    if error_dict['error'] or error_dict['warning']:
        typer.echo("Application is invalid.")
    else:
        typer.echo("Application is valid.")


@experiments_app.command("create")
def experiments_create(
    name: str = typer.Argument(..., help="Name of the experiment."),
    application: str = typer.Argument(..., help="Name of the application."),
    network_name: str = typer.Argument(..., help="Name of the network to use."),
    local: bool = typer.Option(
        True, "--local/--remote", help="Run the application locally."
    ),
) -> None:
    """
    Create new experiment.
    """
    validate_path_name("Experiment", name)

    cwd = Path.cwd()
    typer.echo(f"Create experiment: '{name}' with network: '{network_name}' for application: '{application}'.")

    # is_app_valid, validation_message = processor.applications_validate(application)
    # TODO: Uncomment above line after application validate command is ready
    is_app_valid, validation_message = True, 'Valid'

    if is_app_valid:
        success, message = processor.experiments_create(name=name, application=application, network_name=network_name,
                                                        local=local, path=cwd)
        if success:
            typer.echo("Experiment created successfully.")
        else:
            typer.echo("Experiment could not be created. " + message)
    else:
        typer.echo(f"The application {application} is not valid. " + validation_message)
        typer.echo("You can use the application validate command to check the application.")

@experiments_app.command("list")
def experiments_list() -> None:
    """
    List experiments.
    """
    typer.echo("List all remote experiments.")
    experiments = processor.experiments_list()
    for experiment in experiments:
        typer.echo(experiment)


@experiments_app.command("delete")
def experiments_delete() -> None:
    """
    Delete local and remote experiment files.
    """
    cwd = Path.cwd()
    typer.echo("Delete local and remote experiment files.")
    processor.experiments_delete(path=cwd)
    typer.echo("Experiment deleted successfully.")


@experiments_app.command("run")
def experiments_run(
    block: bool = typer.Option(
        False, "--block", help="Wait for the result to be returned."
    )
) -> None:
    """
    Execute a run of the experiment.
    """
    cwd = Path.cwd()
    typer.echo("Run experiment.")
    processor.experiments_run(path=cwd, block=block)
    if block:
        typer.echo("Experiment has run successfully.")
    else:
        typer.echo("Experiment has been created successfully.")


@experiments_app.command("validate")
def experiments_validate() -> None:
    """
    Validate the experiment configuration.
    """
    cwd = Path.cwd()
    typer.echo(f"Validate experiment at '{cwd}'.")
    is_valid, message = processor.experiments_validate(path=cwd)
    if is_valid:
        typer.echo("Experiment is valid.")
    else:
        typer.echo("Experiment is not valid. " + message)


@experiments_app.command("results")
def experiments_results(
    all_results: bool = typer.Option(
        False, "--all", help="Get all results for this experiment."
    ),
    show: bool = typer.Option(
        False, "--show", help="Show the results on screen instead of saving to file."
    ),
) -> None:
    """
    Get results for an experiment.
    """
    result_noun = "results" if all_results else "result"
    typer.echo(f"Get {result_noun} for this experiment.")
    cwd = Path.cwd()
    results = processor.experiments_results(all_results=all_results, show=show, path=cwd)
    if show:
        for result in results:
            typer.echo(result)
    else:
        typer.echo(f"{result_noun.title()} stored successfully.")
