import pathlib

from release_integrity_contract_lib import ReleaseIntegrityError, validate_release_integrity

ROOT = pathlib.Path(__file__).resolve().parents[1]
try:
    validate_release_integrity(ROOT)
except ReleaseIntegrityError as exc:
    raise SystemExit(str(exc)) from exc
print("check_release_integrity_contract: OK")
