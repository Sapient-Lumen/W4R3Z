import pathlib

from external_metadata_contract_lib import assert_external_metadata

ROOT = pathlib.Path(__file__).resolve().parents[1]
assert_external_metadata(ROOT)
print("check_external_metadata_contract: OK")
