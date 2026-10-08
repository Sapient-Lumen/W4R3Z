# Scenario — security and docs surfaces still need a task-fit review packet

Question:
- if a crate has a docs.rs page, rustdoc JSON, a Security tab, and Trusted Publishing signals, what packet is still missing before another engineer can honestly answer “should we use this crate for this task?”

Why this belongs here:
- current official surfaces increasingly expose useful structure, but they do not flatten into one task-fit verdict.
- docs.rs tells us about hosted docs surfaces and recipe choices.
- crates.io can now expose advisories, publishing posture, and publication timing.
- none of that alone says whether a crate is the right choice for a specific team, workload, target, or review standard.

Expected packet behavior:
- the knowledge pack should emit a `review-packet.manifest.json` that names the compact bundle another person receives;
- the packet should link to `query-support.matrix.json`, `claim-trace.report.json`, `citation-locator.receipt.json`, and `answer-boundary.note.md`;
- `security_posture` and `task_fit` should remain separate query classes;
- the packet should mark performance, safety, migration, and hard-domain suitability as manual-review-only unless there is explicit supporting basis.

What this scenario guards against:
- mistaking “well documented” for “good task fit”;
- mistaking “no known advisories” for “appropriate choice”;
- mistaking “trusted publishing enabled” for “operationally reviewed”; 
- exporting an assistant-ready slice that cannot say what it must refuse to answer.

Relevant sources:
- docs.rs rustdoc JSON
- docs.rs metadata
- docs.rs builds
- crates.io development update
- Rust challenges
