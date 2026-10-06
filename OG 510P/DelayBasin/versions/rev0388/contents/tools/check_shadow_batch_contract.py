from shadow_contract_common import SHADOW_CONTRACT_SPECS, run_shadow_contract_batch


if len(SHADOW_CONTRACT_SPECS) != 29:
    raise SystemExit(f"shadow batch expected 29 contracts, found {len(SHADOW_CONTRACT_SPECS)}")

run_shadow_contract_batch()
print("check_shadow_batch_contract: OK")
