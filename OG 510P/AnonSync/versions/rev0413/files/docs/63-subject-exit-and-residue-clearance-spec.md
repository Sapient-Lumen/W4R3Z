# Subject Exit and Residue Clearance Spec

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
