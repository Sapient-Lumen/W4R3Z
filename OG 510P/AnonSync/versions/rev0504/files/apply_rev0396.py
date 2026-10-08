from pathlib import Path

root = Path(__file__).resolve().parent

def prepend(path: str, text: str):
    p = root / path
    old = p.read_text(encoding='utf-8')
    p.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

def write(path: str, text: str):
    p = root / path
    p.write_text(text.strip() + '\n', encoding='utf-8')

readme_add = '''## Revision addendum after rev0395 — evidence packet, custody, redaction, and export truth

This continuation archive advances the doctrine by tightening another concrete non-clone seam around **evidence packet truth**.
It does eight things in one tranche:

1. Continues the archive after rev0395 with a new page family centered on what happens *after* a fact or artifact has been captured but *before* others are expected to rely on it.
2. Tightens the non-clone line again: borrow Resilio's candor that logs, dumps, mobile captures, NAS captures, feedback uploads, service-path variants, and support-routing details are all real evidence ingredients; refuse any contract where the operator still has to reconstruct `what exact artifact form are we sharing, what was redacted or transformed, which storage world produced it, and what integrity ceiling survives the export channel?` from scattered support pages.
3. Adds one new **Resilio evaluation** document focused on why current evidence-packet truth is still too fragmented to clone even though the capture instructions are useful.
4. Adds five new **interface specs** for evidence packet contract sheet, packet-shaping review, export proof, packet timeline, and packet lineage receipt.
5. Makes one hard product decision explicit: **raw capture, derived digest, redacted packet, and narrative summary are different objects.**
6. Makes another hard product decision explicit: **sent, received, opened, validated, and usable remain separate truths.**
7. Makes a third hard product decision explicit: **minimum-sufficient sharing is first-class, but every redaction or transformation must publish the diagnostic power it weakens.**
8. Packages the result as another continuation archive whose new tranche makes the `source artifact / redaction class / audience envelope / export integrity / recall boundary` seam explicit in the reading order and page family.

New docs in this tranche:

- `1516-resilio-evidence-packet-custody-redaction-and-export-fragmentation-evaluation.md`
- `1517-evidence-packet-contract-sheet-page-source-artifacts-redaction-class-and-audience-envelope-interface-spec.md`
- `1518-packet-shaping-review-page-raw-derived-redacted-and-minimum-sufficient-share-interface-spec.md`
- `1519-evidence-export-proof-page-sent-received-opened-validated-and-usable-interface-spec.md`
- `1520-evidence-packet-timeline-page-capture-redaction-export-recall-and-supersession-events-interface-spec.md`
- `1521-evidence-packet-lineage-receipt-page-custody-redaction-integrity-and-audience-boundary-interface-spec.md`

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's evidence-capture candor and channel honesty**
- **do not clone Resilio's evidence-packet and custody contract**
'''

status_add = '''## Revision addendum — status shift toward evidence packet, custody, and export truth after rev0395

The next seam after burden-aware fact acquisition is now explicit:

- the archive can already say which missing fact matters, which evidence channel is cheapest, what burden rung applies, and what stronger sentence stays blocked if heavier capture is declined
- it still needed to own the harder truth where evidence has been captured and must now be *shaped, redacted, exported, validated, and handed to an audience* without lying about what was lost in the process

This pass turns that gap into a first-class product object: **evidence packet truth**.

What is newly true in the archive:

- captured facts and artifacts can now compile into explicit packet objects rather than vague `sent logs` folklore
- operators can now separate `raw capture`, `derived digest`, `redacted packet`, `narrative summary`, and `audience-facing minimum share`
- export state can now stay visibly split across `sent`, `received`, `opened`, `validated`, and `usable`
- redaction and transformation now publish their diagnostic cost instead of hiding behind `privacy-safe` wording
- later operators can now see which storage world or runtime lane produced the packet, how it was transformed, who held custody, and what stronger evidentiary sentence the packet still cannot support

New docs in this tranche:

- `1516-resilio-evidence-packet-custody-redaction-and-export-fragmentation-evaluation.md`
- `1517-evidence-packet-contract-sheet-page-source-artifacts-redaction-class-and-audience-envelope-interface-spec.md`
- `1518-packet-shaping-review-page-raw-derived-redacted-and-minimum-sufficient-share-interface-spec.md`
- `1519-evidence-export-proof-page-sent-received-opened-validated-and-usable-interface-spec.md`
- `1520-evidence-packet-timeline-page-capture-redaction-export-recall-and-supersession-events-interface-spec.md`
- `1521-evidence-packet-lineage-receipt-page-custody-redaction-integrity-and-audience-boundary-interface-spec.md`

The newest hardening move is important:

- **raw capture, redacted packet, and narrative summary are not interchangeable**
- **minimum-sufficient sharing is allowed, but every redaction must publish what it weakens**
- **a packet exported successfully is still weaker than one the audience actually validated and could use**
'''

resilio_eval_add = '''## Revision addendum — Resilio evidence packet, custody, redaction, and export evaluation after rev0395

Another current official Resilio pass still supports the same tightened judgment:

- **borrow Resilio's evidence-capture candor and channel honesty**
- **do not clone Resilio's evidence-packet and custody contract**

This time the key evidence cluster is:

- `Collecting debug logs automatically` still routes one export path through `Preferences (Settings) > Support > Contact support`, asks the operator to include peer role, timestamps, and affected shares or files, requires the `Include logs` step explicitly, and says not to close the app or device until sending is done
- `Collecting debug logs manually` still routes another export path through manual attachment or upload, still requires enablement, restart, reproduction, and still varies the log-storage path by desktop, service principal, config `storage_path`, NAS, or Android lane
- `Collect debug logs on mobiles` still routes yet another path through a hidden `.synclogs` folder after a special debug action
- `Where to collect logs on NAS?` still says each NAS has its own local storage for `.sync` state, settings, and logs, and if the expected path is wrong the operator may need to inspect config for the real storage
- `Collecting crash reports, mini-dumps and core dumps` and `Collecting core dump on NAS devices` still introduce even heavier artifact classes, storage paths, and movement steps such as moving a dump into a public folder for download
- the current `Errors & Troubleshooting` category still groups these support-facing evidence instructions as article clusters rather than one packet-shaping workspace
- both current debug-log articles and crash-dump articles still say direct technical support is available only to Sync Business customers and not to Sync v3 users
- the current `Resilio Sync change log` still records transport-related debug-data history, including HTTPS sending for Contact Support dialog and earlier inability-to-send-feedback fixes

So current Resilio still deserves credit for exposing many useful evidence channels.
But it still does not own one operator-facing answer to:

> what exact packet are we sharing, what was redacted or transformed, which source world produced it, what export path was used, what integrity and audience ceiling survives, and how do we supersede or recall that packet later?

That is why this pass again strengthens the non-clone line.
'''

scorecard_add = '''## Addendum after rev0395 — why evidence packet truth now sits on the non-clone side

Resilio still earns credit for candid capture instructions, multiple export channels, and real platform-specific artifact paths.
Those stay on the **borrow** side.

What stays on the **do not clone** side is the packet contract:

- raw logs, mobile captures, service-world logs, NAS dumps, and support feedback uploads still live as separate instructions
- current docs still make the operator infer what packet form is minimally sufficient for which audience
- storage-world and service-principal differences still matter to packet meaning but are not normalized into one custody object
- `sent logs` still does too much work because transport success, audience receipt, packet usability, and evidentiary strength are not unified

So the line hardens again:

- **borrow evidence capture and export candor**
- **do not clone a product shape where packet form, redaction cost, custody, and export integrity live outside the operator workspace**
'''

clone_veto_add = '''## Addendum after rev0395 — new clone-veto test for evidence packet and custody truth

A borrowed interface fails the clone test if it can capture evidence but cannot shape and export it honestly.
The new veto questions are:

- can the operator distinguish raw capture from redacted, summarized, or derived packet forms?
- can the interface publish exactly what diagnostic power each transformation weakens?
- can the product preserve source-world and custody continuity across service, config, mobile, and NAS lanes?
- can the interface tell the difference between `sent`, `received`, `opened`, `validated`, and `usable`?
- can supersession and recall of old packets happen without relying on email-thread memory?

If the answer is no, the interface is still cloning Resilio's scattered support-packet shape too closely.
'''

product_add = '''## Product-direction addendum after rev0395 — evidence must travel as a typed packet

AnonSync should not let captured evidence masquerade as audience-ready evidence.
The product direction is now explicit:

- **evidence packets are first-class**
- **raw capture, derived artifact, redacted packet, narrative summary, and published packet remain separate**
- **minimum-sufficient sharing is legitimate but must publish what it weakens**
- **transport success is weaker than audience receipt, and audience receipt is weaker than validated usability**
- **every meaningful evidence export needs one receipt preserving custody, redaction, integrity ceiling, and recall boundary**

That means future interface work should keep one stable family for:

- packet shaping from captured artifacts
- redaction-cost review
- audience-envelope selection
- export proof and validation
- supersession and recall of stale packets
- durable lineage receipts for later challenges or appeals

The product should never force the operator to infer packet truth from separate log-path articles, support-form hints, NAS dump instructions, and remembered email steps alone.
'''

sources_add = '''## rev0396 source set — evidence packet, custody, redaction, and export truth

The most load-bearing source set for this pass was:

- Resilio's current `Collecting debug logs automatically` article, which still routes logs through `Contact support`, requires `Include logs`, says not to close the app or device until sending completes, and asks for peer role, timestamps, and affected shares/files.
- Resilio's current `Collecting debug logs manually` article, which still requires debug enablement, restart, reproduction, and platform-specific log retrieval, including service-principal-specific storage paths and config-defined `storage_path` on Linux.
- Resilio's current `Collect debug logs on mobiles` article, which still uses a distinct hidden `.synclogs` collection path after a special debug action.
- Resilio's current `Where to collect logs on NAS?` article, which still says each NAS has its own local storage for `.sync` state and that config may define the true storage path if the obvious location is wrong.
- Resilio's current `Collecting crash reports, mini-dumps and core dumps` article, which still introduces heavier artifact classes and path variants by operating system and service principal.
- Resilio's current `Collecting core dump on NAS devices` article, which still instructs operators to move dumps into a public folder for download, making export transformation and custody visible.
- Resilio's current `Errors & Troubleshooting` category page, which still groups support-facing evidence instructions as article clusters rather than one packet workspace.
- Resilio's current debug-log and dump articles, which still say direct technical support is available only for Sync Business customers and not for Sync v3 users.
- Resilio's current `Resilio Sync change log`, which still records transport-oriented packet facts such as HTTPS sending for Contact Support dialog and prior inability-to-send-feedback fixes.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for exposing many useful evidence channels
- but current Resilio still answers `what exact evidence packet are we sharing, what got transformed or redacted, which source world produced it, what integrity survives export, and what audience may rely on it?` too diffusely
- AnonSync should therefore prefer explicit evidence-packet sheets, packet-shaping reviews, export proofs, packet timelines, and durable lineage receipts over scattered support instructions and thread memory

Primary sources:

- Collecting debug logs automatically
  https://help.resilio.com/hc/en-us/articles/360019430539-Collecting-debug-logs-automatically

- Collecting debug logs manually
  https://help.resilio.com/hc/en-us/articles/206664730-Collecting-debug-logs-manually

- Collect debug logs on mobiles
  https://help.resilio.com/hc/en-us/articles/38269346960531-Collect-debug-logs-on-mobiles

- Where to collect logs on NAS?
  https://help.resilio.com/hc/en-us/articles/205326945-Where-to-collect-logs-on-NAS

- Collecting crash reports, mini-dumps and core dumps
  https://help.resilio.com/hc/en-us/articles/206214615-Collecting-crash-reports-mini-dumps-and-core-dumps

- Collecting core dump on NAS devices
  https://help.resilio.com/hc/en-us/articles/360015557220-Collecting-core-dump-on-NAS-devices

- Errors & Troubleshooting
  https://help.resilio.com/hc/en-us/categories/200410985-Errors-Troubleshooting

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log
'''

write('docs/1516-resilio-evidence-packet-custody-redaction-and-export-fragmentation-evaluation.md', '''# Resilio evidence packet, custody, redaction, and export fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- compare fact patterns against doctrine
- choose the next best discriminator
- rank the next evidence ask by burden and discriminator value
- record what came back from a chosen capture

What it still lacked was the next ordinary operator answer:

> now that we captured something material, what exact packet are we sharing, what was transformed or redacted, which source world produced it, how trustworthy is the export path, and what audience is allowed to rely on this form?

That is the seam this pass locks.
A product that can gather evidence but cannot package it honestly still leaves too much truth in support folklore.
Evidence that moves between people and systems needs its own contract.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose many useful packet ingredients, but mostly as separate support instructions:

- `Collecting debug logs automatically` still routes logs through `Contact support`, asks the operator to include peer role, timestamps, and affected shares/files, and says not to close the application or device until sending is done.
- `Collecting debug logs manually` still routes another export path through manual attachment or upload, requires enablement, restart, reproduction, and gives different retrieval paths for desktop, service, LocalService, Local System, Linux, config-defined storage, NAS, and Android.
- `Collect debug logs on mobiles` still adds a mobile-specific path through a hidden `.synclogs` directory after a special debug action.
- `Where to collect logs on NAS?` still says each NAS keeps its own local storage for `.sync` state and may require checking config if the obvious log path is wrong.
- `Collecting crash reports, mini-dumps and core dumps` still introduces heavier artifact classes with different storage roots, and the service principal still changes where dumps live.
- `Collecting core dump on NAS devices` still includes moving a dump into a public folder for later download, which is an explicit packet-transform and custody event.
- `Errors & Troubleshooting` still presents these support-facing evidence instructions as clustered articles rather than one packet-shaping workspace.
- Current debug-log and dump articles still say direct technical support is available only for Sync Business customers and not for Sync v3 users.
- The current `Resilio Sync change log` still shows packet-transport facts like HTTPS sending for debug data in the Contact Support dialog and a prior fix for inability to send feedback.

## What current Resilio still gets right

### 1) It is candid that artifact classes differ

Logs, crash reports, mini-dumps, and core dumps are not treated as the same thing.
That is worth borrowing.

### 2) It preserves platform and runtime specificity

Desktop, mobile, NAS, service, and config-mode storage roots differ.
That honesty matters because source world affects packet meaning.

### 3) It admits that transport is part of the workflow

Contact-support upload, manual attachment, hidden mobile folders, NAS public-folder movement, and size limits all make the export path visible.
That is useful.

## Where current Resilio still fragments the operator answer

### A) Packet form still lives across separate support articles

Current Resilio helps gather artifacts, but still leaves the operator to infer what packet form is minimally sufficient for which audience.
Raw logs, dump files, support-form uploads, and narrative descriptions are spread out rather than normalized.

### B) Redaction and transformation cost are not a first-class contract

A moved dump in a public folder, a log excerpt pasted into text, or a summarized description all weaken or transform the evidence differently.
Current Resilio implies this reality but still does not make the cost explicit in one packet object.

### C) Custody and source world are visible, but not unified

Service principal, config `storage_path`, NAS local storage, mobile hidden paths, and manual versus automatic export all change how much confidence we should have in packet provenance.
Current Resilio shows the ingredients, but still does not compile them into one custody statement.

### D) `Sent` still does too much work

A packet can be sent, yet not received, not opened, not validated, or not usable.
Current Resilio instructions acknowledge parts of this, but still do not make these stages separate product truths.

## Hard product decision unlocked by this pass

AnonSync should not let evidence sharing live in email habits, support macros, or remembered path lore.
It should compile every serious export into a first-class **evidence packet** object that separately expresses:

- source artifacts and source world
- packet form
- redaction or transformation class
- custody chain
- audience envelope
- export path and transport result
- validation state after receipt
- diagnostic power preserved and diagnostic power weakened
- supersession and recall boundary

## Replacement line for AnonSync

Borrow from Resilio:

- its candor that artifact classes differ
- its platform-specific honesty about storage paths, service worlds, and config-defined local storage
- its explicit export steps for feedback forms, manual collection, mobile hidden folders, and NAS dump movement

Do not clone from Resilio:

- any workflow where packet form must be reconstructed from several support pages manually
- any contract where redaction or transformation can happen without publishing what it weakens
- any interface where `logs sent` pretends receipt, validation, and usability are already proven
- any product shape where old packets can linger without an explicit supersession or recall story

AnonSync should instead ship explicit pages for:

- evidence packet contract sheet
- packet-shaping and minimum-sufficient-share review
- export proof
- packet timeline
- packet lineage receipt
''')

write('docs/1517-evidence-packet-contract-sheet-page-source-artifacts-redaction-class-and-audience-envelope-interface-spec.md', '''# Evidence packet contract sheet page: source artifacts, redaction class, and audience envelope interface spec

## Purpose

After evidence has been captured, the operator still needs one page that answers:

> what exactly are we packaging, what form will it take, what has been removed or transformed, and who is this packet actually for?

## Core decision

AnonSync must expose one first-class **Evidence packet contract sheet** whenever captured facts or artifacts are prepared for handoff, review, support, appeal, or archival reliance.

## Fixed page order

1. **Packet header**
2. **Source-artifact card**
3. **Packet-form card**
4. **Redaction-and-transformation card**
5. **Audience-envelope card**
6. **Current packet decision card**
7. **Decision sentence**

### 1) Packet header

Show:

- packet sheet id
- source case id
- source capture proof ids
- packet owner
- current packet posture
- current strongest safe evidence sentence
- strongest blocked evidence sentence

Supported `packet_posture` values:

- `raw-packet-preferred`
- `derived-packet-acceptable`
- `redacted-packet-required`
- `summary-only-safe`
- `packet-not-yet-safe-to-share`
- `packet-ready-for-export`

Hard rule:

The page may not discuss export before naming packet posture first.

### 2) Source-artifact card

Required rows:

- source artifact ids
- source artifact classes
- source world or runtime lane
- capture times
- collector identity
- custody start point
- artifact freshness horizon

Supported `source_artifact_class` values:

- `ui-observation-set`
- `log-bundle`
- `single-log-excerpt`
- `history-export`
- `queue-or-peer-snapshot`
- `crash-report`
- `mini-dump`
- `core-dump`
- `narrative-note`
- `mixed-packet`

Hard rule:

Source world must stay visible.
A service-world log and a user-world log are not interchangeable provenance.

### 3) Packet-form card

Required rows:

- proposed packet form
- included artifacts
- omitted artifacts
- derived digests or summaries included
- audience-readable index included or not
- packet size or transport constraints

Supported `packet_form` values:

- `raw-archive`
- `raw-plus-index`
- `redacted-archive`
- `excerpt-bundle`
- `derived-digest`
- `narrative-summary`
- `hybrid-packet`

Hard rule:

The packet form must distinguish raw artifact carriage from explanatory layers.
A narrative summary may accompany a raw archive, but cannot silently replace it.

### 4) Redaction-and-transformation card

Required rows:

- redaction class
- transformation steps applied
- reason each step was applied
- diagnostic power weakened
- challenge or appeal power weakened
- reconstructability from retained raw source

Supported `redaction_class` values:

- `none`
- `identifier-redacted`
- `path-redacted`
- `time-redacted`
- `content-excerpted`
- `metadata-only`
- `summary-only`
- `mixed-redaction`

Hard rule:

Every redaction or transformation must publish what stronger evidence claim it prevents.
`privacy-safe` is not enough.

### 5) Audience-envelope card

Required rows:

- target audience class
- minimum sufficient share
- forbidden packet forms for this audience
- confidentiality boundary
- expected validation skill at destination
- recall path if packet is superseded

Supported `target_audience_class` values:

- `internal-operator`
- `peer-reviewer`
- `support-channel`
- `appeal-body`
- `external-stakeholder`
- `archival-record-only`

Hard rule:

Audience envelope and packet form must stay separate.
A raw packet may be valid for one audience and inappropriate for another.

### 6) Current packet decision card

Supported `current_packet_decision` values:

- `share-raw`
- `share-redacted`
- `share-hybrid`
- `share-summary-first`
- `withhold-until-reshaped`
- `retain-local-only`

Required rows:

- current packet decision
- chosen packet form
- chosen audience envelope
- why it beat alternatives
- strongest preserved claim
- strongest weakened claim
- rereview trigger

Hard rule:

The chosen packet must publish both what survives and what was sacrificed.

### 7) Decision sentence

Render one sentence only:

- `The current packet decision is [decision] as [packet form] for [audience], preserving [preserved claim] while weakening [weakened claim] because of [redaction/transformation basis].`

## Required interactions

- **Attach source artifact**
- **Change packet form**
- **Add or remove redaction step**
- **Switch audience envelope**
- **Withhold packet**

## Failure state

If no acceptable packet form exists, show:

- `No safe packet form currently satisfies this audience and confidentiality boundary. Retain locally or reshape the packet before export.`
''')

write('docs/1518-packet-shaping-review-page-raw-derived-redacted-and-minimum-sufficient-share-interface-spec.md', '''# Packet shaping review page: raw, derived, redacted, and minimum-sufficient-share interface spec

## Purpose

The contract sheet names the source artifacts, audience, and packet options.
The **Packet shaping review** decides which packet form should actually leave the operator workspace.
It exists to stop raw oversharing, summary overclaiming, and silent weakening through careless redaction.

## Core decision

AnonSync must ship one review page that ranks packet-form options by **diagnostic power**, **audience fit**, **confidentiality cost**, **validation ease**, and **redaction loss**.

## Fixed page order

1. **Review header**
2. **Packet-option matrix**
3. **Minimum-sufficient-share card**
4. **Redaction-loss card**
5. **Audience-validation card**
6. **Review verdict**

### 1) Review header

Show:

- review id
- linked packet sheet id
- target audience
- current confidentiality posture
- current evidence sensitivity
- current strongest safe export sentence

Supported `confidentiality_posture` values:

- `raw-safe`
- `raw-restricted`
- `redaction-required`
- `summary-preferred`
- `export-frozen`

Hard rule:

The review must publish confidentiality posture before comparing packet forms.

### 2) Packet-option matrix

Columns:

- packet label
- packet form
- diagnostic power preserved
- appeal or challenge usability
- confidentiality cost
- audience comprehension cost
- validation ease
- recommended rank

Supported `recommended_rank` values:

- `export-first`
- `acceptable-second`
- `hold-in-reserve`
- `too-weak-for-purpose`
- `too-sensitive-for-envelope`

Hard rule:

A weaker packet cannot outrank a stronger packet merely because it is easier to read.
The matrix must weigh evidentiary strength and not just convenience.

### 3) Minimum-sufficient-share card

Required rows:

- least-sensitive packet that still serves the purpose
- stronger packet kept in reserve
- audience tasks that the minimal packet supports
- audience tasks that it cannot support
- condition that forces promotion to a stronger packet

Hard rule:

Minimum sufficient share must publish its boundary.
It may not pretend to support later challenge, appeal, or reproduction work if it does not.

### 4) Redaction-loss card

Required rows:

- redaction steps chosen
- strongest fact preserved
- strongest fact blurred or removed
- reproducibility cost
- doctrine-applicability cost
- dispute or appeal cost

Hard rule:

Redaction loss must be stated in operator language.
A later reviewer must not need the raw packet to learn that a time window, path, or identifier was removed.

### 5) Audience-validation card

Required rows:

- can audience open the packet
- can audience validate integrity
- can audience act on the packet alone
- additional context needed
- packet likely to bounce or fail transport

Hard rule:

Audience readability and audience validation are different truths.
A packet can arrive and still be unusable.

### 6) Review verdict

Supported `review_verdict` values:

- `raw-packet-approved`
- `hybrid-packet-approved`
- `redacted-packet-approved`
- `summary-only-too-weak`
- `export-deferred-for-reshaping`
- `retain-raw-send-summary-first`

Render one sentence only:

- `Review verdict: [review_verdict]. Export [packet] because it preserves [preserved power] within confidentiality posture [posture]; claims above [ceiling] remain blocked unless [stronger packet] is later released.`

## Required interactions

- **Re-rank packet options**
- **Toggle stronger reserve packet**
- **Add redaction-loss note**
- **Promote or demote minimal share**
- **Defer export**

## Failure state

If every acceptable packet is too weak for the current purpose, show:

- `All audience-safe packet forms are below the needed evidence ceiling. Export is deferred unless a stronger envelope or different audience is authorized.`
''')

write('docs/1519-evidence-export-proof-page-sent-received-opened-validated-and-usable-interface-spec.md', '''# Evidence export proof page: sent, received, opened, validated, and usable interface spec

## Purpose

Once the chosen packet is exported, the product still needs one page that answers:

> what exactly left, did anyone receive it, did they actually open and validate it, and what evidentiary ceiling now survives that export path?

## Core decision

AnonSync must expose one first-class **Evidence export proof** page whenever a packet is exported, uploaded, attached, transferred, recalled, or superseded in a materially meaningful way.

## Fixed page order

1. **Export header**
2. **Packet-and-path card**
3. **Transport-result card**
4. **Destination-validation card**
5. **Integrity-ceiling card**
6. **Proof sentence**

### 1) Export header

Show:

- export proof id
- source packet sheet id
- source packet form
- export state
- current strongest safe post-export sentence
- strongest blocked post-export sentence

Supported `export_state` values:

- `sent-not-confirmed`
- `received-not-opened`
- `opened-not-validated`
- `validated-not-acted-on`
- `usable-for-stated-purpose`
- `delivery-failed`
- `recalled`
- `superseded`

Hard rule:

The page must not jump from `sent` to `usable` silently.
Each rung is product truth.

### 2) Packet-and-path card

Required rows:

- exported packet id
- exported packet form
- destination audience
- transport path
- size or artifact constraints encountered
- retained source packet pointer
- superseding packet pointer if any

Supported `transport_path` values:

- `in-product-upload`
- `manual-attachment`
- `secure-link`
- `local-file-drop`
- `public-staging-path`
- `api-export`
- `narrative-only-channel`

Hard rule:

Transport path must stay visible because it changes the integrity ceiling and recall options.

### 3) Transport-result card

Required rows:

- send result
- receive acknowledgement
- open acknowledgement
- checksum or integrity witness if any
- transport failure notes
- resend or alternate-path decision

Hard rule:

Receive acknowledgement and open acknowledgement must remain separate.
A mailbox or upload service can acknowledge receipt without proving the packet was read.

### 4) Destination-validation card

Required rows:

- destination validation state
- validation method
- packet usable for stated purpose or not
- missing context still requested
- audience challenge or rejection state

Supported `destination_validation_state` values:

- `not-yet-attempted`
- `format-opened`
- `integrity-checked`
- `context-sufficient`
- `usable-for-purpose`
- `usable-but-narrow`
- `rejected-or-corrupt`

Hard rule:

Format readability is weaker than validation.
A packet that opens but cannot support the requested task stays weaker.

### 5) Integrity-ceiling card

Required rows:

- highest safe statement supported by this export event
- highest blocked statement
- reason still blocked
- event that would upgrade the ceiling
- recall or supersession consequence if stale

Hard rule:

The integrity ceiling must consider packet form, transport path, and destination validation together.

### 6) Proof sentence

Render one sentence only:

- `This export is [export_state] via [transport path]; destination validation is [validation state], so the strongest safe post-export sentence is [sentence].`

## Required interactions

- **Acknowledge receipt**
- **Record open or validation result**
- **Attach resend or alternate path**
- **Recall packet**
- **Supersede with stronger packet**

## Failure state

If transport or validation fails, show:

- `The packet left the source boundary but did not yet become usable evidence at destination. The prior export ceiling survives until receipt, validation, or stronger resend.`
''')

write('docs/1520-evidence-packet-timeline-page-capture-redaction-export-recall-and-supersession-events-interface-spec.md', '''# Evidence packet timeline page: capture, redaction, export, recall, and supersession events interface spec

## Purpose

Operators need one durable chronology that explains how a packet changed over time:

- when raw evidence was captured
- when it was redacted or transformed
- when it was exported
- when it failed, was recalled, or was superseded
- which audiences saw which version

## Core decision

Every material evidence-packet lifecycle in AnonSync must have one first-class **Evidence packet timeline**.

## Fixed page order

1. **Timeline header**
2. **Packet-version ladder**
3. **Custody events card**
4. **Audience exposure card**
5. **Supersession-and-recall card**
6. **Timeline sentence**

### 1) Timeline header

Show:

- timeline id
- source packet sheet id
- current live packet version
- current audience exposure posture
- current strongest safe packet statement

### 2) Packet-version ladder

Each version row must show:

- version id
- packet form
- redaction class
- created from which predecessor
- current status
- current audience scope

Supported `current_status` values:

- `draft-only`
- `held-local`
- `exported-live`
- `partially-received`
- `validated-live`
- `recalled`
- `superseded`
- `retired-archive-only`

Hard rule:

Later versions may not erase earlier exposures.
The timeline must preserve which weaker or riskier packet actually left the system.

### 3) Custody events card

Supported event kinds:

- `captured`
- `reshaped`
- `redacted`
- `checksummed`
- `exported`
- `receipt-confirmed`
- `opened`
- `validated`
- `rejected`
- `recalled`
- `superseded`
- `deleted-local-copy`

Hard rule:

Every transformation and export must preserve who performed it and against which packet version.

### 4) Audience exposure card

Required rows:

- audience that saw each version
- first exposure time
- last confirmed usable time
- audience still holding stale packet or not
- re-notification needed or not

Hard rule:

Audience exposure is not binary.
Different audiences may hold different packet generations at once.

### 5) Supersession-and-recall card

Required rows:

- active superseding packet
- stale packet versions still in the wild
- recall path attempted
- acknowledgment of recall or not
- strongest sentence still unsafe because stale packets persist

Hard rule:

Recall must preserve uncertainty.
A recalled packet is weaker than a definitely withdrawn packet from every destination.

### 6) Timeline sentence

Render one sentence only:

- `Packet lineage is currently at [live version]; earlier packet [older version] is [status], and audience exposure remains [exposure posture], so the safe packet statement is [sentence].`

## Required interactions

- **Add packet version**
- **Log transformation event**
- **Log export or validation event**
- **Mark packet recalled or superseded**
- **Record stale-packet exposure**

## Failure state

If version history is broken, show:

- `Packet chronology is incomplete. Audience reliance must stay below the normal export ceiling until custody continuity is restored.`
''')

write('docs/1521-evidence-packet-lineage-receipt-page-custody-redaction-integrity-and-audience-boundary-interface-spec.md', '''# Evidence packet lineage receipt page: custody, redaction, integrity, and audience boundary interface spec

## Purpose

After evidence has been shaped and exported, the next operator needs one compact receipt that answers:

- what source artifacts fed this packet
- what packet form actually left
- what was redacted or transformed
- who held custody
- what audience saw it
- what integrity and usability ceiling now survives

## Core decision

Every material evidence-packet lifecycle in AnonSync must end in one durable **Evidence packet lineage receipt**.

## Fixed page order

1. **Receipt header**
2. **Source-and-form summary**
3. **Custody-and-transformation summary**
4. **Export-and-validation summary**
5. **Integrity-and-boundary summary**

### 1) Receipt header

Show:

- receipt id
- source case id
- source packet sheet id
- live packet version
- receipt freshness horizon
- current safe packet claim

### 2) Source-and-form summary

Required rows:

- source artifacts used
- source world
- packet form exported
- audience class
- strongest reserve packet still retained locally
- raw source retained or not

### 3) Custody-and-transformation summary

Required rows:

- custody owner chain
- redaction class
- transformation steps
- diagnostic power weakened
- reconstructable from source or not
- recall path available or not

Hard rule:

The receipt must preserve both what the packet includes and what it no longer includes.

### 4) Export-and-validation summary

Required rows:

- transport path
- export state
- destination validation state
- packet usable for stated purpose or not
- superseded or recalled packet ids still relevant
- stale audience exposures still relevant

### 5) Integrity-and-boundary summary

Required rows:

- strongest safe evidentiary sentence
- strongest blocked evidentiary sentence
- reason the stronger sentence remains blocked
- event that would upgrade the ceiling
- event that would downgrade or revoke the ceiling

## Required interactions

- **Open source packet sheet**
- **Open export proof**
- **Mark packet stale**
- **Spawn stronger superseding packet**

## Failure state

If the packet cannot be trusted enough for ordinary reuse, show:

- `This receipt records a packet whose form, custody, or validation ceiling is too weak for normal reuse. Re-export or stronger source access is required.`
''')

prepend('README.md', readme_add)
prepend('docs/00-status.md', status_add)
prepend('docs/10-resilio-sync-evaluation.md', resilio_eval_add)
prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', clone_veto_add)
prepend('docs/20-product-direction.md', product_add)
prepend('docs/sources.md', sources_add)
