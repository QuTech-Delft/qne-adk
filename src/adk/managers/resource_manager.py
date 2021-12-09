import logging
import os
from pathlib import Path
import tarfile
from typing import cast

from adk.api.qne_client import QneFrontendClient
from adk.type_aliases import AppSourceType, AppConfigType, ApplicationDataType


class ResourceManager:
    """Manager that makes sure that the correct source files are downloaded and unpacked to the input directory.

    The ResourceManager keeps track of the source files that have been used and the ones that are needed for the new
    execution. If the source files that are needed for the current execution are not yet used, the manager will download
    them and store them in the cache directory. After this, it will assume that the tarball needed is present and can
    be unzipped to the input directory.

    Args:
        cache_dir: The directory that contains the uploaded tarballs.
        input_dir: The directory that will contain unzipped application.
        api_client: The client that connects to the API-Router.
    """

    def __init__(self, qne_client: QneFrontendClient) -> None:
        self._qne_client = qne_client

    def prepare_resources(self, application_data: ApplicationDataType, application_path: Path,
                          app_config: AppConfigType) -> AppSourceType:
        """Make sure that the files needed for running the application are in the src directory.

        The source files depicted in the AppSource object may have been downloaded for a prior run of the algorithm. If
        that is the case, this method will reuse those source files. If not, the tarball will be downloaded again from
        the API-Router. In all cases, the tarball will be extracted from the cache_dir to the input_dir.

        Args:
            application_path:
        """
        app_source = {}
        app_src_path = application_path / 'src'
        file_path = app_src_path / (application_data["meta"]["slug"] + ".tar.gz")
        with tarfile.open(file_path, "w:gz") as tar:
            for role in app_config["network"]["roles"]:
                filename = app_src_path / f'app_{role.lower()}.py'
                tar.add(name=filename, recursive=False)
        #source_files = self._qne_client.upload_source_files(file_path)
        app_source["source_files"] = file_path
        return app_source

    @staticmethod
    def __get_file_name(url: str) -> str:
        """Get the file name at the end of the URL.

        An URL pointing to a file has the format of http://domain.tld/file_name.ext. This method will strip off
        everything before the last slash and return only file_name.ext.

        Args:
            url: The url that should be parsed.

        Returns:
            Filename the url points to.
        """
        return os.path.basename(url)
