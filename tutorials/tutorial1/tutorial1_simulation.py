import os
from maltoolbox.language import LanguageGraph
from maltoolbox.attackgraph import AttackGraph
from tutorial1_model import create_model

def main():
    lang_file = "exampleLang.mal"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(current_dir, lang_file)
    example_lang = LanguageGraph.load_from_file(lang_file_path)

    # Create our example model
    model = create_model(example_lang)

    # Generate an attack graph from the model
    graph = AttackGraph(example_lang, model)


if __name__ == "__main__":
    main()