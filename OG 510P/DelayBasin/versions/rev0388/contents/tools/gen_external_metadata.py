import pathlib

from external_metadata_contract_lib import write_external_metadata

ROOT = pathlib.Path(__file__).resolve().parents[1]
write_external_metadata(ROOT)
print("wrote external metadata surfaces")
