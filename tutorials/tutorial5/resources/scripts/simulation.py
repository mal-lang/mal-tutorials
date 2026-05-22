'''
    This file contains the baseline simulation for tutorial 5.
    The simulation uses a depth-first search policy for the attacker.
'''

import os
import pprint
from maltoolbox.language import LanguageGraph
from maltoolbox.attackgraph import AttackGraph
from malsim import MalSimulator, run_simulation, AttackerSettings
from malsim.policies import DepthFirstAttacker

from model import create_model

def main():
    lang_file = "./coreLang/src/main/mal/main.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    coreLang = LanguageGraph.load_from_file(lang_file_path)

    model = create_model(coreLang)
    graph = AttackGraph(coreLang, model)

    attacker = AttackerSettings(
        "Attacker",
        entry_points={"Internet:accessUninspected"},
        goals={"CustomerData:read"},
        policy=DepthFirstAttacker,
    )

    simulator = MalSimulator(graph, agents=[attacker], send_to_api=True)
    run_simulation(simulator)

    pprint.pprint(simulator.recording)

if __name__ == "__main__":
    main()