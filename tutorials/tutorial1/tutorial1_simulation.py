import os
from maltoolbox.language import LanguageGraph
from tutorial1_model import create_model
from maltoolbox.attackgraph import AttackGraph

from malsim import MalSimulator, run_simulation, AttackerSettings, DefenderSettings
from malsim.policies import RandomAgent


def main():
    lang_file = "./exampleLang.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    example_lang = LanguageGraph.load_from_file(lang_file_path)

    # Create our example model
    model = create_model(example_lang)
    print("Model created successfully!")
    print(model)
    # Generate an attack graph from the model
    graph = AttackGraph(example_lang, model)
    print("Attack graph generated successfully!")


    # FIRST SIMULATION (NO AGENTS)
    #simulator = MalSimulator(graph, [])
    #path = run_simulation(simulator)

    # SECOND SIMULATION (WITH AGENTS)
    
    # Create agent settings
    agent_settings = [
        AttackerSettings(
            "Attacker1",
            entry_points={"Machine1:compromise"},
            goals={"Machine2:compromise"},
            policy=RandomAgent
        ),
        DefenderSettings(
            "Defender1",
            policy=RandomAgent
        )
    ]

    simulator = MalSimulator(graph, agents=agent_settings)
    run_simulation(simulator)

    import pprint
    pprint.pprint(simulator.recording)
    
if __name__ == "__main__":
    main()
