import os

from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model, ModelAsset
from maltoolbox.attackgraph import AttackGraph
from maltoolbox.visualization.graphviz_utils import render_model, render_attack_graph

from malsim.mal_simulator import MalSimulator, run_simulation
from malsim.config import AttackerSettings, DefenderSettings, MalSimulatorSettings, TTCMode
from malsim.policies import RandomAgent, TTCSoftMinAttacker, PassiveAgent

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


def add_creds_to_user(
    model: Model, identity: ModelAsset, data_asset_name: str
) -> ModelAsset:
    """
    Add a credentials asset and association from `identity` to the credentials.
    return the credentials asset.
    """
    creds_asset = model.add_asset("Credentials", data_asset_name)
    creds_asset.add_associated_assets("identities", {identity})
    return creds_asset


def create_model(lang_graph: LanguageGraph) -> Model:
    # Create a model with 4 apps
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
    agent_settings = {
        "MyAttacker": AttackerSettings(
            "MyAttacker",
            entry_points={"App 1:fullAccess"},
            goals={"DataOnApp4:read"},
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


if __name__ == "__main__":
    main()
