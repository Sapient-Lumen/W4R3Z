# Cube deep audit rev0229: schema validation and context compaction

## Audit posture

Rev0229 is a maintenance audit, not a service-evidence release. It keeps `FT-0181` live because the cube still has no real `SRC2+` pilot packet, no owner-reviewed import, no closure-ready acceptance packet, and no real closeout minutes. The work in this pass is about the integrity and carrying cost of the datacube itself.

## What was missing

The most important missing control was not another policy document. The missing control was executable schema-instance validation. Rev0228 had a strong schema registry, but `tools/check_schema_registry.py` checked registration, wiring, coverage, and doc-surface reachability rather than validating every registered instance against its declared JSON Schema. A direct local schema pass found two green-lint-invalid records:

- `examples/real-import-closeouts/no-real-data-ft0181-closeout.json` carried a `revision` field that the closeout schema did not allow.
- `examples/release-deltas/rev0228-delta-manifest.json` used a lowercase `delta_id` that violated the schema pattern.

That means the registry was partly ceremonial: it could prove that every example had a named schema, but it could not prove that the example conformed to that schema. Rev0229 changes that.

## What changed in this pass

Rev0229 makes schema conformance real by teaching `tools/check_schema_registry.py` to instantiate a Draft 2020-12 JSON Schema validator for each registered schema and validate every matched instance. The pass also fixes the two records exposed by that stricter check and adds `revision` to the real-import closeout schema because the placeholder already needed revision traceability.

The second concrete change is context-pack compaction. `context-pack.json` previously embedded all assumption objects and all followthrough objects under fields named `live_assumptions` and `live_followthrough`. Only `FT-0181` is live, but the pack still carried 198 followthrough objects, including 197 done items, plus the full assumption ledger. That contradicted the stated compact-startup policy and made the re-entry payload misleading. Rev0229 changes the generator so the context pack carries compact assumption IDs, only non-done followthrough objects, and explicit ledger counts/source pointers. `tools/check_reentry_navigation.py` now fails if the context pack regrows embedded assumption objects, done followthrough payloads, or excessive file size.

## What appears wasteful

The cube has become heavily protected against false closure, but the cost of protection is now visible. There are many release-control artifacts, many branch-history shells, and many documents that repeat the same claim-boundary grammar. This is not all bad: the repetition was part of the safety migration. It is now expensive enough that new control creation should be treated as a scarce intervention rather than the default move.

The highest-return future compression target is the branch-history plane: `first-*`, `portable-*`, and `late-relapse-*` governance surfaces remain useful as archive memory, but many are structurally similar and could be represented by denser branch-family records plus a small number of canonical prose pages. The safe path is not deletion first. The safe path is to add compression budgets, identify families with repeated phrase load, then quarantine or retire prose only after retrieval equivalence is demonstrated.

The second compression target is assumption state. The assumption ledger is useful, but the cube currently treats nearly every historical assumption as active. A future pass should split assumption state into `active`, `superseded`, `archived`, and `candidate`, with `active` reserved for assumptions that can change a present decision. That would make the live re-entry bundle smaller and more truthful.

## What still looks noisy

The surface-map metadata is better than before rev0228, but tags remain too broad on rule-assisted rows. A document can inherit `hot-exam`, `service-intake`, or similar tags from incidental prose rather than primary identity. Surface contracts prevent the most important canonical rows from drifting, but they do not solve noisy retrieval across the long tail. A future map should separate `primary_tags` from `mentioned_tags`, with stronger thresholds for branch and service labels.

## What external research suggests

The external environment still points toward caution. Current public guidance supports AI use in education only when aligned with statutory authority, privacy, transparency, human-centered design, and evidence discipline. AI tutors and support agents may be useful, but recent reviews still distinguish stronger evidence for structured intelligent tutoring systems from thinner evidence for fully autonomous generative-AI tutors. Privacy rules for children and student records are also tightening rather than loosening. This reinforces the cube's refusal to convert examples, validators, or vendor claims into learning evidence.

## Speculative direction

The cube should probably stop growing by adding whole new prose surfaces for every concern. The next sustainable phase should prefer three moves:

1. turn repeated prose families into structured records and maps;
2. make validators enforce semantic promises that are already written in prose;
3. quarantine low-decision-value history after it remains discoverable through generated indexes.

The guiding question for new work should be: does this add decision power, or only another reminder not to make a forbidden claim?

## Boundaries

This audit does not close `FT-0181`, does not upgrade any `SRC0` or synthetic example into real evidence, does not prove learning, and does not make any operational AI service safe, compliant, effective, accessible, fair, or workload-reducing. It only makes the cube's control plane more executable and less wasteful to reload.
