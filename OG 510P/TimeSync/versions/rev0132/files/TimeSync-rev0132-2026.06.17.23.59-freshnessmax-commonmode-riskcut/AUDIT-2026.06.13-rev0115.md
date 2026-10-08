# TimeSync rev0115 audit — cloudtainer mutation-survivor triage

rev0115 continues FT-0090. The deep-read result was that rev0114 was not structurally broken: JSON parsing, schema validation, fixture coverage, semantic-vector execution, derivation checks, manifest checks, and revision-reference lint were clean. The issue was narrower and more dangerous: some schema-valid digest fields could still bind the wrong artifact class unless an existing semantic helper happened to cover that exact branch.

## What was found

A targeted mutation pass over passing fixtures changed digest `binds` values to other schema-allowed artifact classes. Several mutations still passed schema and semantic validation. The highest-signal survivors were not exotic edge cases; they sat in current replay-transparency and aggregate publication surfaces:

- `replay_event.replay_event_digest` could bind an aggregate revision-chain artifact instead of `challenge_result_replay_event`.
- `transparency_anchor.digest` and `anchor_evaluation.checkpoint_consistency.current_checkpoint_digest` could bind a revision-chain artifact instead of an append-only replay log checkpoint.
- `aggregate_summary.integrity_binding.digest` could bind a revision-chain artifact instead of `aggregate_verifier_audit_summary`.
- `aggregate_correction_authority_reference.authority_binding.authority_digest` could bind `retained_operator_record` instead of correction-authority rules or identity.
- `transparency_trust_policy_reference.lifecycle_status.status_record_digest` could bind `profile_compatibility_statement` instead of `transparency_trust_policy_lifecycle_status`.

These are wrong-bind bypasses: the archive was already treating digest class as semantic evidence, but not all branches had fail-closed class binding.

## What changed

rev0115 adds three small helper modules and wires them into the existing validator:

- `tools/replay_digest_semantics.py`
- `tools/aggregate_correction_digest_semantics.py`
- `tools/transparency_policy_digest_semantics.py`

The helpers reject wrong artifact-class bindings for replay receipt core digests, aggregate verifier audit integrity digests, aggregate correction-authority digests, and transparency trust-policy lifecycle/drift digests. Four derivation-checked negative fixtures were added, with semantic vectors `TV-N314` through `TV-N317`. The semantic vector suite now contains 336 vectors.

## What is still missing

The project still needs a repeatable mutation-survivor harness. The ad hoc audit was useful because it tested semantic class substitution rather than only handcrafted negatives. That should become a checked tool, but it should be scoped: mutate digest class, freshness state, lifecycle state, and current-use flags only in fields where a schema-valid mutation could plausibly preserve shape while changing meaning.

The digest `binds` ontology is also still informal. The validator now contains many local class expectations, but there is not yet a single machine-readable table saying which semantic path may bind which artifact classes and under which conditions. A small table would reduce helper drift without importing external repositories or policy languages.

## What looks wasteful

The schemas remain large and repetitive. The archive contains no `$defs` or `$ref` reuse in the JSON Schema files, so repeated digest, profile-reference, lifecycle, and redacted-evidence shapes are rendered inline. That makes review and mutation harder because the same object grammar appears in many places. The safest correction is not to hand-edit every schema today; it is to create a source-of-truth schema-generation layer or an internal shared-definition form that renders the current flat schemas for consumers that need standalone files.

The validator is also still too central. rev0092 through rev0115 have moved many concern families out of `tools/validate_archive.py`, but the main validator remains the routing hub for schema-specific logic and embedded object checks. Future extractions should be driven by mutation survivors or long-function collapse, not by cosmetic modularity.

The fixture corpus is useful but bulky. New negative examples should continue using derivations from positive fixtures so copied JSON families do not silently drift apart.

## External context considered

Current standards work reinforces TimeSync's boundary choice: stay a semantic/evidence layer rather than become a time-transfer protocol. NTPv5 is focused on the wire protocol and deliberately leaves client selection, filtering, and clock discipline out of scope. NTS authenticates NTP client-server synchronization, Roughtime supplies rough authenticated bootstrap time and malfeasance-report concepts, PTP/IEEE 1588 serves precision networked clock synchronization, and Certificate Transparency shows the value and limits of append-only public logs. TimeSync should bind and assess evidence from such systems without importing their rosters, keys, logs, or policy languages as TimeSync provenance.

## Recommended next moves

1. Add a checked `tools/mutation_survivor_audit.py` that mutates digest `binds` fields in passing fixtures and fails only on an allowlist of intentionally polymorphic paths.
2. Introduce a small digest-binding expectation table for semantic paths, expected `binds`, and conditional alternatives such as `authorization_basis == profile_compatibility_statement`.
3. Start a schema-rendering experiment that preserves standalone schemas while eliminating repeated inline subtrees in source.
4. Continue converting bulky negatives to derivation-checked fixtures.
5. Leave FT-0090 open until mutation-survivor checks and schema-source deduplication are both in place.
