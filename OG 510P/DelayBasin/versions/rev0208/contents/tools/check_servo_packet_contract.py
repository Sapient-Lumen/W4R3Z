import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/servo-packets-receding-horizon-control-and-archive-target-tracking.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG):
    if not path.exists():
        raise SystemExit(f"missing required servo surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Servo packets, receding-horizon control, and archive target-tracking",
    "## Practice / observation",
    "## External pressure from current research",
    "## Working synthesis",
    "## Servo packet vs control authority vs continuation monitor vs stopping packet",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "target continuation property",
    "current error signature or drift symptom",
    "actuator family or editable surface",
    "short horizon or horizon proxy",
    "retune / rollback consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("servo-packet contract missing: " + ", ".join(missing))

traj = TRAJ.read_text(encoding="utf-8")
if "OQ-0078" not in traj or "servo-packet" not in traj:
    raise SystemExit("trajectory map missing servo-packet wiring")

prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0037" not in prompt_text or "target continuation property" not in prompt_text or "current error signature or drift symptom" not in prompt_text:
    raise SystemExit("prompt pairs missing servo-packet ratchet")

runbook = RUNBOOK.read_text(encoding="utf-8")
if "servo packet / receding-horizon control / target-tracking" not in runbook:
    raise SystemExit("runbook missing servo-packet guidance")

if "CL-0078" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0078")
if "INV-0076" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0076")
if "OQ-0078" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0078")
if "PP-0037" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0037")

print("check_servo_packet_contract: OK")
