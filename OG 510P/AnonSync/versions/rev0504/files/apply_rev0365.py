from pathlib import Path

# Revision helper retained for archive traceability.
# This archive already contains the applied rev0365 content.
# The tranche added docs 1330-1335 and prepended revision addenda to README.md,
# docs/00-status.md, docs/10-resilio-sync-evaluation.md,
# docs/11-resilio-borrow-line-and-non-clone-scorecard.md, docs/20-product-direction.md,
# and docs/sources.md.

root = Path(__file__).resolve().parent
print("rev0365 archive contents are already applied at", root)
