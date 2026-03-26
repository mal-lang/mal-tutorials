# Tutorial 1 - Create a language and a model
In this tutorial, you will learn how to build a simple MAL language, create a model from it and run simulations.

## Step by step
### Environment Set-up
Create a directory for the tutorial and set it as your working directory: `mkdir mal-tutorial1 && cd mal-tutorial1`
Create a Python virtual environment and activate it.
- On Linux-based operating systems:
```
python -m venv .venv
source .venv/bin/activate
```
- On Windows:
```
python -m venv .venv
.\.venv\Scripts\activate
```
Install the requirements:
```
pip install mal-toolbox
pip install mal-simulator
```

### Definition of a MAL Language
To define a ***MAL-Lang***, create a file in the same directory called `exampleLang.mal` and copy the following code into it:

```
#id: "exampleLang"
#version: "2.0.0"

category System {

    asset Machine {
        | connect
            -> authCompromise

        | authenticate
            -> authCompromise

        & authCompromise
            -> compromise

        | compromise
            -> storesCreds.access,
               networks.communicate
    }

    asset Credentials {
        | access
            -> useUnencrypted,
               crack

        & useUnencrypted
            -> use

        | crack [HardAndCertain]
            -> use

        | use
            -> authenticates.authenticate

        # encrypted
            -> useUnencrypted
    }

    asset Network {
        | communicate
            -> parties.connect
    }
}

associations {
    Machine [parties] * <-- Communication --> * [networks] Network
    Machine [storedOn] 0..1 <-- Storage --> * [storesCreds] Credentials
    Machine [authenticates] 0..1 <-- Access --> * [authCreds] Credentials
}
```

This piece of code defines a simple example of MAL-Language. More specifically, it is [**exampleLang**](https://github.com/mal-lang/exampleLang), a basic MAL language intended to demonstrate the standard structure and essential components of a MAL language. Here is an explanation of the language:

We define a category called System that holds three assets:
- Machine
    - If steps `connect` and `authenticate` happen, then `authCompromise` would be triggered, which at the same time would trigger `compromise`, which would also trigger `access` in the `Credentials` asset and `communicate` in the `Network` asset.
- Credentials
    - If `access` is given, it would trigger `useUnencrypted` and `crack`.
        - `useUnencrypted` would trigger `use`, which then would trigger `authenticate` in the `Machine` asset. This would mean that the attack has succedeed and the attacker has access to the machine.
    - The `crack` step has an ordinal distribution (HardAndCertain). This means that probability for this step to happen is hard and certain. HardAndCertain is defined by the distribution function Exponential(0.1). You can read more about this topic [here](https://github.com/mal-lang/malcompiler/wiki/Supported-distribution-functions).
    - The `encrypted` step is a **defense step**. That is, if the defender activates it, `useEncrypted` will be blocked and, therefore, that path will be as well.
- Network
    - If the `communicate` step is activated, `connect` of the `Machine` asset will be given. This step allows jumping from machine to machine.

In the `associations` section we define the relationship assets have. In this case, we have three relationships:
- `Machine` and `Network` have an N to M relationship, represented by the `*`.
- `Machine` and `Credentials` have two relationships:
    - In the `Storage` sense, they have a 1 to N relationship. A machine can store many credentials (`storesCreds` and `*`) and credentials can only be stored in one machine (`storedOn` and `0..1`).
    - In the `Access` sense, they also have a 1 to N relationship. A machine can be authenticated with many credentials (`authCreds` and `*`) and credentials can only authenticate one machine (`authenticates` and `0..1`).

Once we have the MAL-Lang file, we can create a python script to automate the creation of *Language Graphs* and *Models* based on this MAL-language. Get deeper insight into **MAL syntax**, [visit the MAL specification repository](https://github.com/mal-lang/mal-specification/wiki/MAL-Syntax).

### Creation of Models and Language Graphs
Create a python file in the same directory called `tutorial1-model.py`.

Copy this code into `tutorial1-model.py`:

```python
from maltoolbox.model import Model
from maltoolbox.language import LanguageGraph

def create_model(lang_graph: LanguageGraph) -> Model:
    """Create a model with two machines, one network and one set of credentials"""
    model = Model("my-model", lang_graph)

    office_net = model.add_asset('Network', 'OfficeNet')
    machine_1 = model.add_asset('Machine', 'Machine1')
    machine_2 = model.add_asset('Machine', 'Machine2')
    credentials_for_machine_2 = model.add_asset('Credentials', 'CredentialsForM2')

    office_net.add_associated_assets('parties', {machine_1, machine_2})
    machine_1.add_associated_assets('storesCreds', {credentials_for_machine_2})
    machine_2.add_associated_assets('authCreds', {credentials_for_machine_2})

    return model
```

In this simple function, we create:
- Two instances of our `Machine` asset (`Machine1` and `Machine2`), one instance of the `Network` asset (`OfficeNet`), and one of instance of the `Credentials` asset (`CredentialsForM2`).
- A connection between `Machine1`, `Machine2` and `OfficeNet`. The string `"parties"` comes from the `Communication` association in the MAL language we created.
- A connection between `Machine1` and `CredentialsForM2`. The string `"storesCreds"` comes from the `Storage` association. 
- A connection between `Machine2` and `CredentialsForM2`. The string `"authCreds"` comes from the `Access` association. 

To instantiate the model, we will create another file called `tutorial1_simulation.py`. This model will work as our main file and we will later learn about mal-simulator in it. Add this to the `tutorial1_simulation.py` file:

```python
def main():
    lang_file = "/path/to/exampleLang.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    example_lang = LanguageGraph.load_from_file(lang_file_path)

    # Create our example model
    model = create_model(example_lang)


if __name__ == "__main__":
    main()
```

And add these imports to the beginning of the file:

```python
import os
from maltoolbox.language import LanguageGraph
from tutorial1_model import create_model
```

By executing this code, we create a model using a language graph, which in turn has been defined using our MAL-Lang (*exampleLang.mal* --> *LanguageGraph* --> *Model*) . To do so, run the script with `python tutorial1-simulation.py`. The **expected result** from this should be a terminal with no errors. This is the Windows result, but the rest of OSs must be similar:
```bash
(.venv) C:\\mal-tutorials\tutorials\tutorial1>c:mal-tutorials\tutorials\tutorial1\.venv\Scripts\python.exe c:/mal-tutorials/tutorials/tutorial1tutorial1_simulation.py
```

### Create an Attack Graph
To create an attack graph, we use the **model** and **exampleLang**. Add this import to the top of the `tutorial1-simulation.py` file:

```python
from maltoolbox.attackgraph import AttackGraph
```

Put this line after `model = create_model(example_lang)`:

```python
# Generate an attack graph from the model
graph = AttackGraph(example_lang, model)
```
And add this import to the beginning of the file:

```python
from maltoolbox.attackgraph import AttackGraph
```

The attack graph is a representation of the model that folds out all of the attack steps defined in the MAL language. This can be used to run analysis or simulations.

If you would like to know more about the concepts ***LanguageGraph***, ***Model*** or ***AttackGraph***, [visit this Wiki](https://github.com/mal-lang/mal-toolbox/wiki/MAL-Toolbox-concepts).

### Run simulation
To run simulations, add these imports to the top of the file (below the other imports):

```python
from malsim import MalSimulator, run_simulation, AttackerSettings
from malsim.types import AgentSettings
from malsim.policies import RandomAgent
```

Now we can create a MalSimulator object from the attack graph `graph` and run simulations.

Add this to the end of the `main` function:

```python
simulator = MalSimulator(graph)
path = run_simulation(simulator, {})
```

When we run `python tutorial1.py` we will just see "Simulation over after 0 steps.". This is because we don't have any agents. Let us add an attacker agent.

To do so, replace the previous code (2 lines) with:

```python
# Create agent settings
agent_settings: AgentSettings = {
    "MyAttacker": AttackerSettings(
        "MyAttacker",
        entry_points={"ComputerA:access"},
        goals={"FolderB:stealSecrets"},
        policy=RandomAgent
    )
}
simulator = MalSimulator(graph, agent_settings=agent_settings)
run_simulation(simulator, agent_settings)

import pprint
pprint.pprint(simulator.recording)
```

This registers an attacker in the simulator, gives a dict of agents to `run_simulation` which will use the policy set in the AttackerSettings object. We then print the recording of the simulation.
