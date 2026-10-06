import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
recovery = pack.get("recovery", {})
if recovery.get("surface") != "docs/20-constitution/recovery-kernel.md":
    raise SystemExit("recovery.surface must be docs/20-constitution/recovery-kernel.md")
if recovery.get("move") != "MV-0010":
    raise SystemExit("recovery.move must be MV-0010")
text = (ROOT / recovery["surface"]).read_text(encoding="utf-8")
for needle in ["Legitimacy predicate", "Kernel surfaces", "Recovery route"]:
    if needle not in text:
        raise SystemExit(f"recovery kernel missing section: {needle}")
print("check_recovery_kernel_contract: OK")
