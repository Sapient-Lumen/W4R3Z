import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
required_files = [
    ROOT / "docs/10-method/stable-continuation-regimes-and-regime-probes.md",
]
for path in required_files:
    if not path.exists():
        raise SystemExit(f"missing required regime surface: {path.relative_to(ROOT)}")

checks = [
    (ROOT / "docs/20-constitution/claim-registry.md", "CL-0022"),
    (ROOT / "docs/20-constitution/invariant-registry.md", "INV-0020"),
    (ROOT / "docs/20-constitution/open-question-registry.md", "OQ-0022"),
    (ROOT / "docs/50-promptcraft/prompt-pairs.md", "discriminating probe or countermodel"),
]
for path, needle in checks:
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        raise SystemExit(f"regime-probe contract missing {needle} in {path.relative_to(ROOT)}")

print("check_regime_probe_contract: OK")
