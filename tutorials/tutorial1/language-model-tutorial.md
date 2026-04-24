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
To define a ***mal-lang***, create a file in the same directory called `exampleLang.mal` and copy the following code into it:

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
Create a python file in the same directory called `tutorial1_model.py`.

Copy this code into `tutorial1_model.py`:

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

    credentials_for_machine_2.defenses = {'encrypted': 1.0}

    return model
```

In this simple function, we create:
- Two instances of our `Machine` asset (`Machine1` and `Machine2`), one instance of the `Network` asset (`OfficeNet`), and one of instance of the `Credentials` asset (`CredentialsForM2`).
- A connection between `Machine1`, `Machine2` and `OfficeNet`. The string `"parties"` comes from the `Communication` association in the MAL language we created.
- A connection between `Machine1` and `CredentialsForM2`. The string `"storesCreds"` comes from the `Storage` association. 
- A connection between `Machine2` and `CredentialsForM2`. The string `"authCreds"` comes from the `Access` association. 
- The `credentials_for_machine_2.defenses = {'encrypted': 1.0}` activate the defense `encrypted` step in the `Credentials` asset. The `1.0` means the defense step is activated. If you don't wish to activate the defense, you can comment this line.

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

By executing this code, we create a model using a language graph, which in turn has been defined using our MAL-Lang (*exampleLang.mal* --> *LanguageGraph* --> *Model*) . To do so, run the script with `python tutorial1_simulation.py`. The **expected result** from this should be a terminal with no errors. This is the Windows result, but the rest of OSs must be similar:
```bash
(.venv) C:\\mal-tutorials\tutorials\tutorial1>c:mal-tutorials\tutorials\tutorial1\.venv\Scripts\python.exe c:/mal-tutorials/tutorials/tutorial1/tutorial1_simulation.py
```

You can see the final version of `tutorial1_model.py` [here](https://github.com/mal-lang/mal-tutorials/blob/main/tutorials/tutorial1/tutorial1_model.py).

### Create an Attack Graph
To create an attack graph, we use the **model** and **exampleLang**. Add this import to the top of the `tutorial1_simulation.py` file:

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

The attack graph is a representation of the model that folds out all of the attack steps defined in the MAL language, in this case, exampleLang. This can be used to run analysis or simulations. We will learn how to visualize models and attack graphs in [tutorial 2](https://github.com/mal-lang/mal-tutorials/tree/main/tutorials/tutorial2).

If you would like to know more about the concepts ***LanguageGraph***, ***Model*** or ***AttackGraph***, [visit this Wiki](https://github.com/mal-lang/mal-toolbox/wiki/MAL-Toolbox-concepts).

### Run simulation
To run simulations, add these imports to the top of the `tutorial1_simulation.py` file:

```python
from malsim import MalSimulator, run_simulation, AttackerSettings
from malsim.types import AgentSettings
from malsim.policies import RandomAgent
```

Now we can create a `MalSimulator` object from the attack graph `graph` and run simulations.

Add this to the end of the `main` function:

```python
simulator = MalSimulator(graph)
path = run_simulation(simulator, {})
```

When we run `python tutorial1_simulation.py` we will just see "Simulation over after 0 steps.". This is because we don't have any agents. Let us add an attacker agent.

#### Add an attacker

To do so, replace the previous code with:

```python
# Create agent settings
agent_settings: AgentSettings = {
    "Attacker1": AttackerSettings(
        "Attacker1",
        entry_points={"Machine1:compromise"},
        goals={"Machine2:compromise"},
        policy=RandomAgent
    )
}
simulator = MalSimulator(graph, agent_settings=agent_settings)
run_simulation(simulator, agent_settings)

import pprint
pprint.pprint(simulator.recording)
```

In this section, we define the `AttackerSettings` object:
- `Attacker1`: the name we give to the attacker agent.
- `entry_points`: the node where we make the attacker start. An attacker can have more than one `entry_point`.
- `goals`: the node or nodes that we want the attacker to reach. This is an optional parameter. The simulation is done when the goals are reached, or when all possible nodes are reached if no goal is set.
- `policy`: tells the `run_simulation` function which policy (policies can be found in [malsim.policies](https://github.com/mal-lang/mal-simulator/tree/main/malsim/policies)).

This registers an attacker in the simulator, gives a dict of agents to `run_simulation` which will use the policy set in the AttackerSettings object. We then print the recording of the simulation.

You should see something like the following code box in your terminal after running `python tutorial1_simulation.py`. You won't see an exact copy of the expected results because the attack path, in this case, is not deterministic. Simulations can be deterministic if we gave a seed to the simulator.

```bash
Iteration 0
---
Iteration 1
---
...
Iteration 9
---
Simulation over after 10 steps.
Total reward "Attacker1" 0.0
defaultdict(<class 'dict'>,
Total reward "Attacker1" 0.0
defaultdict(<class 'dict'>,
            {1: {'Attacker1': [AttackGraphNode(name: "OfficeNet:communicate", id: 0, type: or)]},
             2: {'Attacker1': [AttackGraphNode(name: "Machine1:connect", id: 1, type: or)]},
             3: {'Attacker1': [AttackGraphNode(name: "Machine2:connect", id: 5, type: or)]},
             4: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:access", id: 9, type: or)]},
             5: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:crack", id: 11, type: or)]},
             6: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:use", id: 12, type: or)]},
             7: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:useUnencrypted", id: 10, type: and)]},
             8: {'Attacker1': [AttackGraphNode(name: "Machine2:authenticate", id: 6, type: or)]},
             9: {'Attacker1': [AttackGraphNode(name: "Machine2:authCompromise", id: 7, type: and)]},
             10: {'Attacker1': [AttackGraphNode(name: "Machine2:compromise", id: 8, type: or)]}})

(.venv) C:\\mal-tutorials\tutorials\tutorial1>
Total reward "Attacker1" 0.0
defaultdict(<class 'dict'>,
            {1: {'Attacker1': [AttackGraphNode(name: "OfficeNet:communicate", id: 0, type: or)]},
             2: {'Attacker1': [AttackGraphNode(name: "Machine1:connect", id: 1, type: or)]},
             3: {'Attacker1': [AttackGraphNode(name: "Machine2:connect", id: 5, type: or)]},
             4: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:access", id: 9, type: or)]},
             5: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:crack", id: 11, type: or)]},
             6: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:use", id: 12, type: or)]},
             7: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:useUnencrypted", id: 10, type: and)]},
             8: {'Attacker1': [AttackGraphNode(name: "Machine2:authenticate", id: 6, type: or)]},
             9: {'Attacker1': [AttackGraphNode(name: "Machine2:authCompromise", id: 7, type: and)]},
             10: {'Attacker1': [AttackGraphNode(name: "Machine2:compromise", id: 8, type: or)]}})
Total reward "Attacker1" 0.0
defaultdict(<class 'dict'>,
            {1: {'Attacker1': [AttackGraphNode(name: "OfficeNet:communicate", id: 0, type: or)]},
             2: {'Attacker1': [AttackGraphNode(name: "Machine1:connect", id: 1, type: or)]},
             3: {'Attacker1': [AttackGraphNode(name: "Machine2:connect", id: 5, type: or)]},
             4: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:access", id: 9, type: or)]},
Total reward "Attacker1" 0.0
defaultdict(<class 'dict'>,
            {1: {'Attacker1': [AttackGraphNode(name: "OfficeNet:communicate", id: 0, type: or)]},
             2: {'Attacker1': [AttackGraphNode(name: "Machine1:connect", id: 1, type: or)]},
             3: {'Attacker1': [AttackGraphNode(name: "Machine2:connect", id: 5, type: or)]},
             4: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:access", id: 9, type: or)]},
             5: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:crack", id: 11, type: or)]},
             6: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:use", id: 12, type: or)]},
             7: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:useUnencrypted", id: 10, type: and)]},
             8: {'Attacker1': [AttackGraphNode(name: "Machine2:authenticate", id: 6, type: or)]},
             9: {'Attacker1': [AttackGraphNode(name: "Machine2:authCompromise", id: 7, type: and)]},
             10: {'Attacker1': [AttackGraphNode(name: "Machine2:compromise", id: 8, type: or)]}})
```

#### Add a defender
The first step will be to comment line 17 `# credentials_for_machine_2.defenses = {'encrypted': 1.0}` in the `tutorial1_model.py` file. We do this so that the defender can use this defense step. If it is already activated, the defender won't be able to activate it during the simulation.

Now, we add a defender to the current `agent_settings`:
```python
agent_settings: AgentSettings = {
    "Attacker1": AttackerSettings(
        "Attacker1",
        entry_points={"Machine1:compromise"},
        goals={"Machine2:compromise"},
        policy=RandomAgent
    ),
    "Defender1": DefenderSettings(
        "Defender1",
        policy=RandomAgent
    )
}
```
In this section, we define the `DefenderSettings` object:
- `Defender1`: the name we give to the defender agent.
- `policy`: The same policies are shared between attackers and defenders (policies can be found in [malsim.policies](https://github.com/mal-lang/mal-simulator/tree/main/malsim/policies)).

Run the simulation again `python tutorial1_simulation.py` and you will see something similar to the codebox below. 

```bash
Iteration 0
---
Iteration 1
---
...
Iteration 9
---
Total reward "Attacker1" 0.0
Total reward "Defender1" 0.0
defaultdict(<class 'dict'>,
            {1: {'Attacker1': [AttackGraphNode(name: "OfficeNet:communicate", id: 0, type: or)],
                 'Defender1': [AttackGraphNode(name: "CredentialsForM2:encrypted", id: 13, type: defense)]},
             2: {'Attacker1': [AttackGraphNode(name: "Machine2:connect", id: 5, type: or)],
                 'Defender1': []},
             3: {'Attacker1': [AttackGraphNode(name: "Machine1:connect", id: 1, type: or)],
                 'Defender1': []},
             4: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:access", id: 9, type: or)],
                 'Defender1': []},
             5: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:crack", id: 11, type: or)],
                 'Defender1': []},
             6: {'Attacker1': [AttackGraphNode(name: "CredentialsForM2:use", id: 12, type: or)],
                 'Defender1': []},
             7: {'Attacker1': [AttackGraphNode(name: "Machine2:authenticate", id: 6, type: or)],
                 'Defender1': []},
             8: {'Attacker1': [AttackGraphNode(name: "Machine2:authCompromise", id: 7, type: and)],
                 'Defender1': []},
             9: {'Attacker1': [AttackGraphNode(name: "Machine2:compromise", id: 8, type: or)],
                 'Defender1': []}})
```

As we can see, the defender uses the `encrypted` defense step, but the attacker still reaches its goal.

You can see the final version of `tutorial1_simulation.py` [here](https://github.com/mal-lang/mal-tutorials/blob/main/tutorials/tutorial1/tutorial1_simulation.py).

This tutorial has shown how to build a mal-lang, a model, an language graph, an attack graph and run a simulation. [Tutorial 2](https://github.com/mal-lang/mal-tutorials/tree/main/tutorials/tutorial2) will cover model-building from a given mal-lang, visualize an attack graph and give further insights on simulations.
