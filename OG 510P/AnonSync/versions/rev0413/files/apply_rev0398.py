from pathlib import Path

root = Path(__file__).resolve().parent

def prepend(path: str, text: str):
    p = root / path
    old = p.read_text(encoding='utf-8')
    p.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

def write(path: str, text: str):
    p = root / path
    p.write_text(text.strip() + '\n', encoding='utf-8')

readme_add = '''## Revision addendum after rev0397 — evidence synthesis, corroboration, contradiction, and integrated-claim truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **evidence synthesis truth**.
It does eight things in one tranche:

1. Continues the archive after rev0397 with a new page family centered on what happens *after* packets have been received and intake-tested but *before* the operator is allowed to speak in one merged sentence.*
2. Tightens the non-clone line again: borrow Resilio's candor that graphs, peer/state surfaces, history, notifications, logs, dumps, mobile captures, NAS artifacts, and iperf runs can all matter; refuse any contract where the operator still has to reconstruct `which packets are genuinely independent, which merely duplicate one another, which conflict, and what strongest integrated sentence survives all of them together?` from scattered support pages and UI fragments.
3. Adds one new **Resilio evaluation** document focused on why current evidence-synthesis truth is still too fragmented to clone even though the source artifacts are useful.
4. Adds five new **interface specs** for evidence synthesis contract sheet, corroboration/conflict review, integrated-claim proof, synthesis timeline, and synthesis lineage receipt.
5. Makes one hard product decision explicit: **multiple packets do not average into truth.**
6. Makes another hard product decision explicit: **duplicate support, independent corroboration, and contradiction stay separate.**
7. Makes a third hard product decision explicit: **one unresolved conflict can keep the stronger sentence blocked even when many weaker packets point the same way.**
8. Packages the result as another continuation archive whose new tranche makes the `packet set / independence / corroboration / contradiction / synthesis ceiling / unresolved conflict` seam explicit in the reading order and page family.

New docs in this tranche:

- `1528-resilio-evidence-synthesis-corroboration-contradiction-and-integrated-claim-fragmentation-evaluation.md`
- `1529-evidence-synthesis-contract-sheet-page-target-question-packet-set-and-weighted-basis-interface-spec.md`
- `1530-corroboration-and-conflict-review-page-independent-support-duplicates-and-unresolved-mismatch-interface-spec.md`
- `1531-integrated-claim-proof-page-merged-basis-open-conflicts-and-ceiling-interface-spec.md`
- `1532-evidence-synthesis-timeline-page-arrival-supersession-corroboration-conflict-and-claim-shift-events-interface-spec.md`
- `1533-evidence-synthesis-lineage-receipt-page-packet-set-weighted-basis-and-blocked-stronger-sentences-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's artifact diversity and troubleshooting candor**
- **do not clone Resilio's evidence-synthesis and integrated-claim contract**
'''

status_add = '''## Revision addendum — status shift toward evidence synthesis and integrated-claim truth after rev0397

The next seam after packet intake and supplement-loop truth is now explicit:

- the archive can already say whether one packet is received, opened, validated, fit for the named question, and strong enough for a bounded claim
- it still needed to own the harder truth where **several packets now exist at once** and the operator must decide whether they actually strengthen, merely repeat, or actively undermine one another

This pass turns that gap into a first-class product object: **evidence synthesis truth**.

What is newly true in the archive:

- operators can now compile several packets and witness surfaces into one explicit synthesis set rather than a vague `we looked at logs and graphs` story
- duplicate support and independent corroboration can now stay visibly separate instead of being counted together
- contradictions can now stay alive as first-class blockers even when many weaker packets appear to align
- the strongest safe integrated sentence can now remain explicitly smaller than the most optimistic reading of any one packet
- later operators can now see which packets were relied on, which were superseded, which were discounted, which conflicts remained unresolved, and exactly why the merged claim ceiling stopped where it did

New docs in this tranche:

- `1528-resilio-evidence-synthesis-corroboration-contradiction-and-integrated-claim-fragmentation-evaluation.md`
- `1529-evidence-synthesis-contract-sheet-page-target-question-packet-set-and-weighted-basis-interface-spec.md`
- `1530-corroboration-and-conflict-review-page-independent-support-duplicates-and-unresolved-mismatch-interface-spec.md`
- `1531-integrated-claim-proof-page-merged-basis-open-conflicts-and-ceiling-interface-spec.md`
- `1532-evidence-synthesis-timeline-page-arrival-supersession-corroboration-conflict-and-claim-shift-events-interface-spec.md`
- `1533-evidence-synthesis-lineage-receipt-page-packet-set-weighted-basis-and-blocked-stronger-sentences-interface-spec.md`

The newest hardening move is important:

- **multiple packets do not average into truth**
- **duplicate support, independent corroboration, and contradiction are not interchangeable**
- **one unresolved conflict can keep the stronger sentence blocked even when the packet count looks impressive**
'''

resilio_eval_add = '''## Revision addendum — Resilio evidence synthesis, corroboration, contradiction, and integrated-claim evaluation after rev0397

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's artifact diversity and troubleshooting candor**
- **do not clone Resilio's evidence-synthesis and integrated-claim contract**

This time the key evidence cluster is:

- `Send info to Support team` still groups several artifact classes — mobile logs, iperf3 runs, automatic log sending, manual log sending, crash reports, and NAS core dumps — as separate articles rather than one synthesis workspace
- `Collecting debug logs automatically` still asks for peer role, timestamps, problem description, and affected shares/files, while `Collecting debug logs manually` still varies artifact paths by desktop, service principal, config `storage_path`, NAS, and Android
- `Collecting crash reports, mini-dumps and core dumps` and `Collecting core dump on NAS devices` still introduce heavier artifact classes with their own path and handling rules
- `Measuring network performance with iperf3` still adds a separate network-performance artifact that only answers one slice of the diagnostic picture
- `Performance overview` still exposes short-window real-time graphs and peer/disk metrics that are useful for troubleshooting but live on a different surface from support packets
- `Sync Main View (Desktop)` still exposes search, notifications, online-vs-total peer counts, and a 30-day History lane as yet another witness surface
- `Errors & Troubleshooting` still clusters symptom and support pages as separate article families rather than one merged evidence-adjudication workspace
- current support articles still say direct technical support is only for Sync Business and not Sync v3, which further pushes synthesis burden back onto the operator

So current Resilio still deserves credit for exposing many useful witness planes.
But it still does not own one operator-facing answer to:

> given several packets and witness surfaces at once, which ones are independent, which merely restate the same root observation, which conflict, and what strongest integrated sentence survives after weighting all of them together?

That is why this pass again strengthens the non-clone line.
'''

scorecard_add = '''## Addendum after rev0397 — why evidence synthesis now sits on the non-clone side

Resilio still earns credit for exposing many useful witness planes: main-view status, History, performance graphs, logs, dumps, NAS artifacts, mobile captures, and network tests.
Those stay on the **borrow** side.

What stays on the **do not clone** side is the synthesis contract:

- current docs still make the operator decide informally whether two packets are independent or merely duplicates
- graph evidence, history/status evidence, support packets, and network tests still live on different surfaces with no canonical weighting object
- conflict handling still has to be reconstructed from article reading and operator memory rather than one integrated-claim review
- packet count can still look persuasive even when one unresolved contradiction should cap the sentence much lower

So the line hardens again:

- **borrow evidence diversity and troubleshooting candor**
- **do not clone a product shape where corroboration, contradiction, and merged-claim ceiling live outside the operator workspace**
'''

clone_veto_add = '''## Addendum after rev0397 — new clone-veto test for evidence synthesis truth

A borrowed interface fails the clone test if it can intake packets one by one but cannot synthesize them honestly.
The new veto questions are:

- can the operator distinguish duplicate support from genuinely independent corroboration?
- can one unresolved contradiction keep the stronger sentence blocked even when many weaker packets align?
- can the interface explain why a graph, log, dump, queue view, or network test received the weight it did?
- can superseded or stale packets remain visible without silently poisoning the merged claim?
- can the interface preserve one durable synthesis receipt instead of forcing later readers to replay the whole packet history?

If the answer is no, the interface is still cloning Resilio's scattered evidence-synthesis shape too closely.
'''

product_add = '''## Product-direction addendum after rev0397 — evidence must converge into an explicit synthesis object

AnonSync should not let packet intake masquerade as integrated belief.
The product direction is now explicit:

- **evidence synthesis is first-class**
- **duplicate support, independent corroboration, contradiction, and unknown relation remain separate**
- **one integrated claim must publish both its weighted basis and its unresolved conflicts**
- **packet count is never a substitute for independence or fit**
- **every meaningful merged sentence needs one receipt preserving the exact packet set, weighting basis, supersessions, and blocked stronger sentences**

That means future interface work should keep one stable family for:

- synthesis-set shaping from multiple packets and witness planes
- corroboration-versus-duplication review
- contradiction handling and discount reasons
- integrated-claim proof and ceiling publication
- synthesis drift when new packets arrive or older packets stale out
- durable lineage receipts for later disputes, appeals, or certification work

The product should never force the operator to synthesize logs, graphs, history, queue observations, and network tests purely through memory and side conversation.
'''

sources_add = '''## rev0398 source set — evidence synthesis, corroboration, contradiction, and integrated-claim truth

The most load-bearing source set for this pass was:

- Resilio's current `Send info to Support team` section page, which still groups mobile logs, iperf3, automatic and manual debug logs, crash reports, and NAS dump flows as separate support articles rather than one synthesis workspace.
- Resilio's current `Collecting debug logs automatically` article, which still requests peer role, timestamps, problem description, and affected shares/files, making one support packet richer but still separate.
- Resilio's current `Collecting debug logs manually` article, which still varies artifact retrieval by desktop, service principal, config-defined `storage_path`, NAS, and Android lane.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article, which still introduces another heavier artifact class with its own storage-path logic.
- Resilio's current `Measuring network performance with iperf3` article, which still adds a distinct performance-test artifact that only answers one slice of a case.
- Resilio's current `Performance overview` article, which still exposes 1-minute, 10-minute, and 1-hour real-time troubleshooting graphs on a separate UI surface.
- Resilio's current `Sync Main View (Desktop)` article, which still exposes search, notifications, peer counts, current activity, and a 30-day History lane as another witness surface.
- Resilio's current `Errors & Troubleshooting` category page, which still presents symptom and support materials as separate article families rather than one integrated evidence-adjudication object.
- Resilio's current support articles, which still say direct technical support is available only for Sync Business and not Sync v3 users.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful witness planes
- but current Resilio still answers `which packets are actually independent, which merely duplicate each other, which conflict, and what strongest integrated claim survives all of them together?` too diffusely
- AnonSync should therefore prefer explicit evidence-synthesis sheets, corroboration/conflict reviews, integrated-claim proofs, synthesis timelines, and durable lineage receipts over scattered support instructions and operator memory

Primary sources:

- Send info to Support team
  https://help.resilio.com/hc/en-us/sections/201494276-Send-info-to-Support-team

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Measuring network performance with iperf3
  https://help.resilio.com/hc/en-us/articles/1500007478562-Measuring-network-performance-with-iperf3

- Performance overview
  https://help.resilio.com/hc/en-us/articles/360001331930-Performance-overview

- Sync Main View (Desktop)
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting
'''

write('docs/1528-resilio-evidence-synthesis-corroboration-contradiction-and-integrated-claim-fragmentation-evaluation.md', '''# Resilio evidence synthesis, corroboration, contradiction, and integrated-claim fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- choose the next best discriminator
- capture and package evidence honestly
- preserve custody and redaction truth
- judge whether one packet is decision-grade for a named question
- request the cheapest useful supplement when one packet is not enough

What it still lacked was the next ordinary operator answer:

> now that several packets and witness planes exist, which ones genuinely reinforce one another, which just repeat the same root observation, which actively conflict, and what strongest integrated sentence survives the whole set together?

That is the seam this pass locks.
A product that can intake packets one by one but cannot synthesize them honestly still leaves too much truth in chat, analyst memory, and support folklore.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful witness planes, but mostly as separate surfaces rather than one synthesis workspace:

- `Send info to Support team` still groups mobile logs, iperf3, automatic log sending, manual log sending, crash reports, and NAS core-dump flows as separate support articles.
- `Collecting debug logs automatically` still asks for peer role, timestamps, detailed problem description, and affected shares/files, which can make one packet richer but still does not merge it with other witness types.
- `Collecting debug logs manually` still varies log retrieval by desktop, service principal, config `storage_path`, NAS, and Android lane, which means one packet may already come from a different world than another.
- `Collecting crash reports, mini-dumps and core dumps` still introduces a heavier artifact class with its own path, crash posture, and storage semantics.
- `Measuring network performance with iperf3` still adds a separate network-performance artifact that can be decisive for one question while being largely orthogonal to another.
- `Performance overview` still exposes short-window real-time graphs and peer/disk metrics useful for troubleshooting, but on a different surface from support packets.
- `Sync Main View (Desktop)` still exposes search, notifications, online-vs-total peer counts, current activity, and a 30-day History lane as yet another witness surface.
- `Errors & Troubleshooting` still clusters symptom and support pages as separate article families rather than a merged evidence-adjudication object.
- current support articles still say direct technical support is only for Sync Business and not Sync v3, which pushes even more synthesis burden back onto the operator.

## What current Resilio still gets right

### 1) It preserves witness diversity

Logs, dumps, performance tests, peer lists, history, warnings, and graphs are not collapsed into one bland blob.
That is worth borrowing.

### 2) It makes source-world differences real

Service-principal paths, config-defined storage paths, mobile capture lanes, NAS-local storage, and UI witness planes all matter.
That honesty is useful.

### 3) It reveals that one artifact rarely answers everything

A packet can be strong for one question and weak for another.
A network test can be decisive for throughput but not for state corruption.
A history lane can show activity but not root cause.
That realism matters.

## Where current Resilio still fragments the operator answer

### A) Synthesis still lives in the operator's head

Current Resilio exposes many evidence ingredients, but still leaves the receiver to decide informally which ones are independent and which are just restating the same situation from a new angle.
The synthesis judgment is implied, not normalized.

### B) Duplicate support and corroboration still blur together

A main-view peer count, a performance graph, and a log excerpt may all derive from the same underlying connectivity condition.
Current Resilio shows them separately, but still does not force the operator to say whether the support is genuinely independent.

### C) Contradictions still lack a canonical home

A packet that suggests healthy transport can coexist with a history lane that shows stalled or missing work.
A log packet from one world can coexist with a UI witness from another.
Current Resilio provides the artifacts, but still does not give one place to say which contradiction remains unresolved and how it caps the merged sentence.

### D) Weighting still has to be improvised

A crash dump, a 15-minute debug log, an iperf run with Sync shut down, a 30-day History view, and a 1-hour graph window do not all carry the same decisional force.
Current Resilio never really denies this, but still does not normalize the weighting contract.

## Hard product decision unlocked by this pass

AnonSync should compile every serious multi-packet reading into a first-class **evidence synthesis** object that separately expresses:

- target question and candidate stronger sentence
- participating packet and witness ids
- packet freshness and world fit for each source
- relation class between each source pair
- duplicate-versus-independent support judgment
- contradiction and open mismatch list
- discount reasons and supersession reasons
- weighted basis for the merged sentence
- strongest safe integrated sentence
- strongest blocked sentence and the conflict or gap still blocking it

## Replacement line for AnonSync

Borrow from Resilio:

- its candor that different witness planes really do matter
- its willingness to expose graphs, peer status, history, logs, dumps, and network tests as separate diagnostic ingredients
- its realism that some packets are platform-specific, world-specific, or question-specific

Do not clone from Resilio:

- any workflow where synthesis only happens in human memory
- any contract where packet count can masquerade as evidentiary strength
- any interface where duplicate support and independent corroboration blur together
- any product shape where contradictions remain visible only as scattered notes instead of merged-claim blockers

AnonSync should instead ship explicit pages for:

- evidence synthesis contract sheet
- corroboration and conflict review
- integrated-claim proof
- synthesis timeline
- synthesis lineage receipt
''')

write('docs/1529-evidence-synthesis-contract-sheet-page-target-question-packet-set-and-weighted-basis-interface-spec.md', '''# Evidence synthesis contract sheet page: target question, packet set, and weighted basis interface spec

## Purpose

Once several packets or witness planes exist for the same live question, the operator still needs one page that answers:

> what exactly are we trying to say, which packets are in the synthesis set, and on what basis are we allowed to merge them into one sentence at all?

## Core decision

AnonSync must expose one first-class **Evidence synthesis contract sheet** whenever two or more evidence packets, witness panes, or support artifacts are being interpreted as one basis for a decision, verdict, escalation, certification, or doctrine move.

## Fixed page order

1. **Synthesis header**
2. **Target-question card**
3. **Packet-set card**
4. **Relation-map card**
5. **Weighting-basis card**
6. **Open-conflict card**
7. **Decision sentence**

### 1) Synthesis header

Show:

- synthesis sheet id
- target case or decision id
- synthesis owner
- current synthesis posture
- source packet count
- independent-support count
- contradiction count
- current strongest safe integrated sentence
- strongest blocked sentence

Supported `synthesis_posture` values:

- `packet-set-opened`
- `relation-mapping-in-progress`
- `weighted-basis-drafted`
- `conflict-blocked`
- `bounded-integrated-claim-ready`
- `integrated-claim-ready-with-reservations`
- `superseded-or-stale`

Hard rule:

The header may not describe a synthesis as `ready` until at least one explicit relation judgment exists for every packet included in the active set.

### 2) Target-question card

Required rows:

- target question or decision
- candidate stronger sentence sought
- currently safe weaker sentence
- governing world assumptions
- governing scope
- excluded questions

Supported `synthesis_target_class` values:

- `diagnosis`
- `control-trust`
- `rollout-health`
- `dispute-verdict`
- `fulfillment-acceptance`
- `precedent-application`
- `certification`
- `external-escalation`

Hard rule:

One synthesis object answers one named target question.
It may support adjacent questions, but it cannot claim to answer them implicitly.

### 3) Packet-set card

Render one row per packet or witness source.
Required fields:

- source id
- source type
- source world or lane
- capture or observation window
- freshness posture
- fit posture for this question
- current participation status

Supported `source_type` values:

- `debug-log-packet`
- `dump-or-crash-packet`
- `network-test-packet`
- `ui-history-witness`
- `ui-graph-witness`
- `peer-state-witness`
- `queue-or-status-witness`
- `operator-note`
- `external-support-note`

Supported `participation_status` values:

- `active-basis`
- `context-only`
- `discounted`
- `superseded`
- `held-out-for-conflict`
- `rejected-wrong-world`

Hard rule:

A packet may not silently disappear from the set once it has influenced synthesis.
It must become `discounted`, `superseded`, or `rejected` explicitly.

### 4) Relation-map card

For each material source pair, require a relation judgment.
Supported `relation_class` values:

- `independent-corroboration`
- `duplicate-observation`
- `downstream-restatement`
- `partial-overlap`
- `not-comparable`
- `soft-conflict`
- `hard-conflict`
- `unknown-relation`

Hard rule:

The interface must not count `duplicate-observation` toward independent corroboration.

### 5) Weighting-basis card

Required rows:

- weighting policy used
- highest-weight sources
- discounted sources and reasons
- stale-but-still-used sources and reasons
- missing source classes that still matter
- open synthesis gap

Supported `weighting_policy` values:

- `source-rank-first`
- `freshness-first`
- `world-fit-first`
- `conflict-sensitive`
- `question-specific-custom`

Hard rule:

Any custom weighting policy must still publish why a lower-count result can outrank a higher-count result.

### 6) Open-conflict card

Required rows:

- unresolved conflict id
- conflicting source ids
- conflict description
- what sentence it blocks
- cheapest resolution path
- safe fallback sentence if unresolved

Supported `conflict_severity` values:

- `cosmetic`
- `bounded`
- `claim-capping`
- `route-reversing`
- `world-invalidating`

Hard rule:

A `claim-capping` or stronger conflict must appear above the final decision sentence, not below it.

### 7) Decision sentence

Render exactly two lines:

- **Strongest safe integrated sentence**
- **Strongest blocked sentence and why**

Hard rule:

If any active source remains `unknown-relation`, the decision sentence must mention the unresolved synthesis relation explicitly.
''')

write('docs/1530-corroboration-and-conflict-review-page-independent-support-duplicates-and-unresolved-mismatch-interface-spec.md', '''# Corroboration and conflict review page: independent support, duplicates, and unresolved mismatch interface spec

## Purpose

The operator needs one review page that answers:

> which sources truly reinforce each other, which only look additive, which conflict, and what is the exact cost of leaving a mismatch unresolved?

## Core decision

AnonSync must expose one first-class **Corroboration and conflict review** whenever a synthesis set contains two or more active sources.

## Fixed page order

1. **Review header**
2. **Independent-support section**
3. **Duplicate-and-restatement section**
4. **Conflict section**
5. **Discount-and-holdout section**
6. **Synthesis consequence section**
7. **Review sentence**

### 1) Review header

Show:

- target synthesis id
- active source count
- independent-support count
- duplicate/restatement count
- open conflict count
- current merged-claim ceiling

### 2) Independent-support section

For each source cluster judged genuinely independent, show:

- cluster id
- participating source ids
- independence basis
- question slice supported
- ceiling gained by this corroboration

Supported `independence_basis` values:

- `different-capture-channel`
- `different-observer-plane`
- `different-runtime-world`
- `different-time-window-same-conclusion`
- `different-measurement-method`
- `explicitly-not-independent`

Hard rule:

Two packets produced by the same underlying channel with only superficial reformatting must not be labeled as independent.

### 3) Duplicate-and-restatement section

For each duplicate or downstream restatement cluster, show:

- cluster id
- source ids
- common root observation
- why these do not add independence
- whether any one source is still retained as the canonical representative

Supported `duplicate_class` values:

- `same-packet-new-format`
- `same-event-new-view`
- `ui-restates-log`
- `history-restates-status`
- `summary-restates-raw`
- `unknown-possible-duplicate`

Hard rule:

A cluster marked `unknown-possible-duplicate` may not be counted toward strong corroboration.

### 4) Conflict section

For each material contradiction, show:

- conflict id
- source ids in tension
- exact propositions in conflict
- severity
- leading interpretations still live
- cheapest discriminator that would reduce this conflict
- current claim ceiling while unresolved

Supported `conflict_resolution_posture` values:

- `needs-no-action`
- `needs-cheap-discriminator`
- `needs-heavy-capture`
- `needs-route-reversal`
- `must-cap-claim-until-later`

Hard rule:

If the conflict is `route-reversing` or `world-invalidating`, the interface must publish at least one surviving alternative interpretation, not only the currently favored one.

### 5) Discount-and-holdout section

List sources that are not in the active weighted basis.
Required rows:

- source id
- holdout reason
- whether it still shadows the claim
- re-entry trigger

Supported `holdout_reason` values:

- `stale-window`
- `wrong-world`
- `wrong-scope`
- `duplicate-not-needed`
- `conflict-not-resolved`
- `inferior-version`
- `transform-too-lossy`

Hard rule:

A held-out source that still shadows the claim must continue to cap the stronger sentence until formally cleared or superseded.

### 6) Synthesis consequence section

Required rows:

- claim strengthened by independent support
- claim still capped by conflict
- sentence that would become safe if the cheapest discriminator landed
- sentence that remains impossible even after that discriminator

Hard rule:

The review must separate `claim could strengthen` from `claim has strengthened`.

### 7) Review sentence

Render exactly three lines:

- **What is genuinely corroborated**
- **What is merely repeated**
- **What still conflicts and what sentence that conflict blocks**
''')

write('docs/1531-integrated-claim-proof-page-merged-basis-open-conflicts-and-ceiling-interface-spec.md', '''# Integrated claim proof page: merged basis, open conflicts, and ceiling interface spec

## Purpose

The operator needs one proof page that turns a multi-packet reading into one durable answer:

> what exact integrated claim is justified, by what weighted basis, and how far does that claim stop because of unresolved conflict or missing independence?

## Core decision

AnonSync must expose one first-class **Integrated claim proof** whenever a synthesis set produces any nontrivial merged sentence that others may rely on.

## Fixed page order

1. **Proof header**
2. **Integrated-claim card**
3. **Weighted-basis card**
4. **Conflict-ceiling card**
5. **Alternative-interpretation card**
6. **Reliance-envelope card**
7. **Proof sentence**

### 1) Proof header

Show:

- proof id
- synthesis source id
- proof owner
- issuance time
- current proof posture
- current strongest safe integrated sentence
- strongest blocked sentence

Supported `proof_posture` values:

- `draft`
- `bounded-proof-issued`
- `reservation-heavy-proof-issued`
- `proof-recalled`
- `proof-superseded`
- `proof-expired`

### 2) Integrated-claim card

Required rows:

- exact integrated sentence
- target question answered
- scope answered
- worlds covered
- worlds excluded
- time window covered

Supported `integrated_claim_grade` values:

- `weak-pattern-only`
- `bounded-supported`
- `strongly-corroborated`
- `conflict-capped`
- `temporary-synthesis-only`

Hard rule:

A `strongly-corroborated` claim must include at least two active source clusters labeled `independent-corroboration`.

### 3) Weighted-basis card

Render the active basis in descending decisional weight.
Required fields per row:

- source id
- source role in proof
- source weight explanation
- freshness posture
- relation status to other top-weight sources

Supported `source_role_in_proof` values:

- `lead-basis`
- `corroborating-basis`
- `context-basis`
- `conflict-shadow`
- `discounted-reference`

Hard rule:

The page must explain why the top-weight source outranks any more numerous lower-weight cluster.

### 4) Conflict-ceiling card

Required rows:

- unresolved conflict ids
- what each conflict blocks
- fallback sentence that remains safe
- recall or downgrade trigger

Hard rule:

If the proof remains conflict-capped, the blocked stronger sentence must be displayed in the same visual block as the issued sentence.

### 5) Alternative-interpretation card

Show the strongest live alternatives that were not fully eliminated.
Required rows:

- alternative interpretation
- why still live
- what evidence weighs against it
- what evidence would kill it

Hard rule:

Alternative interpretations may not be omitted merely because one integrated claim is favored.

### 6) Reliance-envelope card

Required rows:

- who may rely on this proof
- what decisions it can support
- what decisions it cannot support
- freshness horizon
- supersession trigger

Hard rule:

A proof issued for one question may not silently authorize a broader policy or certification claim.

### 7) Proof sentence

Render exactly three lines:

- **Issued integrated claim**
- **Why this merged basis is enough for that sentence**
- **What stronger sentence is still blocked and by what unresolved conflict or missing independence**
''')

write('docs/1532-evidence-synthesis-timeline-page-arrival-supersession-corroboration-conflict-and-claim-shift-events-interface-spec.md', '''# Evidence synthesis timeline page: arrival, supersession, corroboration, conflict, and claim-shift events interface spec

## Purpose

The operator needs one timeline that answers:

> how did the merged claim change as packets arrived, were superseded, corroborated each other, or opened new contradictions?

## Core decision

AnonSync must expose one first-class **Evidence synthesis timeline** for every synthesis object that survives beyond one reading session.

## Fixed page order

1. **Timeline header**
2. **Packet-arrival lane**
3. **Relation-change lane**
4. **Claim-shift lane**
5. **Conflict lane**
6. **Supersession-and-expiry lane**
7. **Timeline sentence**

### 1) Timeline header

Show:

- synthesis id
- first packet arrival time
- latest packet or witness arrival time
- latest integrated claim time
- current synthesis posture
- current strongest safe integrated sentence

### 2) Packet-arrival lane

Supported `arrival_event` values:

- `packet-arrived`
- `packet-opened`
- `packet-validated`
- `packet-added-to-active-basis`
- `packet-held-out`
- `packet-rejected`

### 3) Relation-change lane

Supported `relation_change_event` values:

- `duplicate-marked`
- `independent-corroboration-established`
- `soft-conflict-opened`
- `hard-conflict-opened`
- `unknown-relation-cleared`
- `relation-reweighted`

### 4) Claim-shift lane

Supported `claim_shift_event` values:

- `sentence-strengthened`
- `sentence-weakened`
- `sentence-narrowed`
- `sentence-broadened-with-proof`
- `fallback-claim-only`
- `integrated-claim-issued`

Hard rule:

A sentence may not be marked `strengthened` unless the timeline records whether the change came from new independence, resolved conflict, improved freshness, or scope narrowing.

### 5) Conflict lane

Supported `conflict_event` values:

- `conflict-opened`
- `conflict-reclassified`
- `conflict-capped-claim`
- `conflict-resolved`
- `conflict-reopened`
- `alternative-interpretation-killed`

### 6) Supersession-and-expiry lane

Supported `supersession_event` values:

- `packet-superseded`
- `packet-expired`
- `proof-recalled`
- `proof-reissued`
- `basis-shifted`

Hard rule:

When a source expires or is superseded, the timeline must show whether the merged sentence stayed the same, shrank, or required reissue.

### 7) Timeline sentence

Render exactly two lines:

- **How the integrated claim reached its current ceiling**
- **What event would most likely change that ceiling next**
''')

write('docs/1533-evidence-synthesis-lineage-receipt-page-packet-set-weighted-basis-and-blocked-stronger-sentences-interface-spec.md', '''# Evidence synthesis lineage receipt page: packet set, weighted basis, and blocked stronger sentences interface spec

## Purpose

Once a multi-packet reading has produced a merged sentence, later operators need one durable receipt that answers:

> exactly which packet set produced this claim, what weight basis was used, what conflicts remained open, and what stronger sentence stayed blocked?

## Core decision

AnonSync must issue one first-class **Evidence synthesis lineage receipt** for every integrated claim proof that can influence later dispute, escalation, precedent, certification, or reliance work.

## Fixed page order

1. **Receipt header**
2. **Packet-set snapshot**
3. **Weighted-basis snapshot**
4. **Conflict-and-gap snapshot**
5. **Claim-envelope snapshot**
6. **Successor-proof hook**
7. **Receipt sentence**

### 1) Receipt header

Show:

- receipt id
- source synthesis id
- source proof id
- issued time
- receipt owner
- current receipt posture

Supported `receipt_posture` values:

- `active-reference`
- `reference-with-reservations`
- `superseded-reference`
- `expired-reference`
- `recalled-reference`

### 2) Packet-set snapshot

Required rows:

- active source ids at issuance
- held-out source ids at issuance
- superseded source ids already known
- source relation summary

Hard rule:

The receipt must preserve the actual packet set used at issuance even if later packets arrive.

### 3) Weighted-basis snapshot

Required rows:

- lead-basis sources
- corroborating sources
- duplicate clusters not counted twice
- discounted sources and reasons
- stale sources still tolerated and why

Hard rule:

A later reader must be able to tell why the issued claim did not simply track source count.

### 4) Conflict-and-gap snapshot

Required rows:

- unresolved conflict ids
- missing independence still desired
- missing source class still desired
- blocked stronger sentences

Hard rule:

If the issued claim was conflict-capped, the receipt must preserve the capped alternative sentence in plain language.

### 5) Claim-envelope snapshot

Required rows:

- exact issued integrated sentence
- scope covered
- worlds covered
- excluded scope
- freshness horizon
- downgrade or recall triggers

### 6) Successor-proof hook

Required rows:

- next proof id if any
- what changed
- whether the new proof strengthened, weakened, narrowed, or only refreshed the old sentence

Hard rule:

The successor hook must preserve continuity without erasing the older synthesis basis.

### 7) Receipt sentence

Render exactly three lines:

- **This is the integrated sentence that was actually issued**
- **This is the weighted packet basis that made it safe**
- **This is the stronger sentence that remained blocked and why**
''')

prepend('README.md', readme_add)
prepend('docs/00-status.md', status_add)
prepend('docs/10-resilio-sync-evaluation.md', resilio_eval_add)
prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', clone_veto_add)
prepend('docs/20-product-direction.md', product_add)
prepend('docs/sources.md', sources_add)
