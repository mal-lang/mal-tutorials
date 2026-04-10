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

    #credentials_for_machine_2.defenses = {'encrypted': 1.0}

    return model