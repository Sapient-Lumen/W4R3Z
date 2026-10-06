# DeriveBSD rev0570 session review — snapshot identity + handoff size guard

## Intent

Continue the FreeBSD real-host proof lane without adding doctrine-only surface area. The highest-risk unfinished item remains non-simulated FreeBSD host proof, so this cut hardens the cloudtainer import boundary that will receive scarce host evidence.

## Substantive changes

- Changed FreeBSD host-proof import directory identity to bind `proof_status` plus the full copied handoff snapshot canonical digest, not only the copied `receipt.json` canonical digest.
- Added regression coverage for same-receipt/different-`README.import.txt` handoffs, proving checksum-bound optional evidence publishes to a distinct import path instead of colliding.
- Added loose handoff member size refusal before checksum or JSON parsing, using the shared finite handoff member size limit.
- Refactored loose verify, seal, unseal, import, and audit paths to consume `HANDOFF_ALLOWED_NAMES` from `tools/freebsd/host_proof_contract.py` instead of rebuilding the allowed handoff member set locally.
- Carried the r598 version and target-matrix/bundle ids through FreeBSD host-smoke/proof-bundle schemas, validation receipts, examples, README, CHANGELOG, current docs, generated docs, and cube summary examples.
- Restored the missing r597 discovery anchor in `docs/00-index.md` while staying inside the front-door byte budget by pruning older index prose rather than raising the budget.

## Audit/refactor note

The audited seam was the import identity boundary. r597 made optional handoff evidence checksum-bound, but the import path still over-focused on the copied receipt digest. That left an avoidable identity collision: two handoffs with identical `receipt.json` but different checksum-bound README, bundle, or SHA256SUMS bytes could claim the same import directory. r598 corrects this by treating the copied handoff snapshot manifest as the import identity material.

## Validation

- `release-critical`: 49/49 passed.
- `schema-cube-audit`: 3/3 passed.
- `validate_spec_examples.py`: 469 examples validated.
- `check_json_duplicate_key_rejection.py`: 1445 JSON files scanned.
- `check_generated_docs.py`: passed.
- `check_current_generated_surface_sync.py`: passed.
- Zip integrity: passed (`zipfile.testzip() == None`).

## Remaining risk

This still does not include a non-simulated FreeBSD host receipt. The true next milestone remains running the operator packet on a real `15.1-RELEASE` host, sealing or transporting the handoff, importing it, and letting the strict audit gate accept only `real-host-proof`.
