import os
from maltoolbox.language import LanguageGraph
from maltoolbox.attackgraph import AttackGraph
from tutorial1_model import create_model
from malsim import MalSimulator, run_simulation, AttackerSettings, DefenderSettings
from malsim.types import AgentSettings
from malsim.policies import RandomAgent

def main():
    lang_file = "exampleLang.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    example_lang = LanguageGraph.load_from_file(lang_file_path)

    # Create our example model
    model = create_model(example_lang)

    # Generate an attack graph from the model
    graph = AttackGraph(example_lang, model)

    # Create agent settings
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
    simulator = MalSimulator(graph, agent_settings=agent_settings)
    run_simulation(simulator, agent_settings)

    import pprint
    pprint.pprint(simulator.recording)


if __name__ == "__main__":
    main()