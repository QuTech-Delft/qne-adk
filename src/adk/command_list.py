"""
Entry point for the qne command-line.
Creates the Typer app and its commands
"""

import logging
from pathlib import Path
from typing import List, Optional, Tuple
from tabulate import tabulate

import typer
from typer import Typer

from adk.api.local_api import LocalApi
from adk.api.remote_api import RemoteApi
from adk.command_processor import CommandProcessor
from adk.decorators import catch_qne_adk_exceptions
from adk.exceptions import NotEnoughRoles, RolesNotUnique, CommandNotImplemented, ExperimentDirectoryNotValid, \
                           ApplicationNotFound
from adk.managers.config_manager import ConfigManager
from adk.settings import Settings
from adk.type_aliases import ErrorDictType
from adk.utils import reorder_data, validate_path_name

app = Typer(add_completion=False)
applications_app = Typer()
app.add_typer(applications_app, name="application", help="Manage applications")
experiments_app = Typer()
app.add_typer(experiments_app, name="experiment", help="Manage experiments")

settings = Settings()
config_manager = ConfigManager(config_dir=settings.config_dir)
local_api = LocalApi(config_manager=config_manager)
remote_api = RemoteApi(config_manager=config_manager)
processor = CommandProcessor(local_api=local_api, remote_api=remote_api)

logging.basicConfig(level=logging.INFO)


@app.command("login")
@catch_qne_adk_exceptions
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
@catch_qne_adk_exceptions
def logout(host: str = typer.Argument(None)) -> None:
    """
    Log out from a Quantum Network Explorer.
    """
    raise CommandNotImplemented


@applications_app.command("create")
@catch_qne_adk_exceptions
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
    # Lower case roles for testing for the same role
    lower_case_roles = [role.lower() for role in roles]
    if not all(lower_case_roles.count(role) == 1 for role in lower_case_roles):
        raise RolesNotUnique()

    validate_path_name("Application", application_name)
    for role in roles:
        validate_path_name("Role", role)

    cwd = Path.cwd()
    application_path = cwd / application_name
    processor.applications_create(application_name=application_name, roles=roles, application_path=application_path)
    typer.echo(f"Application '{application_name}' created successfully in directory '{str(cwd)}'")


def retrieve_application_name_and_path(application_name: Optional[str]) -> Tuple[Path, str]:
    if application_name is not None:
        validate_path_name("Application", application_name)
        application_path_temp = config_manager.get_application_path(application_name)
        if application_path_temp is None:
            application_path = application_path_temp
        else:
            application_path_unwrapped: str = application_path_temp
            application_path = Path(application_path_unwrapped)
    else:
        application_path = Path.cwd()
        application_name, _ = config_manager.get_application_from_path(application_path)

    if application_path is None or not application_path.is_dir():
        raise ApplicationNotFound(application_name)

    return application_path, application_name


@applications_app.command("delete")
@catch_qne_adk_exceptions
def applications_delete(
    application_name: Optional[str] = typer.Argument(None, help="Name of the application")
) -> None:
    """
    Delete application files from application directory. Currently only local

    When application_name is given ./application_name is taken as application directory, when this directory is
    not valid the application directory is fetched from the application configuration. When application_name is
    not given, the current directory is taken as application directory.
    """

    application_path, application_name = retrieve_application_name_and_path(application_name=application_name)

    deleted_completely = processor.applications_delete(application_name=application_name,
                                                       application_path=application_path)
    if deleted_completely:
        typer.echo("Application deleted successfully")
    else:
        if application_name is None:
            typer.echo("Application files deleted")
        else:
            typer.echo("Application files deleted, directory not empty")


@applications_app.command("init")
@catch_qne_adk_exceptions
def applications_init() -> None:
    """
    Initialize an existing application.
    """
    raise CommandNotImplemented


@applications_app.command("upload")
@catch_qne_adk_exceptions
def applications_upload() -> None:
    """
    Create or update a remote application.
    """
    raise CommandNotImplemented


@applications_app.command("list")
@catch_qne_adk_exceptions
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
@catch_qne_adk_exceptions
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
@catch_qne_adk_exceptions
def applications_validate(
    application_name: Optional[str] = typer.Argument(None, help="Name of the application")
) -> None:
    """
    Validate the application.
    """

    application_path, application_name = retrieve_application_name_and_path(application_name=application_name)

    typer.echo(f"Validate application '{application_name}'")
    error_dict = processor.applications_validate(application_name=application_name, application_path=application_path)

    show_validation_messages(error_dict)

    if error_dict["error"] or error_dict["warning"]:
        typer.echo(f"Application '{application_name}' is invalid")
    else:
        typer.echo(f"Application '{application_name}' is valid")

@experiments_app.command("create")
@catch_qne_adk_exceptions
def experiments_create(
    experiment_name: str = typer.Argument(..., help="Name of the experiment"),
    application_name: str = typer.Argument(..., help="Name of the application"),
    network_name: str = typer.Argument(..., help="Name of the network to use"),
    local: bool = typer.Option(
        True, "--local", help="Run the application locally"
    )
) -> None:
    """
    Create new experiment.
    """
    # Temporary force local only
    if not local:
        local = True
    validate_path_name("Experiment", experiment_name)

    cwd = Path.cwd()

    path, application_name = retrieve_application_name_and_path(application_name=application_name)
    validate_dict = processor.applications_validate(application_name=application_name, application_path=path)
    if validate_dict["error"] or validate_dict["warning"]:
        show_validation_messages(validate_dict)
        typer.echo(f"Application '{application_name}' is invalid. Experiment not created.")
    else:
        processor.experiments_create(experiment_name=experiment_name, application_name=application_name,
                                     network_name=network_name, local=local, path=cwd)
        typer.echo(f"Experiment '{experiment_name}' created successfully in directory '{cwd}'")


@experiments_app.command("list")
@catch_qne_adk_exceptions
def experiments_list() -> None:
    """
    List experiments.
    """
    raise CommandNotImplemented


def retrieve_experiment_name_and_path(experiment_name: Optional[str]) -> Tuple[Path, str]:
    path = Path.cwd()
    if experiment_name is not None:
        validate_path_name("Experiment", experiment_name)
        experiment_path = path / experiment_name
    else:
        experiment_name = path.name
        experiment_path = path

    if not experiment_path.is_dir():
        raise ExperimentDirectoryNotValid(str(experiment_path))

    return experiment_path, experiment_name


@experiments_app.command("delete")
@catch_qne_adk_exceptions
def experiments_delete(
    experiment_name: Optional[str] = typer.Argument(None, help="Name of the experiment")
) -> None:
    """
    Delete experiment files.

    When experiment_name is given ./experiment_name is taken as experiment path, otherwise current directory.
    """

    experiment_path, experiment_name = retrieve_experiment_name_and_path(experiment_name=experiment_name)
    deleted_completely = processor.experiments_delete(experiment_name=experiment_name, experiment_path=experiment_path)
    if deleted_completely:
        typer.echo("Experiment deleted successfully")
    else:
        if experiment_name is None:
            typer.echo("Experiment files deleted")
        else:
            typer.echo("Experiment files deleted, directory not empty")


@experiments_app.command("run")
@catch_qne_adk_exceptions
def experiments_run(
    experiment_name: Optional[str] = typer.Argument(None, help="Name of the experiment"),
    block: bool = typer.Option(False, "--block", help="Wait for the result to be returned")
) -> None:
    """
    Execute a run of the experiment.
    """

    experiment_path, _ = retrieve_experiment_name_and_path(experiment_name=experiment_name)

    # Validate the experiment before executing the run command
    validate_dict = processor.experiments_validate(experiment_path=experiment_path)

    if validate_dict["error"] or validate_dict["warning"]:
        show_validation_messages(validate_dict)
        typer.echo("Experiment is invalid. Please resolve the issues and then run the experiment.")
    else:
        results = processor.experiments_run(experiment_path=experiment_path, block=block)

        if results:
            if "error" in results["round_result"]:
                typer.echo("Error encountered while running the experiment")
                typer.echo(results["round_result"]["error"])
            else:
                typer.echo("Experiment run successfully. Check the results using command 'experiment results'")


@experiments_app.command("validate")
@catch_qne_adk_exceptions
def experiments_validate(
    experiment_name: Optional[str] = typer.Argument(None, help="Name of the experiment")
) -> None:
    """
    Validate the experiment configuration.
    """

    experiment_path, experiment_name = retrieve_experiment_name_and_path(experiment_name=experiment_name)
    typer.echo(f"Validate experiment '{experiment_name}'\n")

    error_dict = processor.experiments_validate(experiment_path=experiment_path)
    show_validation_messages(error_dict)

    if error_dict["error"] or error_dict["warning"]:
        typer.echo("Experiment is invalid")
    else:
        typer.echo("Experiment is valid")


@experiments_app.command("results")
@catch_qne_adk_exceptions
def experiments_results(
    experiment_name: Optional[str] = typer.Argument(None, help="Name of the experiment"),
    all_results: bool = typer.Option(False, "--all", help="Get all results for this experiment"),
    show: bool = typer.Option(False, "--show", help="Show the results on screen instead of saving to file"),
) -> None:
    """
    Get results for an experiment.
    """

    experiment_path, _ = retrieve_experiment_name_and_path(experiment_name=experiment_name)
    results = processor.experiments_results(all_results=all_results, experiment_path=experiment_path)
    if show:
        typer.echo(results)
    else:
        result_noun = "Results are" if all_results else "Result is"
        typer.echo(f"{result_noun} stored at location '{experiment_path}/results/processed.json'")
