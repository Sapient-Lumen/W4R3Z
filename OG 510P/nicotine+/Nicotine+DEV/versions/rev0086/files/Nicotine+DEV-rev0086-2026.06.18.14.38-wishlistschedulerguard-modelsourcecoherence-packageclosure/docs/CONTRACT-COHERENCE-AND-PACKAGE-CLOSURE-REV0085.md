# Contract coherence and package closure — rev0085

## Why this is substantive evidence work

Rev0085 originally reached valid search, public-head, composition, and unit-test
results but failed twice during final package assembly. The failure was not
merely cosmetic. The working tree simultaneously contained:

```text
REVISION.txt                                      rev0085
data/current_revision_contract.json              rev0084
data/current_public_head_contract.json candidate rev0084 prototype
data/current_candidate_artifact_contract.json    rev0085 prototype
data/rev0085_patch_composition_audit.json         retained status: pass
```

The retained composition result was correct when generated, but ceased to be a
valid statement about the live authority graph after one input contract drifted.
Because each validator checked only its own local inputs, the cube could display
several individually plausible green records while the package as a whole had
no coherent current meaning.

## Correction

`data/current_contract_coherence_contract.json` now classifies every current
JSON authority as either revision-bound or revision-neutral and binds the
shared candidate, public-head, composition, source, unit-lane, search-action,
package, and revision identities.

`tools/audit_current_contract_coherence.py` then validates the live graph and
retained result records together. It rejects, among other cases:

- a stale revision-bound contract;
- a revision marker added to a revision-neutral contract;
- different current candidates in public-head, composition, or action policy;
- omission of this contract or tool from package/revision authority;
- a retained result whose status is no longer pass;
- a retained composition result bound to old candidate bytes.

The audit also records a digest over the complete authority/result snapshot so
future revisions can identify exactly which graph was validated.

## Package integration

`tools/audit_current_package.py` now invokes the coherence audit directly.
Listing `data/rev0085_contract_coherence_audit.json` as a passing status file is
not sufficient: the current graph must pass again at package-audit time and
again after clean extraction.

The package contract additionally covers the source-history evidence root and
requires the coherence contract itself. The candidate-artifact validator now
requires an exact top-level schema, eliminating the redundant
`historical_evidence_bindings` alias that had contradicted the role-classified
`evidence_bindings` authority.

## Disposition

Package finalization is part of the evidence chain. A revision is not complete
merely because its local research tests passed; the linked archive must bind
one revision, one current candidate, one source lineage, one packet ledger, and
one reproducible manifest without stale green records.
