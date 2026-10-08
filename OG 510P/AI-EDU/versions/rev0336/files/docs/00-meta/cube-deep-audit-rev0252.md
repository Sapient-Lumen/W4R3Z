# Cube deep audit rev0252

## Posture

Rev0252 is a smoke-triage firebreak and waste audit. The archive is still
ready-but-not-closed. `FT-0181` remains live because there is no real `SRC2+`
owner-reviewed pilot packet, no real owner-returned eight-row CSV, no accepted
import, no live-window readout, and no closure-ready signoff.

The concrete repair in this revision is narrow: normal owner-reply triage now
refuses archive smoke fixtures and smoke-labelled CSV content as `SRC0-SMOKE`
non-evidence. The smoke harness can still opt in for plumbing rehearsal, but
that route is deliberately labelled as fixture-only and cannot create a real
packet claim.

## What was missing

The archive has strong internal controls, but the missing object is still the
same external object: one real, minimized owner reply. The next archive motion
should be evidence-first, not doctrine-first. Send or adapt the eight-row
`AIEDU-SR-003` owner request, run local intake only if a real CSV comes back,
and record `NO-OWNER-PACKET` after the existing one-follow-up clock if no viable
packet arrives.

The second missing piece is a deployment inventory and risk-classification
crosswalk that can be updated without rewriting doctrine. Education use cases
that evaluate learning, determine admission or assignment, assess education
level, or monitor test behavior need a visibly higher control lane than sandbox
hinting, internal drafting, or accessibility-neutral staff support.

The third missing piece is a measurement design that separates operational
plumbing from learning or service outcomes. This archive repeatedly says no
synthetic fixture proves effectiveness; the next useful step is to name which
minimal aggregate signals could support only bounded operational claims, which
signals would be insufficient, and which claims would remain forbidden even
after a small pilot.

The fourth missing piece is a maintainer burden budget. There are 456 tracked
files before this new audit, including 282 Markdown files, 102 JSON files, and
69 Python tools. `FOLLOWTHROUGH_QUEUE.json` has 198 items, with 197 done and one
live item. That is powerful as a memory system, but the live action is still a
single external packet. A future operator needs a fast lane that protects the
field ask from being buried under the control plane.

The fifth missing piece is a scheduled legal/context watch rather than a static
bibliography. The online environment now includes active EU AI Act application
timelines, U.S. education guidance on AI use, COPPA rule changes, and fast-moving
school-district privacy defaults. These need a small watchlist and refresh clock
instead of more one-off prose.

## What went severely wrong

The standalone triage tool could previously classify the shipped synthetic smoke
fixture as `PROCEED-STAGED` and `is_real_packet: true`. Downstream receipt,
staging, and intake controls still blocked or labelled the fixture, so this did
not create accepted evidence in the archive. But it was a source-truth boundary
failure at the first classifier and could have misled an operator using the CLI
alone.

Rev0252 fixes that by adding source-truth detection in
`tools/triage_owner_reply_csv.py`. CSVs under `fixtures/` or rows labelled with
smoke-fixture language now return `BLOCK-EVIDENCE`, `stage_to_workbench: false`,
`is_real_packet: false`, and `source_truth_class: SRC0-SMOKE` unless the caller
uses the explicit smoke-only opt-in. `tools/check_owner_reply_triage.py` now
asserts that ordinary triage blocks the fixture. `tools/stage_owner_reply_csv.py`,
`tools/receipt_owner_reply_csv.py`, and `tools/smoke_owner_reply_pipeline.py`
were updated so smoke allowance is explicit and non-evidence.

A smaller but real drift bug was also found in the navigation generator:
`tools/gen_context_pack.py` hardcoded the rev0251 deep audit path. Rev0252 changes
it to compute the current audit path from `REVISION_RECEIPT.json`.

## Waste and correction opportunities

The archive is now control-heavy relative to its only live external task. Before
this new audit, `SURFACES.json` indexed 282 Markdown surfaces. The branch-family
index identified 100 branch-history surfaces across 12 families, with 50 in the
`hot_exam_recipient_followup_shells` family. This is not wrong as institutional
memory, but it is too much for the first-contact path. Future turns should avoid
adding sibling branch surfaces unless a real packet exposes a genuinely new
pattern.

A duplicate-paragraph scan found at least 73 long repeated paragraphs across
Markdown surfaces. Many repetitions are deliberate branch-tail guardrails, but
they still impose review cost. A reasonable correction over time is to move
branch-tail doctrine behind family compression pages, preserve aliases in the
archive index, and make `START_HERE.md` plus `context-pack.json` the real entry
path.

The full lint suite is useful as release discipline, but it is wasteful as a
single operator loop in this cloudtainer. Individual owner-reply checks pass in
reasonable chunks, while the monolithic suite can run long enough to obscure the
actual changed-surface signal. The next toolchain improvement should split lint
into a fast changed-surface lane, a release-control lane, and a full release lane
instead of asking every turn to re-run everything as one opaque block.

The large root ledgers and bibliography are not useless, but they should stop
growing until real evidence arrives. `ASSUMPTION_LEDGER.json` has 279 items
across active, watch, and archived-context states. The next revision should
prefer closing, tagging, or referencing existing assumptions over writing new
assumption prose.

## Online-context implications

The EU AI Act context reinforces the archive's conservative stance. Education
systems used for admission or assignment, evaluating learning outcomes, assessing
education level, or monitoring prohibited behavior during tests can fall into
high-risk areas. The EU timeline also means education-related high-risk rules are
not merely speculative future doctrine; they have an implementation clock.

NIST's AI Risk Management Framework and generative-AI profile reinforce the need
for explicit mapping from risks to controls, not just a pile of controls. The
archive has many controls; the missing upgrade is a concise crosswalk from each
active use case to risk, owner, evidence, monitor, rollback, and public-claim
ceiling.

U.S. Department of Education guidance, COPPA changes, CoSN privacy resources,
UNESCO generative-AI education guidance, and district-level rules such as NYCPS
all point in the same practical direction: minimize student data, keep humans in
oversight roles, document vendor/tool boundaries, engage stakeholders where
needed, and do not use sensitive student material as casual model-input fuel.
The archive already says these things, but it needs a refreshable watchlist and
fewer repeated restatements.

## Recommended next sequence

1. Keep `FT-0181` on the eight-row owner reply path. Do not add another first
   contact artifact unless a real owner says the current one is impossible.
2. Add a tiny legal/context watch record with refresh dates for EU AI Act,
   COPPA/student privacy, U.S. Department of Education guidance, NIST AI RMF/GAI,
   UNESCO, and local district policy.
3. Split lint into `fast-changed`, `release-controls`, and `full-release` lanes
   while preserving `tools/run_lint_suite.py` as the final gate.
4. Begin branch-tail compression only after preserving current links in
   `ARCHIVE_INDEX.md` and `BRANCH_FAMILY_INDEX.json`.
5. Freeze new doctrine until one real owner reply, one `NO-OWNER-PACKET`, or one
   real block shows what the archive actually needs next.

## Validation notes for this revision

The materially changed owner-reply checks were run individually after the patch:
triage, staging, receipt, intake bundle, workbench seed, pipeline smoke, and
`make owner-reply-smoke`. The monolithic full lint suite is still treated as a
release target, but in this cloudtainer it is slow enough to be a separate waste
item rather than a good interactive diagnostic.
