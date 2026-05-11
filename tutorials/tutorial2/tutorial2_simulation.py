import os
from tutorial2_model import create_model
from maltoolbox.language import LanguageGraph
from maltoolbox.attackgraph import AttackGraph
from maltoolbox.visualization.graphviz_utils import render_model, render_attack_graph
from malsim.mal_simulator import MalSimulator, run_simulation
from malsim.config import AttackerSettings, DefenderSettings, MalSimulatorSettings, TTCMode
from malsim.policies import RandomAgent, TTCSoftMinAttacker, PassiveAgent

def main():
    lang_file = "/Users/navas/sweden/amanuensis/tyrLang/src/main/mal/main.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    tyr_lang = LanguageGraph.load_from_file(lang_file_path)

    model = create_model(tyr_lang)
    attack_graph = AttackGraph(tyr_lang, model)

    # render_model(model) # Uncomment to render graphviz pdf
    # render_attack_graph(attack_graph) # Uncomment to render graphviz pdf


    agent_settings: AgentSettings = {
        "MyAttacker": AttackerSettings(
            "MyAttacker",
            entry_points={"App1:fullAccess"},
            goals={"DataOnApp4:read"},
            policy=RandomAgent
        )
    }

    simulator = MalSimulator(
        attack_graph,
        agents=agent_settings,
        sim_settings=MalSimulatorSettings(
            ttc_mode=TTCMode.PRE_SAMPLE
        )
    )

    run_simulation(simulator)
    import pprint
    pprint.pprint(simulator.recording)

if __name__ == "__main__":
    main()