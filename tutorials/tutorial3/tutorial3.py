from maltoolbox.visualization import render_attack_graph, render_model
from malsim import Scenario, MalSimulator, run_simulation, MalSimulatorSettings
from malsim.config import TTCMode

def main():
    scenario_file = "tutorial3_scenario.yml"
    scenario = Scenario.load_from_file(scenario_file)
    simulator = MalSimulator.from_scenario(
        scenario,
        sim_settings=MalSimulatorSettings(
            ttc_mode=TTCMode.EXPECTED_VALUE,
            # attack_surface_skip_unnecessary=False
        )
    )
    run_simulation(simulator, scenario.agent_settings)
    render_attack_graph(scenario.attack_graph)
    render_model(scenario.model)
    import pprint
    pprint.pprint(simulator.recording)


if __name__ == '__main__':
    main()