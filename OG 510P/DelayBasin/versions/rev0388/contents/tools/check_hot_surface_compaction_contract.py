import pathlib

from hot_surface_compaction_lib import verify_compaction_receipt

ROOT = pathlib.Path(__file__).resolve().parents[1]
verify_compaction_receipt(ROOT)
print("check_hot_surface_compaction_contract: OK")
