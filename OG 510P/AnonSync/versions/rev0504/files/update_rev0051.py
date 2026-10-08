from pathlib import Path
import re
root = Path('/tmp/anonsync_rev0050_work')
docs = root/'docs'

rev = 'rev0051'
timestamp = '2026.03.17.11.36'
codename = 'exitintentresidueledger'
new_open = '64-critical-open-questions.md'
old_open = '63-critical-open-questions.md'
new_spec = '63-subject-exit-and-residue-clearance-spec.md'

# rename open questions file
old_open_path = docs/old_open
new_open_path = docs/new_open
if old_open_path.exists():
    old_open_path.rename(new_open_path)

# helper

def replace_in_file(path, old, new):
    p = Path(path)
    text = p.read_text()
    if old not in text:
        raise SystemExit(f'missing target in {p}: {old[:80]}')
    p.write_text(text.replace(old, new))

# README update
readme = (root/'README.md').read_text()
readme = re.sub(r'- Revision: `rev\d+`', f'- Revision: `{rev}`', readme)
readme = re.sub(r'- Timestamp: `[^`]+` \(America/New_York\)', f'- Timestamp: `{timestamp}` (America/New_York)', readme)
readme = re.sub(r'- Codename: `[^`]+`', f'- Codename: `{codename}`', readme)
readme = re.sub(r'This revision continues directly from `rev\d+` and does seven things:', 'This revision continues directly from `rev0050` and does seven things:', readme)
readme = re.sub(r'1\. Re-checks \*\*Resilio Sync\*\* again with extra emphasis on how current discovery and route settings still collapse connection success, identity disclosure, share-membership disclosure, and endpoint publication into the same operational lore\.', '1. Re-checks **Resilio Sync** again with extra emphasis on how current docs still scatter removal, unlink, disconnect, uninstall, and stolen-device remediation across several different rituals rather than one exit contract.', readme)
readme = re.sub(r'2\. Sharpens the \*\*non-clone rationale\*\* into a stricter rule: AnonSync should not let tracker/LAN/known-host convenience stand in for an explicit disclosure contract\.', '2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let overloaded `remove` / `hide` / `unlink` convenience stand in for an explicit exit-intent and residue-clearance contract.', readme)
readme = re.sub(r'3\. Adds a dedicated \*\*discovery publication and identity-disclosure spec\*\* so the archive now says which audiences can learn which facts, by which mechanisms, and with what residual leakage after narrowing\.', '3. Adds a dedicated **subject exit and residue-clearance spec** so the archive now says what a removal-style action actually ends, what local or remote residue still remains, and what continuity claims were preserved.', readme)
readme = re.sub(r'4\. Extends the \*\*CLI/interface contract\*\* with a first-class `disclosure \.\.\.` surface for inspecting audience/fact matrices, residue findings, and disclosure receipts\.', '4. Extends the **CLI/interface contract** with a first-class `exit ...` surface for previewing exit intent, residue, continuity consequences, and durable exit receipts.', readme)
readme = re.sub(r'5\. Extends the \*\*daemon API\*\* so workbench/CLI/TUI/headless clients can inspect effective disclosure, preview widening/narrowing, and clear or acknowledge residual disclosure honestly\.', '5. Extends the **daemon API** so workbench/CLI/TUI/headless clients can create reviewed exit plans, inspect exit residue, and apply exit actions without hiding cross-domain consequences.', readme)
readme = re.sub(r'6\. Adds additional \*\*canonical interface flows\*\* for previewing what a route/discovery policy really publishes before applying it and for narrowing publication while proving what residue still remains\.', '6. Adds additional **canonical interface flows** for decommissioning a workstation cleanly and for retiring a backup-style replica without confusing revocation, detachment, byte cleanup, and disclosure residue.', readme)
readme = re.sub(r'7\. Refreshes the \*\*workbench\*\*, \*\*evaluation\*\*, \*\*ADRs\*\*, \*\*roadmap\*\*, \*\*open questions\*\*, and \*\*reading order\*\* so future revisions keep publication audience, fact classes, dialing posture, and residue truth separate public facts\.', '7. Refreshes the **workbench**, **evaluation**, **ADRs**, **roadmap**, **open questions**, and **reading order** so future revisions keep hide/detach/revoke/decommission/erase/replace semantics and residue truth separate public facts.', readme)
# add should/should not bullets
marker = '- a first-class personal-constellation / authority-domain surface so operators can tell which members belong to a convenience-linked set, what each member may see or do, how far approvals can travel, and when a local-looking action actually reaches the wider constellation\n'
if marker in readme:
    readme = readme.replace(marker, marker + '- a first-class subject-exit / residue-clearance surface so operators can tell what an exit action actually stops, what bytes, trust, publication, and recovery material remain, and which receipt proves the result\n')
marker2 = '- remembered approvals that silently become standing future authority across devices or share classes\n'
if marker2 in readme:
    readme = readme.replace(marker2, marker2 + '- removal or uninstall stories that still overload hide, unlink, disconnect, revoke, byte cleanup, and continuity destruction into one vague off-ramp\n')
(root/'README.md').write_text(readme)

# Status rewrite top portion more simply
status = (docs/'00-status.md').read_text()
status = status.replace('This revision is an in-place continuation of `rev0049`, driven by the current request:', 'This revision is an in-place continuation of `rev0050`, driven by the current request:')
status = status.replace('- make sure the archive has a better reason not to clone route controls that talk about success while hiding disclosure residue\n', '- make sure the archive has a better reason not to clone route controls that talk about success while hiding disclosure residue\n- make sure the archive has a better reason not to clone removal and uninstall stories that blur hide, revoke, detach, erase, and replace\n')
status = re.sub(r'## Immediate output of this pass\n\nThe archive now contains:\n\n- a deeper Resilio-derived warning that tracker, LAN discovery, predefined hosts, and relay-oriented route controls still hide one more basic operator question: who can learn what about this node or share right now\n- a new dedicated spec for \*\*discovery publication and identity-disclosure truth\*\*\n- interface/API extensions for `disclosure` inspection, disclosure reports, residual-disclosure findings, and disclosure receipts\n- additional canonical flows for previewing audience/fact disclosure before a route-policy change and for narrowing publication while proving what residue still remains\n- workbench, evaluation, roadmap, ADR, and open-question updates so future revisions keep publication audience, disclosed fact class, dialing posture, and residual exposure separate public facts',
'''## Immediate output of this pass

The archive now contains:

- a deeper Resilio-derived warning that current `hide`, `unlink`, `disconnect`, `remove`, `uninstall`, and stolen-device guidance still scatter one operator question across several articles: what exactly stops, what remains, and what residue is still real after exit
- a new dedicated spec for **subject exit and residue-clearance truth**
- interface/API extensions for `exit` inspection, exit plans, exit residue findings, and exit receipts
- additional canonical flows for reviewed workstation decommission and reviewed replica retirement
- workbench, evaluation, roadmap, ADR, and open-question updates so future revisions keep hide/detach/revoke/decommission/erase/replace semantics and residue truth separate public facts''', status, flags=re.S)
status = re.sub(r'`rev0050` pushes the next step:\n\n> a serious Linux-first workbench is still underspecified if it can explain trust, storage, rollback, routing, throughput, attention, access, recovery, release boundaries, policy origin, diagnostics, temporary exceptions, and personal constellations, yet still make “discovery policy” hide which audiences learn which facts, what residue remains after narrowing, and whether a named endpoint is still an act of disclosure\.\n\nThat changes the archive in six specific ways:\n\n- discovery/publication is now modeled as an explicit audience/fact boundary instead of only a transport-success knob set\n- a subject can now publish identity facts, share-membership facts, and endpoint facts through visibly different mechanisms\n- residual disclosure after narrowing is now first-class state instead of support-lore about cache clearing or waiting for provider TTLs\n- workbench and CLI/API surfaces can answer whether a change widened audience, widened fact class, or only changed dialing posture\n- receipts can now prove not only that publication narrowed, but also whether any residual disclosure was acknowledged or cleared\n- the Resilio comparison now lands a sharper non-clone argument: current route/discovery controls still depend too much on transport-language and scattered docs to count as one trustworthy disclosure model',
'''`rev0051` pushes the next step:

> a serious Linux-first workbench is still underspecified if it can explain trust, storage, rollback, routing, throughput, attention, access, recovery, release boundaries, policy origin, diagnostics, temporary exceptions, personal constellations, and disclosure, yet still make “remove this thing” hide which authority ended, which bytes stayed, which recovery claims survived, and what residue is still real.

That changes the archive in six specific ways:

- exit intent is now modeled as an explicit contract instead of a loose family of removal verbs
- a subject exit can now separately describe authority revocation, local-byte cleanup, publication narrowing, continuity preservation, and successor binding
- residue after exit is now first-class state instead of uninstall lore or offline-device confusion
- workbench and CLI/API surfaces can answer whether an exit was cosmetic cleanup, true revocation, decommission, or replacement
- receipts can now prove not only that an exit happened, but also what remained intentionally and what residue still needed time or follow-up
- the Resilio comparison now lands a sharper non-clone argument: current removal and uninstall stories still depend too much on scattered support ritual to count as one trustworthy exit model''', status, flags=re.S)
status = status.replace('Those unresolved items are now reflected in `63-critical-open-questions.md`.', 'Those unresolved items are now reflected in `64-critical-open-questions.md`.')
(docs/'00-status.md').write_text(status)

# sources append
sources = (docs/'sources.md').read_text().rstrip() + '\n\n- Disconnecting and Removing Folders\n  https://help.resilio.com/hc/en-us/articles/205457785-Disconnecting-and-Removing-Folders\n\n- How to clear offline devices? (desktop only)\n  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only\n\n- If your device is stolen\n  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen\n\n- Syncthing Configuration\n  https://docs.syncthing.net/users/config.html\n'
(docs/'sources.md').write_text(sources)

# create new spec
spec_text = '''# Subject Exit and Residue Clearance Spec

## Question

> when an operator says “remove”, “hide”, “detach”, “revoke”, “replace”, “decommission”, or “erase”, what exact commitments end, what continuity is preserved, what residue still remains, and what receipt proves the outcome?

## Why this spec exists

The archive already has strong treatment for device retirement, path detachment, disclosure residue, recovery bundles, access revocation, and temporary exceptions.
What it still lacked was one shared contract for exit itself.

Current Resilio docs still split exit semantics across multiple articles:

- **Hide offline device** only hides it from view; it does not unlink it, and the device reappears if it ever comes back online.
- **Unlink from identity** is local-only; you cannot remotely unlink other devices.
- **Disconnect folder** affects one device, removes placeholders in selective mode, and later reconnect may propose a new default path or create a duplicate directory.
- **Remove folder** affects linked devices, but a folder may still exist on other remote devices not linked to the same identity.
- **Uninstall** recommends unlinking identity and removing remaining Standard shares first or the old instance will simply remain visible as an offline peer, and hidden `.sync/Archive` bytes remain unless manually cleaned up.
- **Stolen-device remediation** asks the operator to back up, remove shares, unlink devices, delete storage state, reinstall, regenerate identity, and re-share.

That is workable support guidance, but it is not one public exit model.
AnonSync should do better.

## Core rule

All removal-style or departure-style actions should compile down to one explicit exit contract that keeps five questions separate:

1. **Authority:** what trust, grant, approval, session, or ownership power ended?
2. **Visibility/publication:** what peer visibility or disclosure posture narrowed?
3. **Bytes/state:** what local bytes, indexes, histories, archives, or service state remained or were destroyed?
4. **Continuity:** what successor, recovery, or preservation claim was intentionally kept?
5. **Residue:** what still exists elsewhere, offline, cached, delayed, or intentionally preserved after apply?

## Shared language

### Exit subject ref

A normalized reference to the thing being exited.

Fields:

- `subject_kind` (`device`, `share`, `mount`, `contact`, `offer`, `access-token`, `session`, `recovery-bundle`, `state-root`, `daemon-self`)
- `subject_id`
- `scope_kind` (`local`, `share`, `constellation`, `daemon`, `audience`, `peer-set`)
- `scope_ref` nullable

### Exit intent profile

The operator-visible meaning of the exit.

Fields:

- `exit_intent_profile_id`
- `label`
- `intent_class` (`hide`, `detach-local`, `ignore-future`, `revoke-authority`, `replace-with-successor`, `decommission`, `erase-local-residue`, `retire-share-presence`)
- `requires_plan` boolean
- `preserve_continuity_default` (`none`, `recovery-only`, `successor-only`, `preservation-only`, `operator-choice`)
- `default_residue_policy` (`show-only`, `show-and-ack`, `show-and-clear-where-possible`)
- `allowed_subject_kinds[]`
- `provenance_ref` nullable

### Exit plan

A reviewed plan describing what an exit would actually do.

Fields:

- `exit_plan_id`
- `subject_ref`
- `intent_profile_ref`
- `status` (`draft`, `ready`, `blocked`, `applied`, `superseded`, `drifted`)
- `authority_effects[]`
- `visibility_effects[]`
- `byte_state_effects[]`
- `continuity_effects[]`
- `residue_findings[]`
- `requires_followup[]`
- `generated_at`
- `expires_at` nullable
- `decision_trace_ref` nullable

### Exit residue finding

A durable description of what still remains after narrowing, retirement, cleanup, or decommission.

Fields:

- `exit_residue_id`
- `subject_ref`
- `residue_class` (`offline-peer-memory`, `remote-share-copy`, `cached-publication`, `local-history`, `recovery-material`, `token-still-valid`, `session-still-open`, `waiting-for-peer-observation`, `intentionally-preserved-bytes`)
- `location_class` (`local`, `remote-peer`, `provider-cache`, `constellation-member`, `unknown-offline-peer`)
- `clearability` (`none`, `time-bound`, `operator-clearable`, `requires-peer-observation`, `rotate-required`)
- `evidence_summary`
- `ack_required` boolean
- `last_verified_at`

### Exit receipt

A durable record proving what exit action actually happened.

Fields:

- `exit_receipt_id`
- `subject_ref`
- `intent_class`
- `before_summary`
- `after_summary`
- `continuity_summary`
- `residue_summary`
- `applied_plan_ref` nullable
- `actor_ref`
- `created_at`

## Public rules

1. **Exit intent must be explicit.**
   `hide`, `detach-local`, `revoke-authority`, `decommission`, and `erase-local-residue` must not be overloaded into one `remove` action.

2. **Decommission is not revocation is not erasure.**
   A device may leave active use while still preserving recovery bundles or retained history. That must be visible.

3. **Visibility narrowing is not byte destruction.**
   A share or device can disappear from ordinary workbench surfaces while bytes, archives, or recovery bundles intentionally remain.

4. **Local cleanup is not proof of remote cleanup.**
   If some peers are offline or provider/cache residue still exists, the exit surface should say so plainly.

5. **Every exit should say what stays.**
   The interface should never list only what will be removed. It should also say what remains intentionally or unavoidably.

6. **Every exit should say what future is blocked.**
   The interface should answer whether future sync, future approvals, future claims, future publication, or future sessions were ended.

7. **Existing domain-specific verbs may remain, but they should compile to this contract.**
   `device retire`, `mount detach`, `offer revoke`, `access token revoke`, `recover invalidate-bundle`, and disclosure-clearing actions should all produce compatible exit plans or exit receipts when the operator outcome is “leave, stop, revoke, or clear”.

## CLI surface

```text
anonsync exit prepare device dev_01J... --intent revoke-authority --plan
anonsync exit prepare daemon self --intent decommission --preserve recovery-only --plan
anonsync exit prepare share shr_01J... --intent retire-share-presence --scope constellation:travel --plan
anonsync exit show exp_01J...
anonsync exit apply exp_01J...
anonsync exit residue list --subject device:dev_01J...
anonsync exit residue show exd_01J...
anonsync exit receipt show exr_01J...
```

The group should answer:

- what exactly this exit would stop
- what bytes, history, recovery material, and visibility would remain
- what residue still depends on time, remote peers, or follow-up cleanup
- whether the exit is cosmetic cleanup, true revocation, full decommission, or continuity-preserving replacement
- which receipt later proves the result

## Workbench expectations

The workbench should expose one **Exits** surface.
It should not replace domain pages, but it should unify exit-like actions across them.

The page should group exits by:

- `needs review now`
- `applied with unresolved residue`
- `awaiting peer observation`
- `continuity preserved`
- `fully cleared`

A detail drawer should always show:

- **What stops now**
- **What stays intentionally**
- **What residue remains**
- **What follow-up is still possible**
- **Which receipt proves the exit later**

## Report language additions

Exit workflows should reuse the common report model with two families:

- `exit-preview` — what the exit would stop, preserve, and leave behind
- `exit-residue` — what still remains after apply and why

## Why this matters

A privacy-respecting sync product should be at least as honest on the way out as on the way in.
If entry, trust, routing, recovery, and disclosure are explicit but departure is still one overloaded `remove` button plus support lore, the control model remains incomplete.

A mature AnonSync surface should let an operator move from `I want this thing gone from active use` to `which kind of gone?` to `what stays?` to `what residue still remains?` to `what receipt proves it?` without reinstall ritual, hidden-folder archaeology, or vague faith that the word “remove” meant the right thing.
'''
(docs/new_spec).write_text(spec_text)

# evaluation add section and requirement
path = docs/'10-resilio-sync-evaluation.md'
text = path.read_text()
anchor = '### Requirement 47 — personal-device convenience must use one explicit constellation and authority-domain contract\n'
insert = '''### 16l) Exit and decommission still depend too much on overloaded remove and uninstall ritual

Resilio's current docs still spread one operator question across several different articles:

- clear offline device hides it from the list, but does not unlink it, and it will reappear if it comes back online
- unlink from identity is local-only and cannot remotely unlink other devices
- disconnect folder is local-ish and may remove placeholders, while reconnect may propose a new path or create a duplicate directory
- remove folder affects linked devices, but the same folder may still live on other remote devices not linked to the same identity
- uninstall guidance says to unlink identity and remove remaining Standard shares first or the old instance will simply remain visible as offline elsewhere, and hidden `.sync/Archive` data still needs manual cleanup
- stolen-device guidance escalates to backup, remove shares, unlink, delete storage state, reinstall, regenerate identity, and reshare

That is not one trustworthy exit model. It is a family of adjacent rituals.
AnonSync should expose one explicit exit contract that says:

- what authority ended
- what visibility/publication ended
- what local bytes or hidden history remained
- what continuity or recovery posture was intentionally preserved
- what residue still remains remotely, offline, or time-delayed after apply

### Requirement 48 — exit intent, continuity, and residue must be one explicit contract

A privacy-respecting sync product should not be more honest about admission than it is about departure.
Hide, detach, revoke, decommission, replace, and erase are different state transitions with different trust, storage, disclosure, and continuity consequences.
The public interface should make that unavoidable.

'''
if anchor in text and '### 16l)' not in text:
    text = text.replace(anchor, insert + anchor)
path.write_text(text)

# product direction append doctrine
path = docs/'20-product-direction.md'
text = path.read_text()
if '### Doctrine 45 — exit is a contract, not removal folklore' not in text:
    text += '''

### Doctrine 45 — exit is a contract, not removal folklore

If entry, trust, route policy, recovery, and disclosure are explicit but departure is still one overloaded family of `remove` buttons, the product is not actually honest.

AnonSync should make every removal-style action answer five questions:

- what authority ends
- what visibility/publication ends
- what bytes or retained history remain
- what continuity is preserved intentionally
- what residue still remains and why

That means `hide`, `detach`, `ignore`, `revoke`, `replace`, `decommission`, and `erase-local-residue` should remain distinct intents even when the UI chooses to present them from the same page.

The operator should never have to learn from support lore that one action merely cleaned up a list, another revoked future trust, a third preserved recovery bundles, and a fourth deleted local archive bytes while leaving remote copies intact.
'''
path.write_text(text)

# report language append exit report family
path = docs/'41-report-and-intervention-language.md'
text = path.read_text()
if '### 12b) Exit/residue report' not in text:
    text = text.replace('## Intervention grammar', '''### 12b) Exit/residue report

Answers what an exit action would stop, what it intentionally preserves, and what residue still remains after apply.
It should always say:

- subject being exited and exit-intent class
- authority, visibility, byte-state, and continuity deltas
- what stays intentionally versus what could not yet be cleared
- which residue findings are time-bound, peer-bound, or operator-clearable
- whether a later receipt proves full clearance or only partial exit with acknowledged residue

## Intervention grammar''')
path.write_text(text)

# interface spec append object definitions and command section
path = docs/'30-interface-spec.md'
text = path.read_text()
if '### Exit plan' not in text:
    text = text.replace('## Top-level groups', '''### Exit plan

A durable preview describing what a removal-style action would actually do across authority, visibility, byte-state, continuity, and residue.

Fields:

- `exit_plan_id`
- `subject_ref`
- `intent_class` (`hide`, `detach-local`, `ignore-future`, `revoke-authority`, `replace-with-successor`, `decommission`, `erase-local-residue`, `retire-share-presence`)
- `authority_effects[]`
- `visibility_effects[]`
- `byte_state_effects[]`
- `continuity_effects[]`
- `residue_findings[]`
- `requires_followup[]`
- `generated_at`
- `expires_at` nullable
- `decision_trace_ref` nullable

### Exit residue finding

A durable finding about what still remains after an exit action.

Fields:

- `exit_residue_id`
- `subject_ref`
- `residue_class` (`offline-peer-memory`, `remote-share-copy`, `cached-publication`, `local-history`, `recovery-material`, `waiting-for-peer-observation`, `intentionally-preserved-bytes`)
- `location_class` (`local`, `remote-peer`, `provider-cache`, `constellation-member`, `unknown-offline-peer`)
- `clearability` (`none`, `time-bound`, `operator-clearable`, `requires-peer-observation`, `rotate-required`)
- `evidence_summary`
- `ack_required` boolean
- `last_verified_at`

### Exit receipt

A durable record proving what kind of exit was actually applied and what remained afterward.

Fields:

- `exit_receipt_id`
- `subject_ref`
- `intent_class`
- `before_summary`
- `after_summary`
- `continuity_summary`
- `residue_summary`
- `applied_plan_ref` nullable
- `actor_ref`
- `created_at`

## Top-level groups''')
    text += '''

## Exit and decommission surfaces

Use one explicit family for reviewed departure-style actions instead of overloading `remove`.

```text
anonsync exit prepare device dev_01J... --intent revoke-authority --plan
anonsync exit prepare daemon self --intent decommission --preserve recovery-only --plan
anonsync exit prepare share shr_01J... --intent retire-share-presence --scope constellation:travel --plan
anonsync exit show exp_01J...
anonsync exit apply exp_01J...
anonsync exit residue list --subject device:dev_01J...
anonsync exit residue show exd_01J...
anonsync exit receipt show exr_01J...
```

Rules:

- `hide`, `detach-local`, `revoke-authority`, `decommission`, `replace-with-successor`, and `erase-local-residue` must remain distinct intents
- domain-specific commands such as `device retire`, `mount detach`, `offer revoke`, `access token revoke`, and `recover invalidate-bundle` may remain, but they should compile to compatible exit plans or receipts when the operator outcome is “leave, stop, revoke, or clear”
- exit surfaces must always show **what stops now**, **what stays intentionally**, and **what residue still remains**
- local cleanup must never be presented as proof that remote or offline residue is gone
- continuity-preserving exits must say exactly what successor, recovery, or preservation claim survives the exit
'''
path.write_text(text)

# daemon api append section and events
path = docs/'31-daemon-api-spec.md'
text = path.read_text()
if '## Exit and decommission resources' not in text:
    text = text.replace('## Event stream', '''## Exit and decommission resources

These resources keep departure-style actions explicit.
They answer what an exit would stop, what it preserves, and what residue remains after apply.

```text
POST   /v1/exits
GET    /v1/exits/{exit_plan_id}
POST   /v1/exits/{exit_plan_id}/apply
GET    /v1/exit-residue
GET    /v1/exit-residue/{exit_residue_id}
GET    /v1/exit-receipts/{exit_receipt_id}
```

`POST /v1/exits` should accept a normalized subject ref plus an explicit `intent_class`.
The resulting plan should always include:

- authority effects
- visibility/disclosure effects
- byte-state effects
- continuity effects
- residue findings and clearability
- apply blockers or acknowledgements still required

Domain-specific mutation endpoints may still exist, but when the operator-visible outcome is a departure, revocation, detachment, or decommission, those endpoints should reference or emit the same exit-plan / exit-receipt model.

## Event stream''')
    text = text.replace('- `audit.entry_written`', '- `audit.entry_written`\n- `exit.plan_created`\n- `exit.applied`\n- `exit.residue_recorded`\n- `exit.residue_cleared`\n- `exit.receipt_recorded`')
path.write_text(text)

# workbench append exits page
path = docs/'38-operator-workbench-interface-spec.md'
text = path.read_text()
if '## Exits page' not in text:
    text = text.replace('## Access page', '''## Exits page

A cross-cutting surface for departure-style actions.
It should not replace domain pages, but it should unify them.

The page should group items into:

- `needs review now`
- `applied with unresolved residue`
- `awaiting peer observation`
- `continuity preserved`
- `fully cleared`

A detail drawer should always show:

- what stops now
- what stays intentionally
- what residue remains and where
- what follow-up can still clear it
- which exit receipt proves the outcome later

## Access page''')
path.write_text(text)

# flows append
path = docs/'32-interface-flows.md'
text = path.read_text()
if '## Flow 89 — decommission a workstation before sale' not in text:
    text += '''

## Flow 89 — decommission a workstation before sale without confusing cleanup, revocation, and continuity

Problem: a laptop is about to be sold or donated. The operator wants it out of active use, wants trust and sessions revoked, wants unnecessary local bytes cleaned up, but still wants an explicit record of what recovery material or remote residue remains.

```text
$ anonsync exit prepare daemon self --intent decommission --preserve recovery-only --clear local-history --plan
Would create exit plan: exp_01JXQ...
Intent: decommission
Subject: daemon-self on laptop-ember

Would stop now:
  - 3 active control sessions
  - 2 access tokens
  - future share publication from this node
  - future sync participation for 12 mounted shares

Would preserve intentionally:
  - 2 sealed recovery bundles
  - successor suggestion for office-laptop-new

Residual findings:
  - 1 offline peer may still remember this device until next observation
  - 4 hidden archive directories will remain unless explicit erase-local-residue is added

Apply blocker: none
```

```text
$ anonsync exit apply exp_01JXQ...
Applied exit plan: exp_01JXQ...
Exit receipt: exr_01JXQ...
Residual findings open: 2
```

```text
$ anonsync exit receipt show exr_01JXQ...
Intent: decommission
Authority ended: sessions, tokens, share participation
Continuity preserved: 2 recovery bundles retained
Residue remaining:
  - offline-peer-memory on dev_01JR...
  - intentionally-preserved-bytes in local archive paths
Safest next action: erase-local-residue --receipt-linked
```

What this flow proves:

- decommission is not the same as “delete everything”
- local cleanup, trust revocation, and continuity preservation stay legible as separate outcomes
- the operator gets one durable receipt instead of support-lore confidence

## Flow 90 — retire an encrypted backup-style replica without pretending authority and byte cleanup are the same thing

Problem: an encrypted replica on a rented VPS is being retired. The operator wants future participation and publication ended, wants to keep the trusted peers intact, and wants a clear answer about what ciphertext bytes or disclosure residue remain after shutdown.

```text
$ anonsync exit prepare device dev_vps9 --intent revoke-authority --scope share:archive --plan
Would create exit plan: exp_01JXR...
Intent: revoke-authority
Subject: device dev_vps9 on share archive

Would stop now:
  - future encrypted-replica participation on share archive
  - direct/publication routes for dev_vps9
  - recovery preference that counted this replica as available witness

Would preserve intentionally:
  - trusted peers and grants on other devices unchanged
  - local recovery bundles on trusted peers unchanged

Residual findings:
  - provider cache may still retain recent endpoint disclosure for up to TTL window
  - ciphertext bytes on remote disk remain until erase-local-residue is separately applied or externally verified
```

```text
$ anonsync exit apply exp_01JXR...
Applied exit plan: exp_01JXR...
Exit receipt: exr_01JXR...
```

```text
$ anonsync exit residue list --subject device:dev_vps9
exd_01JXR1  cached-publication        clearability: time-bound
exd_01JXR2  intentionally-preserved-bytes  clearability: operator-clearable
```

What this flow proves:

- replica retirement can end future authority without pretending remote bytes vanished already
- disclosure residue and byte residue remain separate public facts
- the operator can keep continuity on trusted peers without re-learning support ritual about what “remove” meant
'''
path.write_text(text)

# roadmap modifications
path = docs/'50-roadmap.md'
text = path.read_text()
if 'exit plans and residue receipts' not in text:
    text = text.replace('- reclaim plans and receipts that keep local space recovery distinct from replicated delete semantics\n', '- reclaim plans and receipts that keep local space recovery distinct from replicated delete semantics\n- exit plans and residue receipts that keep hide/revoke/decommission/erase semantics explicit across device, share, and daemon exits\n')
    text = text.replace('- operators no longer need unsupported clone-style workarounds\n', '- operators no longer need unsupported clone-style workarounds\n- operators can decommission a node or retire a replica without confusing cosmetic cleanup, authority revocation, remote residue, and preserved continuity\n')
path.write_text(text)

# ADR append
path = docs/'40-architecture-decisions.md'
text = path.read_text()
if '## ADR-063 — exit intent must be a first-class contract' not in text:
    text += '''

## ADR-063 — exit intent must be a first-class contract

**Decision:** Departure-style actions should compile to a shared exit-plan / exit-receipt model instead of relying on overloaded remove/uninstall vocabulary.

**Why:** Current sync-product support lore often makes operators infer too much from verbs like hide, disconnect, remove, unlink, or uninstall. A privacy-respecting product should be at least as explicit on the way out as it is on the way in.

**Implications:**

- exit intent stays explicit (`hide`, `detach-local`, `revoke-authority`, `replace-with-successor`, `decommission`, `erase-local-residue`)
- exit plans always show what stops, what stays, and what residue remains
- domain-specific verbs may stay for ergonomics, but their outcomes should compile to one shared receipt model
'''
path.write_text(text)

# open questions append and references rename
for p in [root/'README.md', docs/'00-status.md', docs/'50-roadmap.md']:
    txt = p.read_text().replace(old_open, new_open)
    p.write_text(txt)
path = new_open_path
text = path.read_text()
if '## 34) How strict should default exit semantics be before departure truth becomes either noisy or too magical?' not in text:
    text += '''

## 34) How strict should default exit semantics be before departure truth becomes either noisy or too magical?

The archive is now clearer that exit intent should use first-class exit plans, residue findings, and exit receipts, but one policy seam remains open:

- when should `decommission` be allowed to preserve recovery material by default versus forcing explicit keep/discard choices
- how much unresolved remote or time-bound residue is acceptable before an exit may still be called “complete” rather than “applied with residue”
- whether some exit classes should always force follow-up review when offline peers or remote providers could still retain disclosure or byte residue
- how much ergonomics may stay in domain-specific verbs before the unified exit contract starts disappearing behind aliases again

This matters because weak defaults recreate uninstall and remove folklore, while overly ceremonial defaults could make ordinary cleanup feel harder than the risk actually warrants.
'''
path.write_text(text)

# interface/workbench map maybe README status references open q already handled

# update revision mentions in docs/00 maybe enough. create maybe no more.
