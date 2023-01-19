import os
from pathlib import Path
import tarfile
from typing import cast, Tuple, List

from adk.api.qne_client import QneFrontendClient
from adk.exceptions import InvalidPath
from adk.type_aliases import ApplicationDataType, AppSourceType


class ResourceManager:
    """Manager that makes sure that the correct source files are packed and ready to be uploaded.

    The ResourceManager creates a tarball of the application source files. The tarball with source files are uploaded
    in the AppSource object.

    """
    @staticmethod
    def prepare_resources(application_data: ApplicationDataType, application_path: Path,
                          files_list: List[str]) -> Tuple[str, str]:
        """ The app-files needed for running the application are in the src directory. For each role a
        source file is expected and added to the tarball.

        A tarball of the source files is created and put in the src directory, ready to be uploaded later.

        Args:
            application_data: application data from manifest.json
            application_path: path to application files (local)
            files_list: list of application files for this application

        Returns:
            the full path to the tarball and the file name of the tarball
        """
        app_src_path = application_path / 'src'
        app_file_name = (application_data["remote"]["slug"] + ".tar.gz")
        app_file_path = app_src_path / app_file_name
        with tarfile.open(app_file_path, "w:gz") as tar:
            for arc_name in files_list:
                file_name = app_src_path / arc_name
                tar.add(name=file_name, arcname=arc_name, recursive=False)
        return str(app_file_path), app_file_name

    @staticmethod
    def delete_resources(application_data: ApplicationDataType, application_path: Path) -> None:
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

    def generate_resources(self, qne_client: QneFrontendClient,
                           app_source: AppSourceType, application_path: Path) -> None:
        """ Generate the application files needed for running the application in the input directory.

        The source files depicted in the AppSource object (the tarball) will be downloaded from
        the API-Router. In all cases, the tarball will be extracted to the src dir.

        Args:
            qne_client: client for api-router access
            app_source: Object that describes the source files for the algorithm.
            application_path: path to application files (local)
        """
        app_src_path = application_path / 'src'
        if not app_src_path.exists():
            app_src_path.mkdir(parents=True, exist_ok=True)

        source_file = cast(str, app_source['source_files'])
        if source_file is not None:
            file_name = self.__get_file_name(source_file)
            file_path = app_src_path / file_name
            if not file_path.exists():
                qne_client.download_source_files(source_file, app_src_path, file_name)

            with tarfile.open(file_path, "r:gz") as tar:

                def is_within_directory(app_src_path: str, target: str) -> bool:
                    """ Check if target path of tar-files is in the application source directory. """
                    abs_app_src_path = os.path.abspath(app_src_path)
                    abs_target = os.path.abspath(target)

                    prefix = os.path.commonprefix([abs_app_src_path, abs_target])

                    return prefix == abs_app_src_path

                def safe_extract(tar: tarfile.TarFile, app_src_path: str) -> None:
                    """ Extract only when target path for all tar-files is in the application source directory. """
                    for member in tar.getmembers():
                        member_path = os.path.join(app_src_path, member.name)
                        if not is_within_directory(app_src_path, member_path):
                            raise InvalidPath(member.name)

                    tar.extractall(app_src_path)

                safe_extract(tar, str(app_src_path))

            # delete it afterwards
            if file_path.is_file():
                file_path.unlink()

    @staticmethod
    def __get_file_name(url: str) -> str:
        """Get the file name at the end of the URL.

        A URL pointing to a file has the format of http://domain.tld/file_name.ext. This method will strip off
        everything before the last slash and return only file_name.ext.

        Args:
            url: The url that should be parsed.

        Returns:
            Filename the url points to.
        """
        return os.path.basename(url)
