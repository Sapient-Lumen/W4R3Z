#!/usr/bin/env python3
import sys
from pathlib import Path

REQUIRED = {
    'README.md': ['ADR-0287', 'current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'CHANGELOG.md': ['ADR-0287', 'current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/00-index.md': ['ADR-0287', 'current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/98-archive-hygiene.md': ['check_workstation_datatransfer_finite_collection_current_stack_contract.py', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/99-llm-runbook.md': ['check_workstation_datatransfer_finite_collection_current_stack_contract.py', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/110-juicy-os-lessons.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/266-open-questions-and-risk-register.md': ['ADR-0287', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/205-data-transfer-portals-clipboard-and-dnd.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/410-desktop-viability-checklist.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/457-workstation-host-ui-and-appvm-boundary.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/484-origin-label-authority-and-anti-laundering-boundary.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/538-workstation-cross-domain-datatransfer-floor.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/675-workstation-finite-collection-handoff-directory-members-stay-snapshot-shaped-and-no-live-tree-traversal-first.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/676-workstation-finite-collection-handoff-snapshot-membership-stays-manifest-first-and-tree-summary-is-supplementary.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/677-workstation-finite-collection-handoff-first-cut-stays-read-only-and-write-enabled-receive-is-follow-on-rfc-only.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/678-workstation-finite-collection-handoff-first-cut-rejects-symlinks-and-special-files.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/679-workstation-finite-collection-handoff-manifest-entry-floor-stays-content-identity-first-and-stat-light.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/680-workstation-finite-collection-handoff-manifest-order-stays-canonical-by-review-path.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/681-workstation-finite-collection-handoff-authoritative-collection-identity-stays-digest-bound-to-canonical-manifest.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/682-workstation-finite-collection-handoff-review-path-normalization-stays-relative-clean-and-nfc-canonical.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/683-workstation-finite-collection-handoff-top-level-review-names-stay-explicit-and-no-silent-auto-rename.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/684-workstation-finite-collection-handoff-manifest-stays-ancestor-closed-and-no-implicit-parent-synthesis.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/685-workstation-finite-collection-handoff-selected-roots-stay-overlap-free-and-no-silent-subsumption.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/686-workstation-finite-collection-handoff-retrieve-stays-fresh-rooted-and-no-silent-merge-into-existing-tree.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/687-workstation-finite-collection-handoff-stays-profiled-to-b-c-d-and-not-a-fleet-host-baseline.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/688-workstation-finite-collection-handoff-first-implementation-keeps-top-level-aliasing-out-and-collisions-fail-closed.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/689-workstation-finite-collection-handoff-review-ui-may-path-compress-deterministic-ancestor-only-runs.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/690-workstation-finite-collection-handoff-advisory-mime-stays-optional-and-non-authoritative.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/691-workstation-finite-collection-handoff-receipts-pin-the-exact-created-fresh-root.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/692-workstation-finite-collection-handoff-placement-hints-stay-advisory-and-receiver-local.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/693-workstation-finite-collection-handoff-result-root-locator-stays-handle-first-and-path-snapshot-advisory.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/694-workstation-finite-collection-handoff-advisory-display-snapshot-stays-retrieve-frozen.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/695-workstation-finite-collection-handoff-result-root-handle-stays-opaque-and-non-path-shaped.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/696-workstation-finite-collection-handoff-no-owner-mode-mtime-xattr-fidelity-in-this-lane.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
    'docs/698-reviewed-finite-collection-handoff-mints-exact-artifact-family-and-first-spec-stack.md': ['current-stack map', 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'],
}

CANONICAL_DOC = 'docs/697-reviewed-finite-collection-handoff-current-contract-stack-and-stale-entrypoint-firewall.md'
CANONICAL_DOCS = ['rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md'] + [f'docs/{n}-' for n in range(674, 699)]

ok = True
for path, toks in REQUIRED.items():
    text = Path(path).read_text()
    for tok in toks:
        if tok not in text:
            print(f'{path} missing required reviewed finite-collection current-stack token: {tok}')
            ok = False

text = Path(CANONICAL_DOC).read_text()
for entry in CANONICAL_DOCS:
    if entry not in text:
        print(f'{CANONICAL_DOC} missing current-stack entry: {entry}')
        ok = False

if not ok:
    sys.exit(1)
print('reviewed finite-collection current-stack contract OK')
