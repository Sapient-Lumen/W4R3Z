from pathlib import Path
import shutil
import re

SRC = Path(__file__).resolve().parent
PREV = SRC
DOCS = SRC / "docs"

# This script documents the rev0141 in-place continuation pass.
# It is intentionally simple because the archive already contains the finished rev0141 state.

assert (DOCS / "225-identity-relabel-certificate-regeneration-and-advanced-subject-salvage-interface-spec.md").exists()
assert (DOCS / "226-share-title-override-link-alias-and-local-name-plane-issuance-interface-spec.md").exists()
assert (DOCS / "227-route-evidence-latency-bottleneck-and-directness-explanation-interface-spec.md").exists()
assert (DOCS / "228-global-search-scope-result-provenance-and-review-preserving-navigation-interface-spec.md").exists()

print("rev0141 already applied in this tree.")
