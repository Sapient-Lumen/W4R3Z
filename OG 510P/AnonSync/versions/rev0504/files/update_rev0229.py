from pathlib import Path
ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
print("rev0229 control surface grade updates baked into archive at", ROOT)
for name in [
    "571-resilio-control-surface-grade-audience-auth-and-transport-fragmentation-evaluation.md",
    "572-control-surface-grade-page-audience-auth-transport-and-fallback-interface-spec.md",
    "573-exposure-auth-mutation-review-page-loopback-lan-http-https-and-mode-shift-interface-spec.md",
    "574-certificate-posture-page-endpoint-origin-warning-class-and-durable-fix-interface-spec.md",
    "575-control-surface-receipt-page-audience-auth-grade-transport-and-recovery-path-interface-spec.md",
]:
    print("-", DOCS / name)
