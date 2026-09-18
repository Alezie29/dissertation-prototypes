import sys
from strategies.prediction import ClientSidePrediction
from strategies.rollback import RollbackNetcode

STRATEGY_MAP = {
    "prediction": ClientSidePrediction,
    "rollback": RollbackNetcode,
}
if len(sys.argv) < 2:
    print("No valid strategy was used, please use this format: python3 -m client.main <strategy_name>")
    print("Please use one of the available strategies below: ", list(STRATEGY_MAP.keys())) # Print error message for typos or invalid strategy inputted
    sys.exit(1) # Cleanly exit instead of raw and confusing traceback
strategy_name = sys.argv[1]

if strategy_name not in STRATEGY_MAP:
    print("Invalid straetgy name, please double check for typos!")
    sys.exit(1)
strategy_class = STRATEGY_MAP[strategy_name]
strategy = strategy_class()
