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