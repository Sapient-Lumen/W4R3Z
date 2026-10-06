import json
import pathlib

from witness_vocabulary_lib import load_families, expect_allowed

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/10-method/witness-vocabularies-state-families-and-comparability-budgets.md"
TRAJ = ROOT / "docs/00-meta/trajectory-map.md"
PROMPTS = ROOT / "docs/50-promptcraft/prompt-pairs.md"
RUNBOOK = ROOT / "docs/00-meta/llm-runbook.md"
CLAIMS = ROOT / "docs/20-constitution/claim-registry.md"
INVS = ROOT / "docs/20-constitution/invariant-registry.md"
OQS = ROOT / "docs/20-constitution/open-question-registry.md"
PPREG = ROOT / "docs/20-constitution/prompt-pair-registry.md"
CONTRACT = ROOT / "docs/20-constitution/revision-receipt-contract.md"
RECEIPT = ROOT / "REVISION-RECEIPT.json"
VOCAB = ROOT / "WITNESS-VOCABULARY.json"
SURFACE = ROOT / "SURFACE-STATUS.json"
FOLLOW = ROOT / "FOLLOWTHROUGH-QUEUE.json"
ASSUME = ROOT / "ASSUMPTION-LEDGER.json"
FOREIGN = ROOT / "FOREIGN-PRESSURE-LEDGER.json"
RESOLUTION = ROOT / "RESOLUTION-LEDGER.json"
RETRO = ROOT / "RETROSPECTIVE-QUEUE.json"
FIREBREAK = ROOT / "FIREBREAK-LEDGER.json"
OBLIGATION = ROOT / "OBLIGATION-LEDGER.json"
APPLICABILITY = ROOT / "APPLICABILITY-LEDGER.json"

for path in (DOC, TRAJ, PROMPTS, RUNBOOK, CLAIMS, INVS, OQS, PPREG, CONTRACT, RECEIPT, VOCAB, SURFACE, FOLLOW, ASSUME, FOREIGN, RESOLUTION, RETRO, FIREBREAK, OBLIGATION, APPLICABILITY):
    if not path.exists():
        raise SystemExit(f"missing required vocabulary surface: {path}")

text = DOC.read_text(encoding="utf-8")
required = [
    "# Witness vocabularies, state families, and comparability budgets",
    "## Practice / observation",
    "## Pressure from neighboring datacubes",
    "## External pressure from adjacent controlled-vocabulary and status practice",
    "## Working synthesis",
    "## Witness vocabulary vs core lexicon vs durable ledgers vs prose rationale",
    "## Countermodels / probes",
    "## Design consequences",
    "## Transformer-facing implication",
    "state family / governed field family",
    "allowed tokens / stable public labels",
    "target surfaces / ledgers / receipt fields governed by that family",
    "excluded near-synonyms / drift temptations / non-controlled prose family",
    "comparability budget",
    "extend-registry / narrow-family / fail-closed-on-drift consequence",
]
missing = [item for item in required if item not in text]
if missing:
    raise SystemExit("vocabulary contract missing: " + ", ".join(missing))

if "OQ-0111" not in TRAJ.read_text(encoding="utf-8"):
    raise SystemExit("trajectory map missing OQ-0111 wiring")
prompt_text = PROMPTS.read_text(encoding="utf-8")
if "PP-0070" not in prompt_text or "allowed tokens / stable public labels" not in prompt_text:
    raise SystemExit("prompt pairs missing vocabulary ratchet")
runbook = RUNBOOK.read_text(encoding="utf-8")
if "witness vocabulary / state-family registry / comparability budget" not in runbook:
    raise SystemExit("runbook missing vocabulary guidance")
if "CL-0111" not in CLAIMS.read_text(encoding="utf-8"):
    raise SystemExit("claim registry missing CL-0111")
if "INV-0109" not in INVS.read_text(encoding="utf-8"):
    raise SystemExit("invariant registry missing INV-0109")
if "OQ-0111" not in OQS.read_text(encoding="utf-8"):
    raise SystemExit("open question registry missing OQ-0111")
if "PP-0070" not in PPREG.read_text(encoding="utf-8"):
    raise SystemExit("prompt pair registry missing PP-0070")
if "vocabulary_witness" not in CONTRACT.read_text(encoding="utf-8"):
    raise SystemExit("revision receipt contract missing vocabulary_witness")

receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
vocab = json.loads(VOCAB.read_text(encoding="utf-8"))
if vocab.get("project") != "DelayBasin":
    raise SystemExit("WITNESS-VOCABULARY project must be DelayBasin")
if vocab.get("revision") != receipt.get("revision"):
    raise SystemExit("WITNESS-VOCABULARY revision must match receipt revision")
families = load_families()
required_families = {
    "basis_state", "scope_state", "autonomy_posture", "collapse_state", "cue_state",
    "retrospective_state", "retrospective_disposition", "followthrough_state",
    "assumption_state", "obligation_state", "applicability_state", "assimilation_state",
    "closure_state", "trace_state", "decision_state", "execution_state", "public_state",
    "status_state_class", "vocabulary_state",
}
missing_families = sorted(required_families - families.keys())
if missing_families:
    raise SystemExit("WITNESS-VOCABULARY missing required families: " + ", ".join(missing_families))
for name, meta in families.items():
    if not isinstance(meta, dict):
        raise SystemExit(f"WITNESS-VOCABULARY family {name} must be an object")
    allowed = meta.get("allowed")
    surfaces = meta.get("surfaces")
    if not isinstance(allowed, list) or not allowed or not all(isinstance(x, str) and x for x in allowed):
        raise SystemExit(f"WITNESS-VOCABULARY family {name} allowed must be a non-empty string list")
    if len(set(allowed)) != len(allowed):
        raise SystemExit(f"WITNESS-VOCABULARY family {name} has duplicate allowed token")
    if not isinstance(surfaces, list) or not surfaces or not all(isinstance(x, str) and x for x in surfaces):
        raise SystemExit(f"WITNESS-VOCABULARY family {name} surfaces must be a non-empty string list")

wv = receipt.get("vocabulary_witness")
if not isinstance(wv, dict):
    raise SystemExit("receipt vocabulary_witness must be an object")
for key in ["witness_surface", "controlled_families", "target_surfaces", "ambient_synonyms_excluded", "comparability_budget", "vocabulary_state", "repair"]:
    if key not in wv:
        raise SystemExit(f"receipt vocabulary_witness missing key: {key}")
if wv.get("witness_surface") != "WITNESS-VOCABULARY.json":
    raise SystemExit("receipt vocabulary_witness.witness_surface must point to WITNESS-VOCABULARY.json")
if not isinstance(wv.get("controlled_families"), list) or not wv["controlled_families"]:
    raise SystemExit("receipt vocabulary_witness.controlled_families must be a non-empty list")
for fam in wv["controlled_families"]:
    if fam not in families:
        raise SystemExit(f"receipt vocabulary_witness references unknown family: {fam}")
if not isinstance(wv.get("target_surfaces"), list) or not wv["target_surfaces"]:
    raise SystemExit("receipt vocabulary_witness.target_surfaces must be a non-empty list")
for rel in wv["target_surfaces"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"receipt vocabulary_witness target surface missing: {rel}")
if not isinstance(wv.get("ambient_synonyms_excluded"), list) or not wv["ambient_synonyms_excluded"]:
    raise SystemExit("receipt vocabulary_witness.ambient_synonyms_excluded must be a non-empty list")
if wv.get("vocabulary_state") not in families["vocabulary_state"]["allowed"]:
    raise SystemExit("receipt vocabulary_witness.vocabulary_state invalid")
if wv.get("repair") not in {"ordinary-continuation", "use-registry", "narrow-family", "hold", "recover-resync"}:
    raise SystemExit("receipt vocabulary_witness.repair invalid")

expect = lambda family, value, where: expect_allowed(families, family, value, where)

expect("basis_state", receipt["basis_witness"]["basis_state"], "receipt basis_state")
expect("scope_state", receipt["scope_witness"]["scope_state"], "receipt scope_state")
expect("autonomy_posture", receipt["authorship_witness"]["autonomy_posture"], "receipt autonomy_posture")
expect("collapse_state", receipt["authorship_witness"]["collapse_state"], "receipt collapse_state")
expect("cue_state", receipt["reentry_cue_witness"]["cue_state"], "receipt cue_state")
expect("retrospective_state", receipt["retrospective_write_witness"]["cooling_state"], "receipt retrospective state")
expect("retrospective_disposition", receipt["retrospective_write_witness"]["disposition"], "receipt retrospective disposition")
expect("followthrough_state", receipt["followthrough_witness"]["followthrough_state"], "receipt followthrough state")
expect("assumption_state", receipt["assumption_witness"]["assumption_state"], "receipt assumption state")
expect("obligation_state", receipt["obligation_witness"]["obligation_state"], "receipt obligation state")
expect("applicability_state", receipt["applicability_witness"]["applicability_state"], "receipt applicability state")
expect("assimilation_state", receipt["foreign_pressure_witness"]["assimilation_state"], "receipt assimilation state")
expect("closure_state", receipt["resolution_witness"]["closure_state"], "receipt closure state")
expect("trace_state", receipt["reasoning_firebreak_witness"]["trace_state"], "receipt trace state")

surface = json.loads(SURFACE.read_text(encoding="utf-8"))
expect("decision_state", surface["status_lanes"]["decision_state"], "SURFACE-STATUS decision_state")
expect("execution_state", surface["status_lanes"]["execution_state"], "SURFACE-STATUS execution_state")
expect("public_state", surface["status_lanes"]["public_state"], "SURFACE-STATUS public_state")
expect("public_state", receipt["status_witness"]["public_state"], "receipt public_state")
expect("status_state_class", surface["state_class"], "SURFACE-STATUS state_class")

for item in json.loads(FOLLOW.read_text(encoding="utf-8")).get("items", []):
    expect("followthrough_state", item["state"], f"FOLLOWTHROUGH {item.get('id')}")
for item in json.loads(ASSUME.read_text(encoding="utf-8")).get("items", []):
    expect("assumption_state", item["state"], f"ASSUMPTION {item.get('id')}")
for item in json.loads(FOREIGN.read_text(encoding="utf-8")).get("items", []):
    expect("assimilation_state", item["state"], f"FOREIGN state {item.get('id')}")
    expect("assimilation_state", item["assimilation_state"], f"FOREIGN assimilation_state {item.get('id')}")
for item in json.loads(RESOLUTION.read_text(encoding="utf-8")).get("items", []):
    expect("closure_state", item["state"], f"RESOLUTION {item.get('id')}")
for item in json.loads(RETRO.read_text(encoding="utf-8")).get("items", []):
    expect("retrospective_state", item["state"], f"RETROSPECTIVE {item.get('id')}")
for item in json.loads(FIREBREAK.read_text(encoding="utf-8")).get("items", []):
    expect("trace_state", item["state"], f"FIREBREAK {item.get('id')}")
for item in json.loads(OBLIGATION.read_text(encoding="utf-8")).get("items", []):
    expect("obligation_state", item["state"], f"OBLIGATION {item.get('id')}")
for item in json.loads(APPLICABILITY.read_text(encoding="utf-8")).get("items", []):
    expect("applicability_state", item["state"], f"APPLICABILITY {item.get('id')}")

print("check_vocabulary_witness_contract: OK")
