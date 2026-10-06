import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from core_method_contract_lib import CoreMethodContractError, validate_core_method_contracts
from core_method_contract_specs import iter_core_method_contract_specs

try:
    message = validate_core_method_contracts(ROOT, list(iter_core_method_contract_specs()))
except CoreMethodContractError as exc:
    raise SystemExit(str(exc)) from exc
print(message)
