import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
register = ROOT / "docs/10-method/mechanism-pressure-register.md"
if not register.exists():
    raise SystemExit("missing mechanism pressure register")
text = register.read_text(encoding="utf-8")
required = [
    "# Mechanism pressure register",
    "MP-0311",
    "FP-0210",
    "TL-0216",
    "OQ-0205",
    "pa-governance-retirement-threshold-scope-retirement-witnesses-settled-window-authority-history-handoff-quarantine-mixed.md",
    "MP-0312",
    "FP-0211",
    "TL-0217",
    "OQ-0206",
    "pa-governance-retirement-threshold-scope-retirement-history-portability-witnesses-nonportable-audit-template-authority-successor-counterexample-mixed.md",
]
missing = [needle for needle in required if needle not in text]
if missing:
    raise SystemExit("mechanism pressure register missing: " + ", ".join(missing))
overview = (ROOT / "docs/10-method/method-overview.md").read_text(encoding="utf-8")
if "mechanism-pressure-register.md" not in overview:
    raise SystemExit("method overview missing mechanism-pressure-register pointer")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
if "mechanism-pressure-register.md" not in changelog:
    raise SystemExit("changelog missing mechanism-pressure-register mention")
print("check_mechanism_pressure_register_contract: OK")
