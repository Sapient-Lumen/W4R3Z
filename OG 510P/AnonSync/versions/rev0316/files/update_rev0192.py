from pathlib import Path

ROOT = Path(__file__).resolve().parent
print("This archive was already materialized as rev0192.")
print("New docs added:")
for name in [
    "docs/386-resilio-seat-lineage-identity-replacement-and-reset-boundary-evaluation.md",
    "docs/387-seat-lineage-page-same-seat-successor-seat-and-foreign-seat-verdict-interface-spec.md",
    "docs/388-identity-replacement-page-certificate-takeover-subject-loss-and-safe-link-review-interface-spec.md",
    "docs/389-device-roster-page-hidden-offline-duplicate-and-returning-seat-interpretation-interface-spec.md",
    "docs/390-reset-impact-page-reset-path-storage-rehome-and-preservation-verdict-interface-spec.md",
]:
    print(" -", name)
