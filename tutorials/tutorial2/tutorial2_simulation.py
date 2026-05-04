import os
from maltoolbox.language import LanguageGraph
from tutorial2_model import create_model
from maltoolbox.attackgraph import AttackGraph
from maltoolbox.visualization.graphviz_utils import render_model, render_attack_graph

def main():
    lang_file = "/Users/navas/sweden/amanuensis/tyrLang/src/main/mal/main.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    tyr_lang = LanguageGraph.load_from_file(lang_file_path)

    model = create_model(tyr_lang)
    attack_graph = AttackGraph(tyr_lang, model)

    # render_model(model) # Uncomment to render graphviz pdf
    # render_attack_graph(attack_graph) # Uncomment to render graphviz pdf

if __name__ == "__main__":
    main()