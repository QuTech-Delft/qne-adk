Introduction
============

The QNE-ADK is a Quantum Network Explorer - Application Development Kit that allows you to create your own applications
and experiments and run them on a simulator.

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

    pip install -e .[dev]

*Note: installing for development will install packages that are needed to develop the QNE-ADK itself.*

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

application list
^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application list [OPTIONS]

Show a list of all applications and relevant information for each of them.
For listing remote applications, the user must be logged in.

    Options:
      --remote  List remote applications  [default: False]
      --local   List local applications  [default: False].
      --help   Show this message and exit.

    Example:
      qne application list --remote

application create
^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application create [OPTIONS] APPLICATION_NAME ROLES...

Create a new application in your current directory containing all the files that are needed to write your application.
The application directory name will be based on the value given to `application`.
Two subdirectories `src` and `config` will be created, along with the default files.

    Arguments:
      APPLICATION_NAME  Name of the application [required]

      ROLES...          Names of the roles to be created [required]

    Options:
      --help  Show this message and exit.

    Example:
      qne application create my_application Alice Bob

application clone
^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application clone [OPTIONS] APPLICATION_NAME [NEW_APPLICATION_NAME]

Clone an existing remote (--remote) or local application to the current directory.
When a new application name is not given (remote only) the application will have the same name as the cloned
application. An application with the new application name may not already exist locally.
A local application must be valid before it can be cloned. For cloning a remote application the user must be logged in.
Cloning remote applications is limited to publicly available applications and applications of which the user is the
author.

    Arguments:
      APPLICATION_NAME  Name of the application to clone [required]

      [NEW_APPLICATION_NAME]  New name for the cloned application

    Options:
      --remote  Clone remote application  [default: False]
      --help  Show this message and exit.

    Example:
      qne application clone existing_application new_application

application delete
^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application delete [OPTIONS] [APPLICATION_NAME]

Delete the files of an application. Will try to delete the application directory
structure but keeps the files that are not part of the application.
For deleting remote parts of the application, the user must be logged in.

When application_name is given ./application_name is taken as application
directory, when this directory does not contain an application the
application directory is fetched from the application configuration. When
application_name is not given, the current directory is taken as
application directory.

    Arguments:
      [APPLICATION_NAME]  Name of the application

    Options:
      --help  Show this message and exit.

    Example:
      qne application delete application_name

application validate
^^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application validate [OPTIONS]

Validate the application created locally.

When application_name is given ./application_name is taken as application
directory, when this directory does not contain an application the
application directory is fetched from the application configuration. When
application_name is not given, the current directory is taken as
application directory.

    Options:
      --help  Show this message and exit.

    Example:
      qne application validate

application upload
^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application upload [OPTIONS] [APPLICATION_NAME]

Create or update a remote application.
For creating or updating remote applications, the user must be logged in.

When application_name is given ./application_name is taken as application
directory, when this directory does not contain an application the
application directory is fetched from the application configuration. When
application_name is not given, the current directory is taken as
application directory.

    Arguments:
      [APPLICATION_NAME]  Name of the application

    Options:
      --help   Show this message and exit.

    Example:
      qne application upload application_name

application publish
^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne application publish [OPTIONS] [APPLICATION_NAME]

Request the application to be published online.
For publishing a new version of a remote application, the author of the application
must have run at least one successful experiment on the remote backend for the new
version of the application.
For publishing a new version of remote applications, the user must be logged in.

When application_name is given ./application_name is taken as application
directory, when this directory does not contain an application the
application directory is fetched from the application configuration. When
application_name is not given, the current directory is taken as
application directory.

    Arguments:
      [APPLICATION_NAME]  Name of the application

    Options:
      --help   Show this message and exit.

    Example:
      qne application publish application_name

experiment list
^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment list [OPTIONS]

List remote experiments.
For listing remote experiments, the user must be logged in.

    Options:
      --help   Show this message and exit.

    Example:
      qne experiment list

experiment create
^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment create [OPTIONS] EXPERIMENT_NAME APPLICATION_NAME NETWORK_NAME

Create a new experiment, based on an application name and a chosen network.
When the experiment is created for a remote application the user must be logged in.

    Arguments:
      EXPERIMENT_NAME   Name of the experiment.  [required]

      APPLICATION_NAME  Name of the application.  [required]

      NETWORK_NAME      Name of the network to be used. [required]

    Options:
      --remote  Use remote application configuration [default: False]
      --help   Show this message and exit.

    Example:
      qne experiment create experiment_name application_name europe

experiment delete
^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment delete [OPTIONS] [EXPERIMENT_NAME]

Delete experiment files.

Local: When deleting an experiment locally, argument EXPERIMENT_NAME_OR_ID
is the local experiment name, which is the subdirectory containing the
experiment files. When the argument is empty the current directory is
taken as experiment directory. The local experiment files are deleted,
when the experiment was created with '--remote' and the experiment was run
remotely, the remote experiment is also deleted.

Remote: the argument EXPERIMENT_NAME_OR_ID is the remote experiment id to
delete. No local files are deleted.

    Arguments:
      [EXPERIMENT_NAME_OR_ID]  Name of the experiment or remote id

    Options:
      --remote  Delete a remote experiment  [default: False]
      --help  Show this message and exit.

    Example:
      qne experiment delete experiment_name

experiment validate
^^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment validate [OPTIONS] [EXPERIMENT_NAME]

Validate the local experiment.

When experiment_name is given ./experiment_name is taken as experiment directory.
When experiment_name is not given, the current directory is taken as experiment
directory.

    Arguments:
      [EXPERIMENT_NAME]  Name of the experiment

    Options:
      --help  Show this message and exit.

    Example:
      qne experiment validate experiment_name

experiment run
^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment run [OPTIONS] [EXPERIMENT_NAME]

This command will parse all experiment files and run them on the NetSquid simulator.

When experiment_name is given ./experiment_name is taken as experiment directory.
When experiment_name is not given, the current directory is taken as experiment
directory.

    Arguments:
      [EXPERIMENT_NAME]  Name of the experiment

    Options:
      --block  Wait for the result to be returned.  [default: False]
      --help   Show this message and exit.

    Example:
      qne experiment run --block experiment_name

experiment results
^^^^^^^^^^^^^^^^^^

.. code-block:: console

    qne experiment results [OPTIONS] [EXPERIMENT_NAME]

Get results for an experiment that run successfully.

When experiment_name is given ./experiment_name is taken as experiment directory.
When experiment_name is not given, the current directory is taken as experiment
directory.

    Arguments:
      [EXPERIMENT_NAME]  Name of the experiment

    Options:
      --all   Get all results for this experiment.  [default: False]
      --show  Show the results on screen instead of saving to file.  [default:
              False]
      --help  Show this message and exit.

    Example:
      qne experiment results experiment_name

login
^^^^^

.. code-block:: console

    qne login [OPTIONS] [HOST]

Log in to a Quantum Network Explorer.

    Arguments:
      [HOST]  Name of the host to log in to

    Options:
      --username  TEXT Username of the remote user  [required]
      --password  TEXT Password of the remote user  [required]
      --help  Show this message and exit.

    Example:
      qne login --username=my_user_name --password=my_password https://api.quantum-network.com

logout
^^^^^^

.. code-block:: console

    qne logout [OPTIONS] [HOST]

Log out from Quantum Network Explorer.

    Arguments:
      [HOST]  Name of the host to log out from

    Options:
      --help  Show this message and exit.

    Example:
      qne logout https://api.quantum-network.com

network list
^^^^^^^^^^^^

.. code-block:: console

    qne network list [OPTIONS]

List available networks. For listing remote networks, the user must be logged in.

    Options:
      --remote  List remote networks  [default: False]
      --local   List local networks  [default: True]
      --help  Show this message and exit.

    Example:
      qne network list --remote

network update
^^^^^^^^^^^^^^

.. code-block:: console

    qne network update [OPTIONS]

Get remote networks and update local network files.
For updating local networks, the user must be logged in.

    Options:
      --overwrite  Overwrite local networks  [default: False]
      --help  Show this message and exit.

    Example:
      qne network update --overwrite

More documentation
------------------
Following this step-by-step documentation, it will give you a better understanding of:

* what each command implies
* which files are generated and their purpose
* a better understanding of what a quantum network consists of
* how to create and run your own applications and experiments

Bug reports
-----------

Please submit bug-reports `on the github issue
tracker <https://github.com/QuTech-Delft/qne-adk/issues>`_.
