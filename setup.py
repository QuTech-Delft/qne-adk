""" Quantum Network Explorer CLI

Copyright 2018 QuTech Delft

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
from setuptools import setup, find_packages


def get_version_number(module):
    """Extract the version number from the source code.
    Returns:
        Str: the version number.
    """
    with open("src/{}/version.py".format(module), "r") as file_stream:
        line = file_stream.readline().split()
        version_number = line[2].replace("'", "")
    return version_number


def get_long_description():
    """Extract the long description from the README file"""

    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()

    return long_description


setup(
    name="qne-cli",
    description="Command Line Interface to interact with the Quantum Network Explorer",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    version=get_version_number("cli"),
    author="QuantumNetworkExplorer",
    python_requires=">=3.7",
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "qne=cli.command_list:app",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
    ],
    license="Apache 2.0",
    packages=find_packages(where="src", exclude=["*tests*"]),
    install_requires=["typer[all]", "netqasm", "pydantic", "tabulate", "jsonschema"],
    extras_require={
        "dev": ["pylint", "coverage>=4.5.1", "mypy", "pytest", "black", "isort", "types-tabulate"],
        "rtd": [
            "sphinx",
            "sphinx_rtd_theme",
            "nbsphinx",
            "sphinx-automodapi",
            "recommonmark",
        ],
    },
)
