'''
    This file contains the baseline model for tutorial 5. It is used to test the model and the attack graph. It creates a simple model of a company with an internet connection, a DMZ, and an internal
    network. The attacker starts from the internet and tries to read the customer data. The model includes vulnerabilities and credentials that the attacker can exploit to achieve their goal.
    Defenses can be added to the model by adding them as assets and associating them with the relevant assets.
'''
from maltoolbox.language import LanguageGraph
from maltoolbox.model import Model

def create_model(lang: LanguageGraph) -> Model:
    model = Model("the-company", lang)

    # Zones
    internet    = model.add_asset("Network", "Internet")
    dmz         = model.add_asset("Network", "DMZ")
    internalnet = model.add_asset("Network", "InternalNet")

    # Applications
    webapp    = model.add_asset("Application", "WebApp")
    appserver = model.add_asset("Application", "AppServer")
    db        = model.add_asset("Application", "Database")

    # Connection rules
    cr_internet_dmz          = model.add_asset("ConnectionRule", "Internet-to-DMZ")
    cr_dmz_webapp            = model.add_asset("ConnectionRule", "DMZ-to-WebApp")
    cr_dmz_internalnet       = model.add_asset("ConnectionRule", "DMZ-to-InternalNet")
    cr_internalnet_appserver = model.add_asset("ConnectionRule", "InternalNet-to-AppServer")
    cr_internalnet_db        = model.add_asset("ConnectionRule", "InternalNet-to-Database")

    # Attacker goal
    customer_data = model.add_asset("Data", "CustomerData")

    # Associations
    internet.add_associated_assets("netConnections",   {cr_internet_dmz})
    dmz.add_associated_assets("netConnections",        {cr_internet_dmz})

    dmz.add_associated_assets("netConnections",    {cr_dmz_webapp})
    webapp.add_associated_assets("appConnections", {cr_dmz_webapp})

    dmz.add_associated_assets("netConnections",        {cr_dmz_internalnet})
    internalnet.add_associated_assets("netConnections", {cr_dmz_internalnet})

    internalnet.add_associated_assets("netConnections", {cr_internalnet_appserver})
    appserver.add_associated_assets("appConnections",   {cr_internalnet_appserver})

    internalnet.add_associated_assets("netConnections", {cr_internalnet_db})
    db.add_associated_assets("appConnections",          {cr_internalnet_db})

    customer_data.add_associated_assets("containingApp", {db})

    # Vulnerabilities and credentials
    webapp_rce = model.add_asset("SoftwareVulnerability", "WebAppRCE")
    webapp_rce.add_associated_assets("application", {webapp})

    dbadmin_id    = model.add_asset("Identity",    "DBAdminIdentity")
    dbadmin_creds = model.add_asset("Credentials", "DBAdminCreds")

    dbadmin_id.add_associated_assets("highPrivApps", {db})
    dbadmin_creds.add_associated_assets("identities",   {dbadmin_id})

    webapp_config = model.add_asset("Data", "WebAppConfig")
    webapp.add_associated_assets("containedData",        {webapp_config})
    webapp_config.add_associated_assets("information",   {dbadmin_creds})

    return model