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
To define a MAL-Language or ***MAL-Lang***, create a file in the same directory called `my-language.mal` and copy the following code into it:

```
#id: "org.mal-lang.my-language"
#version: "1.0.0"

category System {
    asset Computer {
        | connect
            -> access
        | crackPassword [HardAndCertain]
            -> access
        & access
            -> compromise
	    | compromise
            -> folder.accessFolder,
               toComputer.connect,
               toComputer.crackPassword
    }
    asset Folder {
        | accessFolder
            -> stealSecrets
        | stealSecrets
    }
}

associations {
    Computer [fromComputer] * <-- ComputerConnection --> * [toComputer] Computer
    Computer [computer] * <-- ComputerFolderConnection --> * [folder] Folder
}
```

This piece of code defines a simple example of MAL-Language. We define a category called System that holds two assets:
- Computer
    - If steps `connect` and `crackPassword` happen, then `access` would be triggered, which at the same time would trigger `compromise`.
    - If `compromise` is activated, we would move to the step `accessFolder` in asset `Folder`.
- Folder
    - If `accessFolder` is given, it would trigger `stealSecrets`.

In the `associations` section we define the relationship assets have. In this case, `Computer` and `Folder` have an N to M relationship, represented by the `*`.

Once we have the MAL-Lang file, we can create a python script to automate the creation of *Language Graphs* and *Models* based on this MAL-language. To get a deeper insight into the **MAL languages syntaxis**, [visit the MAL Documentation repository](https://github.com/mal-lang/mal-documentation/wiki/1.-MAL-Syntax)

### Creation of Models and Language Graphs
Create a .py file in the same directory called `tutorial1.py`.

Copy this code into `tutorial1.py`:

```python
import os
from maltoolbox.model import Model
from maltoolbox.language import LanguageGraph


def create_model(lang_graph: LanguageGraph) -> Model:
    """Create a model with 2 computers"""
    model = Model("my-model", lang_graph)

    # Two computers
    comp_a = model.add_asset("Computer", "ComputerA")
    comp_b = model.add_asset("Computer", "ComputerB")

    # Connection between computers
    comp_a.add_associated_assets("toComputer", {comp_b})

    # Two folders
    folder1 = model.add_asset("Folder", "FolderA")
    folder2 = model.add_asset("Folder", "FolderB")

    # Connect the folders to the computers
    comp_b.add_associated_assets("folder", {folder2})
    comp_a.add_associated_assets("folder", {folder1})

    return model
```
In this simple function, we create:
- Two instances of our `Computer` asset (`ComputerA` and `ComputerB`) and our `Folder` asset (`FolderA` and `FolderB`).
- A connection between `ComputerA` and `ComputerB`. The string `"computer2"` comes from the `ComputerConnection` association in the MAL language we created. 
- Two connections between the computer and folder instances. The strings `"folder"` come from the `ComputerFolderConnection` association.

Now we can instantiate the model. Add this to the end of the file:

```python
def main():
    lang_file = "my-language.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    my_language = LanguageGraph.load_from_file(lang_file_path)

    # Create our example model
    model = create_model(my_language)


if __name__ == "__main__":
    main()
```
By executing this code, we create a model using a language graph, which in turn has been defined using our MAL-Lang "my-language.mal" (*my-language.mal* --> *LanguageGraph* --> *model*) . To do so, run the script with `python tutorial1.py`.

### Create an Attack Graph
To create an attack graph, we use the model and the MAL-Lang. Add this import to the top of the file (below the other imports):

```python
from maltoolbox.attackgraph import AttackGraph
```

Put this line after `model = create_model(tyr_lang)`:

```python
# Generate an attack graph from the model
graph = AttackGraph(my_language, model)
```

The attack graph is a representation of the model that folds out all of the attack steps defined in the MAL language. This can be used to run analysis or simulations.

If you would like to know more about the concepts ***LanguageGraph***, ***Model*** or ***AttackGraph***, [visit this Wiki](https://github.com/mal-lang/mal-toolbox/wiki/MAL-Toolbox-concepts)

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
