# Quantum Network Explorer ADK
Application Development Kit to interact with the Quantum Network Explorer. With the QNE-ADK you can create your application and experiment and run it locally using the commands. 

## Prerequisites
- Before installing any packages it is recommended that you have a python3 virtual environment activated that has pip installed. 
- NetQASM makes use of SquidASM for which you need credentials in order to use it. These credentials can either be obtained by registering on the forum of [NetSquid](https://forum.netsquid.org/ "NetSquid").


## Installation
To install all the required packages, execute the following commands:

```
pip install qne-adk
```

After installing the qne-cli, you can install SquidASM. Replace '{netsquid-user-name}' and '{netsquid-password}' with the credenials you registered on [NetSquid](https://forum.netsquid.org/ "NetSquid"):

```
pip install squidasm --extra-index-url=https://{netsquid-user-name}:{netsquid-password}@pypi.netsquid.org
```

Now everything should be setup and ready in order to create your own applications and experiments and run them on the simulator!


## Commands
The QNE-ADK uses various commands to create and run your applications and experiments. All of the commands are listed below:

<!--- QNE LOGIN --->
<!---
<details closed>
<summary><b>qne login</b></summary>
Used to be logged in to a Quantum Network Explorer instance. If you want to run your experiment remotely, you have to be logged in.
<br></br>

```
qne login [OPTIONS] [HOST]

Arguments:
  [HOST]  [default: https://staging.quantum-network.com/]

Options:
  --username TEXT  Username of the remote user.  [required]
  --password TEXT  Password of the remote user.  [required]
  --help           Show this message and exit.
  
Example:
  qne login username password https://staging.quantum-network.com/
```
</details>
--->

<!--- QNE LOGOUT --->
<!---
<details closed>
<summary><b>qne logout</b></summary>
Log out from a specific Quantum Network Explorer instance.
<br></br>
    
```
qne logout [OPTIONS] [HOST]

Arguments:
  [HOST]  [default: https://staging.quantum-network.com/]

Options:
  --help  Show this message and exit.
  
Example:
  qne logout default: https://staging.quantum-network.com/
```
</details>
--->

<!--- QNE APPLICATION CREATE --->
<details closed>
<summary><b>qne application create</b></summary>
Create a new application in your current directory containing all the files that are needed to write your application. The application directory name will be based on the value given to <b>application</b>. Two child directories <b>src</b> and <b>config</b> will be created, along with the default files.
<br></br>
    
```
qne application create [OPTIONS] APPLICATION NODES...

Arguments:
  APPLICATION  Name of the application  [required]
  NODES...     Names of the nodes to be created  [required]

Options:
  --help  Show this message and exit.
  
Example:
  qne application create application_name node1 node2
```
</details>


<!--- QNE APPLICATION DELETE --->
<!---
<details closed>
<summary><b>qne application delete</b></summary>
Used to delete a remote application. All remote objects and files are deleted. However, the local files will persist.
<br></br>
    
```
qne application delete [OPTIONS]

Options:
  --help  Show this message and exit.

Example:
  qne application delete
```
</details>
--->

<!--- QNE APPLICATION INIT --->
<!---
<details closed>
<summary><b>qne application init</b></summary>
This command can be called in an already existing application, used to initialize it. Any files that adhere to the naming conventions will be detected and moved to the appropriate location.
<br></br>
    
```
qne application init [OPTIONS]

Options:
  --help  Show this message and exit.

Example:
  qne appplication init
```
</details>
--->


<!--- QNE APPLICATION LIST --->
<details closed>
<summary><b>qne application list</b></summary>
Show the list of all applications accessible to this user. If no flags are provided, this entails both remote and local applications are listed.
<br></br>
    
```
qne application list [OPTIONS]

Options:
  --remote / --local  Only list applications from this source.
  --help              Show this message and exit.

Example:
  qne application list
```
</details>



<!--- QNE APPLICATION UPLOAD --->
<!---
<details closed>
<summary><b>qne application upload</b></summary>
This command can be used to create or update a remote application. The command will either create a new application, starting with version 1 or update an already existing application and increment the version number.
<br></br>
    
```
qne application upload [OPTIONS]

Options:
  --help  Show this message and exit.

Example:
  qne application upload
```
</details>
--->


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
Create a new experiment, based on either a local or a remote application name.
<br></br>
    
```
qne experiment create [OPTIONS] NAME APPLICATION NETWORK

Arguments:
  NAME         Name of the experiment.  [required]
  APPLICATION  Name of the application.  [required]
  NETWORK      Name of the network to be used. [required]

Options:
  --local / --remote  Run the application locally.  [default: True]
  --help              Show this message and exit.
  
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
Delete the entire experiment, both on the local and remote side.
<br></br>
    
```
qne experiment delete [OPTIONS]

Options:
  --help  Show this message and exit.
  
Example:
  qne experiment delete
```
</details>



<!--- QNE EXPERIMENT LIST --->
<!---
<details closed>
<summary><b>qne experiment list</b></summary>
List all the remote applications.
<br></br>
    
```
qne experiment list [OPTIONS]

Options:
  --help  Show this message and exit.
  
Example:
  qne experiment list
```
</details>
--->



<details closed>
<!--- QNE EXPERIMENT RUN --->
<summary><b>qne experiment run</b></summary>
Using this command the experiment will be run on the backend. In case of a local run, netsquid will be used as backend simulator. 
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
More documentation about these commands and about the files that are generated can be found in the QNE-ADK user guide on the Quantum Network Explorer [website](https://beta.quantum-network.com/knowledge-base/qne-adk).
