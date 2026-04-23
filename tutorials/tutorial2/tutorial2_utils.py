import os

from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model, ModelAsset

from maltoolbox.visualization.graphviz_utils import render_model

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