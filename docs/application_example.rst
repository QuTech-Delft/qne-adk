###################
Application example
###################

This section shows a complete example of a working application. Below, all files are shown, which are generated when
creating your application and experiment and its contents. You can use this example to see what a complete application
and experiment looks like and see how you can apply some of the examples to your experiment.

***********
Application
***********

Create your application using the following command:

.. code-block:: console

    qne application create teleport Sender Receiver

Config
======

Within the config directory, you can find the application.json, network.json, and result.json. Result.json can be left
as it is. Fill in application.json and network.json with the examples given below.

application.json
----------------
.. literalinclude:: json_examples/application_conf_example.json
  :language: JSON

network.json
------------
.. literalinclude:: json_examples/network_conf_example.json
  :language: JSON

Src
===

After creating your application, a src directory has also been created containing the files app_sender.py and
app_receiver.py. Below two examples are given, which you can use to fill in these files.

app_sender.py
-------------
.. literalinclude:: src_examples/app_sender.py
  :language: Python

app_receiver.py
---------------
.. literalinclude:: src_examples/app_receiver.py
  :language: Python

Manifest
========

After creating your application, a manifest.json file has been created containing the information about the
application. You should edit it and add your information. The ``remote`` part of this file can be left as it is
and should not be edited.

manifest.json
-------------
.. literalinclude:: json_examples/application_manifest_example.json
  :language: JSON

Before proceeding to create your experiment, you can validate to check whether your application and json structure is
correct by running:

.. code-block:: console

    qne application validate teleport

***********
Experiment
***********

Create your experiment using the following command:

.. code-block:: console

    qne experiment create teleport_experiment teleport randstad

Input
======

After executing the experiment create command, an input directory is created within the experiment directory. These
files are all copied over from the teleport application and can be left untouched.

experiment.json
===============

Next to the input that is generated, an experiment.json file is generated as well. This is where you can choose which
nodes to use for your roles and give your inputs a specific value. Below is an entire experiment.json file as an
example. Use the contents of this example in your experiment.json file.

.. literalinclude:: json_examples/experiment_complete_example.json
  :language: JSON

Before running your experiment, you can validate if the file and json structure of your experiment is correct by
running:

.. code-block:: console

    qne experiment validate teleport_experiment

Run your experiment
===================

After you have created your experiment and modified the contents of experiment.json, you can run your experiment with
the following command:

.. code-block:: console

    qne experiment run teleport_experiment

Running the experiment will generate some raw outputs in your experiment directory and a processed.json file where
all the results of your experiment are stored!

Examine experiment results
==========================

.. code-block:: console

    qne experiment results --all teleport_experiment

Results of latest run are stored in processed.json

.. code-block:: console

    qne experiment results --show teleport_experiment

The result from processed.json is shown on the terminal.
