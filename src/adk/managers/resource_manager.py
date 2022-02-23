from pathlib import Path
import tarfile
from typing import Tuple

from adk.type_aliases import app_configNetworkType, ApplicationDataType


class ResourceManager:
    """Manager that makes sure that the correct source files are packed and ready to be uploaded.

    The ResourceManager creates a tarball of the application source files. The tarball with source files are uploaded
    in the AppSource object.

    """
    def prepare_resources(self, application_data: ApplicationDataType, application_path: Path,
                          app_config: app_configNetworkType) -> Tuple[str, str]:
        """ The app-files needed for running the application are in the src directory. For each role a
        source file is expected and added to the tarball.

        A tarball of the source files is created and put in the src directory, ready to be uploaded later.

        Args:
            application_data: application data from manifest.json
            application_path: path to application files (local)
            app_config: app_config data for this application

        Returns:
            the full path to the tarball and the file name of the tarball
        """
        app_src_path = application_path / 'src'
        app_file_name = (application_data["remote"]["slug"] + ".tar.gz")
        app_file_path = app_src_path / app_file_name
        with tarfile.open(app_file_path, "w:gz") as tar:
            for role in app_config["roles"]:
                arc_name = f'app_{role.lower()}.py'
                file_name = app_src_path / arc_name
                tar.add(name=file_name, arcname=arc_name, recursive=False)
        return str(app_file_path), app_file_name

    def delete_resources(self, application_data: ApplicationDataType, application_path: Path) -> None:
        """ The tar-ball is deleted from the src-directory

        Args:
            application_data: application data from manifest.json
            application_path: path to application files (local)
        """
        app_src_path = application_path / 'src'
        app_file_name = (application_data["remote"]["slug"] + ".tar.gz")
        app_file_path = app_src_path / app_file_name
        if app_file_path.is_file():
            app_file_path.unlink()
