# Tutorial 2 - Create model and run simulations
In this tutorial, we will learn how to load a pre-existing language, create a model and run simulations on the generated attack graph.

## Step by step
### Environment set-up
Create a directory for the tutorial:

`mkdir mal-tutorial2 && cd mal-tutorial2`

Download tyrLang from github and put tyrLang in the directory:

`git clone https://github.com/mal-lang/tyrLang.git`

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

### Helper Functions

Create a python file in the directory called `tutorial2.py` with the text editor of choice.

Copy this piece of code into `tutorial2.py`:

```python

import os

from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model, ModelAsset

from maltoolbox.visualization.graphviz_utils import render_model

def connect_net_to_net(model: Model, net1: ModelAsset, net2: ModelAsset):
    """
    Create a connection rule between net1 and net 2 and return it.
    """
    cr_asset_name = f"ConnectionRule {net1.name} {net2.name}"
    cr_asset = model.add_asset("InternetworkConnectionRule", cr_asset_name)
    net1.add_associated_assets("interNetConnections", {cr_asset})
    net2.add_associated_assets("interNetConnections", {cr_asset})
    return cr_asset


def connect_app_to_net(model: Model, app: ModelAsset, net: ModelAsset) -> ModelAsset:
    """
    Create a connection rule between app and net and return it.
    """
    cr_asset_name = f"ConnectionRule {app.name} {net.name}"
    cr_asset = model.add_asset("ConnectionRule", cr_asset_name)
    app.add_associated_assets("appConnections", {cr_asset})
    net.add_associated_assets("netConnections", {cr_asset})
    return cr_asset


def add_vulnerability_to_app(model: Model, app: ModelAsset) -> ModelAsset:
    """
    Add vulnerability and association from `app` to the vuln.
    Return the vuln.
    """
    asset_name = f"Vulnerability {app.name}"
    vuln_asset = model.add_asset("SoftwareVulnerability", asset_name)
    vuln_asset.add_associated_assets("application", {app})
    return vuln_asset


def add_data_to_app(model: Model, app: ModelAsset, data_asset_name: str) -> ModelAsset:
    """
    Add a data asset and association from `app` to the data.
    return the data asset.
    """
    data_asset = model.add_asset("Data", data_asset_name)
    data_asset.add_associated_assets("containingApp", {app})
    return data_asset

def add_user_to_app(model: Model, app: ModelAsset, data_asset_name: str) -> ModelAsset:
    """
    Add a user asset and association from `app` to the user.
    return the user asset.
    """
    user_asset = model.add_asset("Identity", data_asset_name)
    user_asset.add_associated_assets("execPrivApps", {app})
    return user_asset

def add_creds_to_user(model: Model, identity: ModelAsset, data_asset_name: str) -> ModelAsset:
    """
    Add a credentials asset and association from `identity` to the credentials.
    return the credentials asset.
    """
    creds_asset = model.add_asset("Credentials", data_asset_name)
    creds_asset.add_associated_assets("identities", {identity})
    return creds_asset

```

These helper functions are made to work with the MAL language tyrLang, association fieldnames and asset types are specific per language. Therefore, they would need to be adapted depending on the MAL language in use.

Each function creates assets in a model and connects the assets to other assets using associations (associatoin fieldnames to be more exact).

### Model Creation

Let's create a model and use the helper functions. First, add these imports to the others at the beginning of the python file:

```python
from maltoolbox.attackgraph import AttackGraph
from maltoolbox.visualization.graphviz_utils import render_model, render_attack_graph
```

Then, add this to the end of the file:

```python
def create_model(lang_graph: LanguageGraph) -> Model:
    """Create a model with 4 apps"""
    model = Model("my-model", lang_graph)

    # Two networks
    net_a = model.add_asset("Network", "NetworkA")
    net_b = model.add_asset("Network", "NetworkB")
    # Connection between networks
    connect_net_to_net(model, net_a, net_b)

    # Four apps with connections to networks
    app1 = model.add_asset("Application", "App 1")
    connect_app_to_net(model, app1, net_a)
    app2 = model.add_asset("Application", "App 2")
    connect_app_to_net(model, app2, net_a)
    app3 = model.add_asset("Application", "App 3")
    connect_app_to_net(model, app3, net_b)
    app4 = model.add_asset("Application", "App 4")
    connect_app_to_net(model, app4, net_b)

    # Add a vulnerability to app4
    add_vulnerability_to_app(model, app4)

    # Add data to app4
    add_data_to_app(model, app4, "DataOnApp4")

    # Add user to app3
    user_on_app_3 = add_user_to_app(model, app3, "UserOnApp3")

    # Add user to app3
    add_creds_to_user(model, user_on_app_3, "User3Creds")

    return model


def main():
    lang_file = "tyrLang/src/main/mal/main.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    tyr_lang = LanguageGraph.load_from_file(lang_file_path)

    # Create our example model
    model = create_model(tyr_lang)

    # Generate an attack graph from the model
    graph = AttackGraph(tyr_lang, model)

    # render_model(model) # Uncomment to render graphviz pdf
    # render_attack_graph(graph) # Uncomment to render graphviz pdf

if __name__ == '__main__':
    main()
```

### Model & Attack Graph Rendering

For the next steps we need the tool **Graphviz**. If you do not have already installed it you might find more information about it in the following link: [How to download & install Graphviz](https://github.com/mal-lang/mal-toolbox?tab=readme-ov-file#requirements). 

Once Graphviz is installed, uncomment the line with 'render_model' and run the file with `python tutorial2.py` to see a [render](my-model.gv.pdf) of the model. This can be helpful to debug generated models. We also have a specific tool for visualizing and creating MAL models covered in [this tutorial](https://github.com/mal-lang/mal-tutorials/blob/main/tutorials/tutorial3/mal-gui-tutorial.md).

Then try it with the other line (render_graph) to see a [render](my-attack-graph.gv.pdf) of the attack graph. The attack graph contains all the attack steps and their relations in the model according to the definition in the MAL language, tyrLang in our case. Conceptually this represents the full blueprint of all possible attacks steps and attack paths possible in the model. As seen from the render, we see that even small models in simple languages easily become difficult to overview. Therefore, we typically would like to apply some form of analysis mechanism on the attack graph. 

In the next section, we will use the `mal-simulator` to run simulations with different agents. In these simulations the agents steps through the full attack graph and produces a (typically partial) graph traversal path, conceptually mimicking the activity of red team penetration tests in the modeled system environment. 

### Run Simulations

To run simulations, add these imports to the top of the file (below the other imports):

```python
from malsim.mal_simulator import MalSimulator, run_simulation
from malsim.config import AttackerSettings, DefenderSettings, MalSimulatorSettings, TTCMode
from malsim.policies import RandomAgent, TTCSoftMinAttacker, PassiveAgent
```

Now we can create a MalSimulator from the attack graph and run simulations.

Add this to the end of the `main` function:

```python

simulator = MalSimulator(graph)
path = run_simulation(simulator, {})

```

When we run `python tutorial2.py` now we will just see "Simulation over after 0 steps.". This is because we don't have any agents. Let us add an attacker agent.

Replace the above code with:

```python
    agent_settings = {
        "MyAttacker": AttackerSettings(
            "MyAttacker",
            entry_points={"App 1:fullAccess"},
            goals={'DataOnApp4:read'},
            policy=TTCSoftMinAttacker,
        ),
        "MyDefender": DefenderSettings(
            "MyDefender",
            policy=PassiveAgent,
        )
    }
    simulator = MalSimulator(
        graph,
        agent_settings=agent_settings,
        sim_settings=MalSimulatorSettings(
            ttc_mode=TTCMode.PRE_SAMPLE
        )
    )

    run_simulation(simulator, agent_settings)
    import pprint
    pprint.pprint(simulator.recording)
```

This creates a dict of agents that are used for registering agents and running policies with `run_simulation`. The attacker agent uses a policy which tries to take the easiest node (low TTC) every step and the defender is passive (does nothing).

When we run `python tutorial2.py` now, we can see that the simulation runs until the attacker reaches `DataOnApp4:read`. This tells us that there was a path from `App 1` to `DataOnApp4`.

As we repeat the command, we can see that it reaches it on different iterations, since it is a probabilistic agent.

Try this out with different policies in `malsim.policies`.

`run_simulation` will return the recording of the simulation which can be found also in `simulator.recording`.

See the finished script in [tutorial2.py](tutorial2.py).
