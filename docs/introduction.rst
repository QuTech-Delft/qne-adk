Introduction
============

The QNE-ADK is a Quantum Network Explorer - Application Development Kit that allows you to create your own applications
and experiments and run them on a simulator. As of now, the ADK can only run experiments locally. Remote interaction
with the Quantum Network Explorer will be added in later updates.

With the ADK you can create your own application using the ``qne application create`` command (see Commands below).
An application directory is generated for you with all the necessary files for you to configure and prepare for an
experiment. When configuring an application, you specify the different roles and what types of inputs your
application uses. In addition, you write the functionality of your application using the NetQASM library.

After creating and configuring an application, you can create an experiment for it using the ``qne experiment create``
command. Also here an experiment directory is generated with all necessary files. When configuring your experiment
you can give values to the inputs that were specified when creating your application. You also choose which channels
and nodes you use in your network and which role is linked to which node. A network consists of channels and each
channel consists of two nodes. The nodes can communicate with each other using the channel between them.

Once your experiment is configured you are ready to run it using the ``qne experiment run`` command. Your experiment
is parsed and sent to the NetSquid simulator. After some time your experiment run will be finished and a results
directory will be generated in which all the results of your experiment are stored.


Prerequisites
-------------
* A modern Linux or MacOS (10 or 11) 64-bit (x86_64) operating system. If you don't have Linux or MacOS you could run
  it via virtualization, e.g. using VirtualBox. If you have Windows 10 or 11 you can also use
  the `Bash on Ubuntu <https://docs.microsoft.com/en-us/windows/wsl/>`_ subsystem.
* A `virtual environment <https://docs.python.org/3/library/venv.html>`_ should be created and activated before
  creating an application.
* Python version 3.7 or higher and pip version 19 or higher.
* NetQASM makes use of SquidASM for which you need credentials in order to use it. These credentials can be obtained
  by registering on the forum of `NetSquid <https://forum.netsquid.org/>`_.

Installation
------------
To install all the required packages, execute the following command:

.. code-block:: console

    pip install qne-adk

After installing the qne-adk, you can install SquidASM. Replace '{netsquid-user-name}' and '{netsquid-password}' with
the credentials you registered on `NetSquid <https://forum.netsquid.org/>`_:

.. code-block:: console

    pip install squidasm --extra-index-url=https://{netsquid-user-name}:{netsquid-password}@pypi.netsquid.org

Now everything should be setup and ready in order to create your own applications and experiments and run them on
the simulator!

Installation from source
------------------------

The source for the QNE-ADK can also be found at Github. For the default installation execute:

.. code-block:: console

    git clone https://github.com/QuTech-Delft/qne-adk
    cd qne-adk
    pip install .

If you want to install for development, install with:

.. code-block:: console

    pip install .[dev]

Installing for generating documentation
---------------------------------------
To install the necessary packages to perform documentation activities for QNE-ADK do:

.. code-block:: console

    pip install -e .[rtd]

To build the 'readthedocs' documentation do:

.. code-block:: console

    cd docs
    make html

The documentation is then build in 'docs/_build/html' and can be viewed `here <index.html>`_.

Commands
--------
The QNE-ADK uses various commands to create and run your applications and experiments. All of the commands are
listed below:

application create
^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application create [OPTIONS] APPLICATION_NAME ROLES...

Create a new application in your current directory containing all the files that are needed to write your application.
The application directory name will be based on the value given to `application`. Two child directories `src` and
`config` will be created, along with the default files.

    Arguments:
      APPLICATION_NAME  Name of the application [required]

      ROLES...          Names of the roles to be created [required]

    Options:
      --help  Show this message and exit.

    Example:
      qne application create my_application Alice Bob

application delete
^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application delete [OPTIONS] [APPLICATION_NAME]

Used to delete an application. Will delete the entire application directory structure.
Delete application files from application directory. Currently only local.
When APPLICATION_NAME is given ./application_name is taken as application
directory, when this directory is not valid the application directory is
fetched from the application configuration. When application_name is not
given, the current directory is taken as application directory.

    Arguments:
      [APPLICATION_NAME]  Name of the application

    Options:
      --help  Show this message and exit.

    Example:
      qne application delete application_name


application list
^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application list [OPTIONS]

Show a list of all existing applications and the path to where they are stored.

    Options:
      --local  List local applications  [default: False].
      --help   Show this message and exit.

    Example:
      qne application list

application validate
^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application validate [OPTIONS]

This command can be used to validate the files that are in the application directory. It checks for a correct file
structure, if all files and directories needed exist and if the json files are in correct format.

    Options:
      --help  Show this message and exit.

    Example:
      qne application validate

experiment create
^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment create [OPTIONS] EXPERIMENT_NAME APPLICATION_NAME NETWORK_NAME

Create a new experiment, based on an application name and a chosen network.

    Arguments:
      EXPERIMENT_NAME   Name of the experiment.  [required]

      APPLICATION_NAME  Name of the application.  [required]

      NETWORK_NAME      Name of the network to be used. [required]

    Options:
      --local  Run the application locally  [default: True]
      --help   Show this message and exit.

    Example:
      qne experiment create experiment_name application_name europe

experiment validate
^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment validate [OPTIONS]

Validates whether the experiment file structure is complete and if the json content is valid.

    Options:
      --help  Show this message and exit.

    Example:
      qne experiment validate

experiment delete
^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment delete [OPTIONS] [EXPERIMENT_NAME]

Delete experiment files.

When experiment_name is given ./experiment_name is taken as experiment
path, otherwise current directory.

    Arguments:
      [EXPERIMENT_NAME]  Name of the experiment

    Options:
      --help  Show this message and exit.

    Example:
      qne experiment delete experiment_name

experiment run
^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment run [OPTIONS]

This command will parse all experiment files and run them on the NetSquid simulator.

    Options:
      --block  Wait for the result to be returned.  [default: False]
      --help   Show this message and exit.

    Example:
      qne experiment run

experiment results
^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment results [OPTIONS]

Get the results for an experiment that has been run.

    Options:
      --all   Get all results for this experiment.  [default: False]
      --show  Show the results on screen instead of saving to file.  [default:
              False]
      --help  Show this message and exit.

    Example:
      qne experiment results

More documentation
------------------
More documentation about these commands and about the files that are generated can be found in the QNE-ADK user guide
on the Quantum Network Explorer `Knowledge base <https://www.quantum-network.com/knowledge-base/qne-adk>`_.

Bug reports
-----------

Please submit bug-reports `on the github issue
tracker <https://github.com/QuTech-Delft/qne-adk/issues>`_.
