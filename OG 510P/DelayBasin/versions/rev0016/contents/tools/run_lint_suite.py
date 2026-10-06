import pathlib
import runpy
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
tools = [
    "check_discovery.py",
    "check_registry_ids.py",
    "check_revision_sync.py",
    "check_prompt_pair_contract.py",
    "check_release_hygiene.py",
    "gen_context_pack.py",
    "check_context_pack_budget.py",
    "check_context_pack_fidelity.py",
    "check_context_pack_contract.py",
    "check_core_lexicon_contract.py",
    "check_move_registry_contract.py",
    "check_promotion_contract.py",
    "check_decay_watch_contract.py",
    "check_recovery_kernel_contract.py",
    "check_revision_receipt_contract.py",
    "check_counterfactual_shadow_contract.py",
]

for tool in tools:
    print(f"== {tool} ==", flush=True)
    try:
        runpy.run_path(str(ROOT / "tools" / tool), run_name="__main__")
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
        if code != 0:
            raise

print("run_lint_suite: OK")
