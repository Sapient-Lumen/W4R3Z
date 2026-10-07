# META INSTRUMENTS — current

This directory was added in rev0029 because the cube has become strong enough to need instruments that audit the cube itself, not only its candidates.

The purpose is not to make the work colder. The purpose is to keep mercy from being laundered into myth, brochure copy, operator preference, public-export harm, or beautiful dissent with no veto power.

Core additions:

- `Redaction-Risk-Scan-current.*` and `Redaction-Risk-Open-Findings-current.*` — scanner-backed public-export hazard layer for contact digits, emails, coordinates, addresses, grave/case identifiers, and other operational redaction risks.

- `Operator-Dissent-Ledger-current.*` — a place where critiques of the cube's method, operator gravity, absorption of dissent, or update failures are logged with required behavior-change fields.
- `Manifest-Audit-current.*` — detects package metadata drift, including the rev0028 stale manifest-count bug.
- `Source-Freshness-and-Provenance-Audit-current.*` — makes source roles and provenance risks visible without pretending to perform a live web refresh.
- `Claim-Type-Taxonomy-current.*` — states the evidence standard for each claim type currently present in the claim ledger.
- `Evidence-Debt-Dashboard-current.*` — summarizes debt pressure so evidence debt remains a work queue rather than decorative humility.
- `Boundary-Rule-Coverage-current.*` — maps high-risk subject classes to the rules that should fire.
- `Public-Export-Checklist-current.md` — a release gate before any prose/public edition escapes the working cube.
- `Update-Behavior-Gate-current.md` — distinguishes literary updates from behavioral updates.

The rev0029 pass adds no new candidates and performs no outward fact refresh. It is a meta-hardening pass.

rev0030 adds a scanner-backed redaction-risk layer and updates QA so high-risk configured findings fail the package. This remains an aid to judgment, not a substitute for manual privacy review.

rev0031 adds a separate `SCHEMA/` contract layer rather than another META table.
That layer includes front-matter contracts, ledger/header contracts, JSON mirror
parity checks, source-type controlled vocabulary, a package release contract,
and schema validation reports. QA now treats schema-contract failure as package
failure. The goal is to prevent careful prose from hiding machine-readable drift.


## rev0032 additions

- `META/Claim-Evidence-Strength-current.*` derives non-final evidence-strength, capacity-currentness risk, and suggested refresh cadence labels for each claim.
- `META/Refresh-Priority-Queue-current.*` aggregates claim/debt pressure into a candidate-level work queue.
- `META/Evidence-Lifecycle-Policy-current.md` records the rule: supported enough to keep is not the same as fresh enough to use publicly.


## rev0033 additions

- `META/Negative-Case-Ledger-current.*` records rejected, deferred, demoted, not-yet-a-door, and admitted-with-boundary cases so the cube does not remember only successful admissions.
- `META/Online-Research-Intake-current.*` holds same-pass web research that has not yet been promoted to Source-Registry or claim evidence.
- `META/Operator-Update-Audit-current.*` records behavior-change receipts for operator-dissent rows, beginning with `opdist_0001`.

rev0033 performs online research as intake and routing work. It does not claim that the candidate ledgers have been fully refreshed.

## rev0034 additions

- `META/Source-Promotion-Decision-Ledger-current.*` gives every online-intake row an explicit promote/hold/block decision before Source-Registry or claim promotion.
- `META/Public-Claim-Quarantine-current.*` turns all `now_or_before_any_public_claim` lifecycle rows into a public-wording block list.
- `META/Refresh-Sprint-Decision-Matrix-current.*` chooses six high-pressure follow-up routes and records why this pass blocks or holds rather than promotes.

rev0034 performs a veto/quarantine pass. It adds no candidates, no office cards, no claim rows, and no Source-Registry rows. It does add six refresh notes because the routing decisions now attach to named candidate clusters.


## rev0035 additions

- `META/Source-Promotion-Transaction-Audit-current.*` records atomic source-promotion transactions and the files/rows changed by each promotion.
- `META/Public-Claim-Release-Ledger-current.*` records claims removed from quarantine with a narrow release scope and remaining blocks.

rev0035 performs a candidate-specific source-promotion canary for Aisha Diss / project.ME. It promotes paired local-reporting sources for high-level work shape only and keeps official/contact-rich pages held.


## rev0036 additions

rev0036 adds a counterevidence-promotion canary for the Sant’Egidio humanitarian-corridor entry. One SAGE academic source is promoted to Source-Registry and claim/debt ledgers as boundary pressure only. No public current-capacity claim is released.

## rev0037 — conflict-zone no-map canary

rev0037 adds a conflict-zone mutual-aid source-promotion canary for Sudan ERRs. `META/Source-Promotion-Transaction-Audit-current.*` now records `spx_0003`, which promotes aggregate localization/risk/context sources without releasing public current-capacity or operational wording. `META/Boundary-Rule-Coverage-current.*` now includes rule 35.


## rev0038 — border counterpressure no-route canary

rev0038 adds a Calais/HRO source-promotion canary. `spx_0004` promotes aggregate counterpressure/publication-infrastructure sources without releasing public current-capacity, route, location, schedule, image, accommodation-access, or referral wording. `META/Boundary-Rule-Coverage-current.*` now includes rule 36.


## rev0039 — Pacific survivor-service no-referral canary

rev0039 adds a Pacific crisis-centre source-promotion canary. `spx_0005` promotes regional standards/funding context while holding contact-rich service pages and live directories. `META/Boundary-Rule-Coverage-current.*` now includes rule 37.

## rev0040 instrument addition
rev0040 adds a family-search no-field-map canary through source-promotion decisions, transaction audit, negative-case ledger, operator receipt, and boundary-rule coverage rule 38.


## rev0041 instrument addition

rev0041 adds a law-to-door no-service-capacity gate. The new refresh note, rule 39, negative-case row, promotion transaction, and source-promotion decisions prevent legal-framework, protection-order, court/police, No Drop, adviser, and justice-pathways sources from becoming legal advice, referral, current-capacity, or enforcement claims.

## rev0043 instrument addition

rev0043 adds a public-cemetery searchable-memory no-record-extraction gate. The new refresh note, rule 41, negative-case row, promotion transaction, public-claim quarantine row, and source-promotion decisions prevent cemetery databases, maps, CMTS/search pages, open datasets, and public-visit material from becoming a second public index of the dead.

- rev0046 overdose memorial no-tribute/no-event-map gate: Source promotion and negative-case ledgers now distinguish high-level campaign/prevention/stigma context from tribute, event-map, memorial-exhibit, contact, training/supply, and referral surfaces.


- rev0047 adds migrant-death monitoring / no-route no-distress-signal handling across intake, promotion, transaction, negative-case, quarantine, and sprint ledgers.

## rev0049 governance and rule-46 instruments

rev0049 adds a governance layer, source harm/link fields, and `META/Rule46-Scan-current.*`. The meta layer treats public links and public files as release surfaces, not as neutral metadata.


## rev0050 public-export eligibility

`META/Public-Export-Eligibility-current.*` is the package-level eligibility gate between the working cube and the scrubbed public index. It distinguishes index eligibility from public prose release, public URL release, current-capacity claims, image reuse, case-detail reuse, and referral language.


## rev0051 public-lint and governance-snapshot instruments

`META/Public-Release-Lint-current.*` is the public-layer handoff blocker report. It is narrower than the whole-cube redaction scan and specifically protects the scrubbed `PUBLIC/` layer after rendering.

`META/Sensitive-Surface-Inventory-current.*` inventories configured sensitive surfaces across the working package. It is an internal audit tool, not a public-safe reading file.

`META/Candidate-Governance-Snapshot-current.*` and `META/Governance-Review-Queue-current.*` join public-export eligibility, source-link review, claim lifecycle, consent/governance rows, and refresh posture so a future editor cannot treat a candidate index row as release approval.


## rev0052 row/provenance/release-gate instruments

`SCHEMA/Row-Validation-Report-current.*` validates row-level values, ids, dates, paths, and cross-ledger references rather than only headers.

`META/Generated-Artifact-Provenance-current.*` records generator scripts, input paths, artifact SHA256 values, input fingerprints, and row counts for key generated artifacts.

`META/Revision-Surface-Audit-current.*` checks front-door current-revision headers and JSON revision fields.

`META/Release-Gate-Attestation-current.*` joins schema, row, public-lint, redaction, Rule 46, sensitive-surface, eligibility, source-link, provenance, revision, and public-contract gates before handoff.

## rev0053 meta-instruments

- `META/Public-Index-Parity-current.*` confirms the public index mirrors and non-release sentinel values agree with eligibility and manifest counts.
- `META/Governance-Consistency-Audit-current.*` confirms governance ledgers agree before public expansion.
- `META/Package-Dependency-Graph-current.*` records dependency and inventory edges for generated outputs, public allowlist files, ledger mirrors, frontmatter surfaces, and tools.

## rev0056 field-schema consistency

`META/Field-Schema-Consistency-Audit-current.*` checks that exact field-schema targets match current table headers and that schema companions exist.


## rev0056 traceability instruments

`META/Path-Reference-Audit-current.*`, `META/Rule-Gate-Traceability-current.*`, `META/Tool-Run-Matrix-current.*`, and `META/Required-Document-Coverage-current.*` add a handoff-integrity layer above field/schema validation. They ask whether paths resolve, rules point to gates/tools/reports, tools are classified, and required public/governance/front-door documents remain present.
## rev0057 audit selftest and rebuild-readiness additions

- `META/Audit-Selftest-current.*` records controlled-mutation tests proving selected auditors fail when known defects are injected into temporary package copies.
- `META/Rebuild-Readiness-Audit-current.*` checks generated-artifact specs, generator/input paths, companion triads, CLI/write modes, duplicate artifact declarations, and obvious nondeterministic primitives.



## rev0058 release proof instruments

rev0058 adds four meta instruments:

- `META/Policy-Assertion-Matrix-current.*` maps high-level release claims to gates, tools, and reports.
- `META/Regeneration-Sequence-Plan-current.*` records a deterministic, plan-only report regeneration order.
- `META/Archive-Build-Manifest-current.*` records root/export alignment, archive posture, public allowlist equality, and deterministic build policy.
- `META/Selftest-Coverage-Matrix-current.*` maps critical release gates to controlled-mutation selftests.

## rev0059 release-closure instruments

rev0059 adds three meta instruments:

- `META/Checksum-Scope-Audit-current.*` audits whether `SHA256SUMS.txt` covers the complete stable file scope without extra/archive/bytecode/path-traversal entries.
- `META/Public-Negative-Corpus-current.*` runs representative unsafe public-release fixtures through the public-release linter.
- `META/Release-Evidence-Closure-current.*` closes the release-gate evidence loop across gates, policy assertions, selftests, provenance, and package-file inventory.
## rev0076 source-health instruments

`Source-Maintenance-Priority-current.*` is the action queue for concrete source-health work. `Source-Preservation-Status-current.*` is now archive/preservation-specific instead of a duplicate of freshness status. `Source-Freshness-Preservation-current.*` remains the freshness/status surface.
