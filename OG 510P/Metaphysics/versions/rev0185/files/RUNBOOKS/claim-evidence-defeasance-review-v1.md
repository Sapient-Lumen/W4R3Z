# Claim/Evidence/Defeasance Review Runbook v1

## Purpose

Use this runbook whenever a release adds, removes, renames, upgrades, publicizes, or operationalizes a claim about the archive.

## Entry criteria

- A current package exists.
- The proposed claim has a stable claim identifier.
- Supporting or limiting evidence packets are named.
- The claim can be assigned a freshness rule and defeasance profile.

## Required steps

1. Add or update the claim node in `CLAIM_GRAPH.yml`.
2. Add or update supporting, limiting, or blocking evidence packets in `EVIDENCE_PACKET_INDEX.yml`.
3. Check whether the claim contradicts any allowed/forbidden claim-language cluster in `CLAIM_LANGUAGE_LEDGER.yml`.
4. Add contradiction rows to `CONTRADICTION_LEDGER.yml` when the claim could be confused with a stronger upgrade claim.
5. Assign freshness rule from `FRESHNESS_POLICY.yml`.
6. Assign downstream defeat or withdrawal rule in `DEFEASANCE_PROPAGATION.yml`.
7. Run `tools/check_claim_evidence.py`.
8. Run `tools/run_query_regression.py` and `tools/run_fixture_corpus.py`.
9. Regenerate reports and `MANIFEST.sha256`.
10. Fresh-extract and rerun `tools/validate_archive.py`.

## Exit criteria

- Claim/evidence check passes.
- Current reports are present.
- Query regression includes claim/evidence queries.
- Fixture corpus contains at least one negative claim/evidence case.
- The validator passes from a fresh extraction.

## Forbidden shortcuts

- Do not treat a claim as warranted merely because it appears in prose.
- Do not treat a file path as evidence unless the evidence packet states what the path supports.
- Do not turn a local evidence packet into a source-current or domain-authoritative claim.
- Do not claim automatic truth maintenance or public knowledge-graph publication.
