# Tutorial 2 - Create model and run simulations
In this tutorial, we will learn how to load a pre-existing language, create a model and run simulations on the generated attack graph. It is recommended to follow [tutorial 1](https://github.com/mal-lang/mal-tutorials/tree/main/tutorials/tutorial1) before this one.

## Step by step
### Environment set-up
Create a directory for the tutorial:

`mkdir mal-tutorial2 && cd mal-tutorial2`

We will use **tyrLang** as the mal-lang. Download it from Github and put tyrLang in the working directory:

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

### mal-lang: tyrLang
[tyrLang](https://github.com/mal-lang/tyrLang) is a mal-lang created by MAL developers. It is derived from another mal-lang called [coreLang](https://github.com/mal-lang/coreLang), which is very general and large language intended for common use cases within the IT domain. tyrLang is a simpler version of coreLang. For this tutorial, we will use certain parts of tyrLang.

- `Network`, `InternetworkConnectionRule` and `ConnectionRule` assets, and `interNetConnections`, `appConnections` and `netConnections` association: can be found in tyrLang's `src/main/mal/Networking.mal` file.
- `Application` asset in `src/main/mal/DataResources.mal` file.
- `SoftwareVulnerability` asset, and `application` association in `src/main/mal/Vulnerability.mal` file.
- `Data` asset, and `containingApp` association in `src/main/mal/DataResources.mal` file.
- `Identity` and `Credentials` assets, and `execPrivApps` and `identities` associations in `src/main/mal/IAM.mal` file.

### Helper Functions

Create a python file in the directory called `tutorial2_utils.py` with the text editor of choice.

Copy this piece of code into `tutorial2_utils.py`:

```python
from maltoolbox.model import Model, ModelAsset

def connect_net_to_net(model: Model, net1: ModelAsset, net2: ModelAsset):
    """
    Create a connection rule (name of the asset) between net1 and net 2 and return it.
    """
    cr_asset_name = f"ConnectionRule {net1.name} {net2.name}"
    cr_asset = model.add_asset("InternetworkConnectionRule", cr_asset_name)
    net1.add_associated_assets("interNetConnections", {cr_asset})
    net2.add_associated_assets("interNetConnections", {cr_asset})
    return cr_asset


def connect_app_to_net(model: Model, app: ModelAsset, net: ModelAsset) -> ModelAsset:
    """
    Create a connection rule (name of the asset) between app and net and return it.
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

These helper functions are made to simplify the creation of the model. If you have followed the tutorials in order, you will see that the functions inside the helper functions (`add_asset`, `add_associated_assets`) were used in [tutorial 1](https://github.com/mal-lang/mal-tutorials/tree/main/tutorials/tutorial1). 

Each function creates assets in a model and connects the assets to other assets using associations; association fieldnames to be more exact.

### Model Creation

Let's create a model and use the helper functions. First, create a file called `tutorial2_model.py` and add this:

```python
from maltoolbox.model import Model
from maltoolbox.language import LanguageGraph
from tutorial2_utils import connect_net_to_net, connect_app_to_net, add_vulnerability_to_app, add_data_to_app, add_user_to_app, add_creds_to_user

def create_model(lang_graph: LanguageGraph) -> Model:
    model = Model("my-model", lang_graph)

    net_a = model.add_asset("Network", "NetworkA")
    net_b = model.add_asset("Network", "NetworkB")

    connect_net_to_net(model, net_a, net_b)

    app1 = model.add_asset("Application", "App1")
    connect_app_to_net(model, app1, net_a)
    app2 = model.add_asset("Application", "App2")
    connect_app_to_net(model, app2, net_a)
    app3 = model.add_asset("Application", "App3")
    connect_app_to_net(model, app3, net_b)
    app4 = model.add_asset("Application", "App4")
    connect_app_to_net(model, app4, net_b)

    add_vulnerability_to_app(model, app4)

    add_data_to_app(model, app4, "DataOnApp4")

    user_on_app_3 = add_user_to_app(model, app3, "UserOnApp3")

    add_creds_to_user(model, user_on_app_3, "User3Creds")

    return model
```

In this simple function, we create:
- Two instances of our `Network` asset (`NetworkA` and `NetworkB`). We connect them using our `connect_net_to_net` helper function, which uses a `InternetworkConnectionRule` asset and a `interNetConnections` association.
- Four instances of our `Application` asset (`App1`, `App2`, `App3` and `App4`). Using our `connect_app_to_net` helper function, we connect them to our two networks using the `ConnectionRule` asset, and `appConnections` and `netConnections` associations:
    - `App1` and `App2` are connected to `NetworkA`.
    - `App3` and `App4` are connected to `NetworkB`.
- Add a vulnerability to `App4` using our `add_vulnerability_to_app` helper function, which uses a `SoftwareVulnerability` asset and an `application` association.
- Add data (`DataOnApp4`) to `App4` using our `add_data_to_app` helper function, which uses a `Data` asset and a `containingApp` association.
- Add a user (`UserOnApp3`) to `App3` using our `add_user_to_app` helper function, which uses an `Identity` asset and an `execPrivApps` association.
- Add credentials (`User3Creds`) to `UserOnApp3` using our `add_creds_to_user` helper function, which uses an `Credentials` asset and an `identities` association.

To instantiate the model, we will create another file called `tutorial2_simulation.py`. This model will work as our main file and we will later learn about mal-simulator in it. Add this to the `tutorial2_simulation.py` file:

```python
import os
from maltoolbox.language import LanguageGraph
from tutorial2_model import create_model

def main():
    lang_file = "/path/to/tyrLang/main.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    tyr_lang = LanguageGraph.load_from_file(lang_file_path)

    model = create_model(tyr_lang)

if __name__ == "__main__":
    main()
```

You can verify whether everything we have done up until this point is correct by running `python tutorial2_simulation.py`. If you don't see any output, the work is correct so far.

### Model & Attack Graph Rendering
In this section, we will visualize our model and its corresponding attack graphs.

First, we need to create our attack graph in order to visualize it. In [tutorial 1](https://github.com/mal-lang/mal-tutorials/tree/main/tutorials/tutorial1), we went over them. Add this import `from maltoolbox.attackgraph import AttackGraph` to the other imports and add this line `attack_graph = AttackGraph(tyr_lang, model)` after the `create_model` one.

For the next steps we need the tool **Graphviz**. If you are not familiar, you may find more information about it in the following link: [How to download & install Graphviz](https://github.com/mal-lang/mal-toolbox?tab=readme-ov-file#requirements). You can see other visualization options [here](https://github.com/mal-lang/mal-toolbox/wiki/visualization).

#### Model visualization
Once Graphviz is installed, add these imports `from maltoolbox.visualization.graphviz_utils import render_model, render_attack_graph` to the other imports and add this line `render_model(model)` after the `attack_graph` one. Run the file with `python tutorial2_simulation.py` to see a render of the model. This can be helpful to debug generated models. We also have a specific tool for visualizing and creating MAL models covered in [this tutorial](https://github.com/mal-lang/mal-tutorials/blob/main/tutorials/tutorial3/mal-gui-tutorial.md).

`render_model` generates a `.gv` file, a plain text file written in the DOT graph description language, primarely used by Graphviz. This file is not human-friendly, so the function also outputs its corresponding `.pdf` file. In the PDF's graph, the assets/associations of the same type have the same color (chosen randomly). You can see the files in this tutorial's folder.

#### Attack Graph visualization
For the attack graph, add this line `render_attack_graph(attack_graph)` after the `render_model` one. The attack graph contains all the attack steps and their relations in the model according to the definition in the MAL language, **tyrLang** in our case. Conceptually this represents the full blueprint of all possible attacks steps and attack paths possible in the model. As seen from the render, we see that even small models in simple languages easily become difficult to overview. Therefore, we typically would like to apply some form of analysis mechanism on the attack graph.

`render_attack_graph` also generates a `.gv` file and a `.pdf` file from it. The nodes color follow the same rules as the model graph. Additionally, in this one we have the nodes' edge colors, blue for defense steps and red for attack steps.

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
