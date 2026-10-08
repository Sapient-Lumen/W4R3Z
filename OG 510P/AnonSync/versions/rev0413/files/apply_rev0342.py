from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"

NEW_FILES = [
    "1192-resilio-download-priority-policy-provenance-active-window-and-visible-order-fragmentation-evaluation.md",
    "1193-queue-governance-contract-sheet-page-policy-origin-active-window-and-visible-order-interface-spec.md",
    "1194-priority-origin-review-page-global-default-sticky-none-and-single-file-spillover-interface-spec.md",
    "1195-active-window-proof-page-50000-file-ceiling-suspension-exceptions-and-queue-rebuild-interface-spec.md",
    "1196-visible-order-mismatch-page-ui-alphabetical-order-non-splittable-files-and-overclaim-barrier-interface-spec.md",
    "1197-queue-governance-lineage-receipt-page-policy-origin-window-scope-and-visible-order-trust-interface-spec.md",
]

if __name__ == "__main__":
    missing = [name for name in NEW_FILES if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f"Missing rev0342 docs: {missing}")
    print("rev0342 docs present and ready")
