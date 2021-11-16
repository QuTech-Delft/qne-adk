# Quantum Network Explorer ADK
The QNE-ADK is a Quantum Network Explorer - Application Development Kit that allows you to create your own applications and experiments and run them on a simulator. As of now, the ADK can only run experiments locally. Remote interaction with the Quantum Network Explorer will be added in later updates. 

With the ADK you can create your own application using the ``qne application create`` command (see Commands below). An application directory is generated for you with all the necessary files for you to configure and prepare for an experiment. When configuring an application, you specify the different roles and what types of inputs your application uses. In addition, you write the functionality of your application using the NetQASM library.

After creating and configuring an application, you can create an experiment for it using the ``qne experiment create`` command. Also here an experiment directory is generated with all necessary files. When configuring your experiment you can give values to the inputs that were specified when creating your application. You also choose which channels and nodes you use in your network and which role is linked to which node. A network consists of channels and each channel consists of two nodes. The nodes can communicate with each other using the channel between them.

Once your experiment is configured you are ready to run it using the ``qne experiment run`` command. Your experiment is parsed and sent to the NetSquid simulator. After some time your experiment run will be finished and a results directory will be generated in which all the results of your experiment are stored.


## Prerequisites
- A modern Linux or MacOS (10 or 11) 64-bit (x86_64) operating system. If you don’t have Linux or MacOS you could run it via virtualization, e.g. using VirtualBox. If you have Windows 10 or 11 you can also use the [Bash on Ubuntu](https://docs.microsoft.com/en-us/windows/wsl/) subsystem.
- A [virtual environment](https://docs.python.org/3/library/venv.html) should be created and activated before creating an application.
- Python version 3.7 or higher and pip version 19 or higher.
- NetQASM makes use of SquidASM for which you need credentials in order to use it. These credentials can be obtained by registering on the forum of [NetSquid](https://forum.netsquid.org/).


## Installation
To install all the required packages, execute the following command:

```
pip install qne-adk
```

After installing the qne-cli, you can install SquidASM. Replace '{netsquid-user-name}' and '{netsquid-password}' with the credentials you registered on [NetSquid](https://forum.netsquid.org/):

```
pip install squidasm --extra-index-url=https://{netsquid-user-name}:{netsquid-password}@pypi.netsquid.org
```

Now everything should be setup and ready in order to create your own applications and experiments and run them on the simulator!


## Commands
The QNE-ADK uses various commands to create and run your applications and experiments. All of the commands are listed below:

<!--- QNE APPLICATION CREATE --->
<details closed>
<summary><b>qne application create</b></summary>
Create a new application in your current directory containing all the files that are needed to write your application. The application directory name will be based on the value given to <b>application</b>. Two child directories <b>src</b> and <b>config</b> will be created, along with the default files.
<br></br>
    
```
qne application create [OPTIONS] APPLICATION_NAME ROLES...

Arguments:
  APPLICATION_NAME  Name of the application  [required]
  ROLES...          Names of the roles to be created  [required]

Options:
  --help  Show this message and exit.
  
Example:
  qne application create application_name role_name1 role_name2
```
</details>


<!--- QNE APPLICATION DELETE --->
<details closed>
<summary><b>qne application delete</b></summary>
Used to delete an application. Will delete the entire application directory structure.
<br></br>
    
```
qne application delete [OPTIONS] APPLICATION_NAME

Arguments:
  APPLICATION_NAME  Name of the application  [required]

Options:
  --help  Show this message and exit.

Example:
  qne application delete application_name
```
</details>



<!--- QNE APPLICATION LIST --->
<details closed>
<summary><b>qne application list</b></summary>
Show a list of all existing applications and the path to where they are stored.
<br></br>
    
```
qne application list [OPTIONS]

Options:
  --local  List local applications  [default: False].
  --help   Show this message and exit.

Example:
  qne application list
```
</details>



<!--- QNE APPLICATION VALIDATE --->
<details closed>
<summary><b>qne application validate</b></summary>
This command can be used to validate the files that are in the application directory. It checks for a correct file structure, if all files and directories needed exist and if the json files are in correct format.
<br></br>
    
```
qne application validate [OPTIONS]

Options:
  --help  Show this message and exit.
  
Example:
  qne application validate
```
</details>



<!--- QNE EXPERIMENT CREATE --->
<details closed>
<summary><b>qne experiment create</b></summary>
Create a new experiment, based on an application name and a chosen network.
<br></br>
    
```
qne experiment create [OPTIONS] EXPERIMENT_NAME APPLICATION_NAME NETWORK_NAME

Arguments:
  EXPERIMENT_NAME   Name of the experiment.  [required]
  APPLICATION_NAME  Name of the application.  [required]
  NETWORK_NAME      Name of the network to be used. [required]

Options:
  --local  Run the application locally  [default: True]
  --help   Show this message and exit.
  
Example:
  qne experiment create experiment_name application_name europe
```
</details>



<!--- QNE EXPERIMENT VALIDATE --->
<details closed>
<summary><b>qne experiment validate</b></summary>
Validates whether the experiment file structure is  complete and if the json content is valid.
<br></br>

```
qne experiment validate [OPTIONS]

Options:
  --help  Show this message and exit.
  
Example:
  qne experiment validate
```
</details>


<!--- QNE EXPERIMENT DELETE --->
<details closed>
<summary><b>qne experiment delete</b></summary>
Delete the entire experiment.
<br></br>
    
```
qne experiment delete [OPTIONS] EXPERIMENT_NAME

Arguments:
  EXPERIMENT_NAME  Name of the experiment

Options:
  --help  Show this message and exit.
  
Example:
  qne experiment delete experiment_name
```
</details>


<!--- QNE EXPERIMENT RUN --->
<details closed>
<summary><b>qne experiment run</b></summary>
This command will parse all experiment files and run them on the NetSquid simulator.
<br></br>

```
qne experiment run [OPTIONS]

Options:
  --block  Wait for the result to be returned.  [default: False]
  --help   Show this message and exit.
  
Example:
  qne experiment run
```
</details>



<!--- QNE EXPERIMENT RESULTS --->
<details closed>
<summary><b>qne experiment results</b></summary>
Download the results for an experiment that has been run.
<br></br>
    
```
qne experiment results [OPTIONS]

Options:
  --all   Get all results for this experiment.  [default: False]
  --show  Show the results on screen instead of saving to file.  [default:
          False]
  --help  Show this message and exit.
  
Example:
  qne experiment results
```
</details>



## More documentation
More documentation about these commands and about the files that are generated can be found in the QNE-ADK user guide on the Quantum Network Explorer [knowledge base](https://www.quantum-network.com/knowledge-base/qne-adk).
