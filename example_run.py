from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from pprint import pprint

from vtms_v1 import SimulationRunner, canonical_scenarios

runner = SimulationRunner()
scenario = canonical_scenarios()["S-01"]
result = runner.run(scenario)

print("Final state")
pprint(result.final_point())
print("\nEnergy balance")
pprint(result.energy_balance)
print("\nWarnings")
pprint(result.warnings)
