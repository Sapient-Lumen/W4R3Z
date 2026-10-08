# 464 — Coupled change follow-through matrices, partial-completion warnings, and closure

## One-line thesis

Material changes to consequential public-AI systems should carry a coupled-surface follow-through matrix that shows which linked governance surfaces have been updated, which remain stale, and which claims stay blocked until closure, so code completion does not impersonate governance completion.

## Why this matters

A consequential public-AI change rarely lands in one place.

A model is updated, but the public card still names the old basis. A prompt or rule changes, but the appeal packet schema does not. Thresholds move, but operator runbooks and training slides stay old. A supplier dependency changes, but the approved use-case register, monitoring thresholds, or legal review packet still describe the prior arrangement. Teams often know this informally. The archive needs a way to govern it explicitly.

The current datacube already covers material-change notice, retesting after change, release authority, review freshness, monitoring truth, and canonical public heads. What it still lacked was one note for the **follow-through problem itself**: the fact that one change creates a set of linked obligations across multiple surfaces, and that partial completion must remain visible until those obligations are closed. The archive should therefore require a coupled change matrix and block strong claims while closure is incomplete.

## Pattern pack

### 1. Open one change object with an explicit affected-surface list

A material change should open a single reviewable object that names the affected surfaces, such as:

- model, prompt, rule, threshold, or retrieval basis,
- public notice, system card, or transparency record,
- impact dossier or peer-review packet,
- approved use-case register or authority map,
- runbooks, training, and escalation guidance,
- monitoring rules, dashboards, and alert thresholds,
- appeal packet schema, logs, or retention joins,
- supplier records, contracts, and dependency registers,
- accessibility or parity-critical interface surfaces.

The point is to stop one consequential change from fragmenting into many half-remembered chores.

### 2. Track each linked surface with a distinct closure state

At minimum, each surface should carry a state such as:

- unchanged and verified still accurate,
- updated and verified,
- update required and pending,
- update blocked with reason,
- intentionally retired,
- or not applicable with justification.

This prevents “done” from hiding a mixed reality.

### 3. Separate implementation completion from governance closure

A runtime or policy change may be technically deployed before the archive is fully current. When that happens, the system should keep those facts separate:

- implementation state,
- review state,
- disclosure state,
- training state,
- and evidence-packet state.

A green deploy should not automatically turn the rest of the matrix green.

### 4. Warn visibly when operation outruns follow-through

If the changed system is already live while linked surfaces remain stale, the archive should surface a visible partial-completion warning showing:

- what changed,
- which surfaces remain stale,
- what the operational risk is,
- who owns the remaining work,
- and what claims are temporarily narrowed or blocked.

Partial truth is better than silent overclaim.

### 5. Block strong claims until critical surfaces are closed

Some claims should remain unavailable until specific linked surfaces are complete, for example:

- do not call the system fully reapproved while the dossier still reflects the old workflow,
- do not call notice current while the public surface still names the old basis,
- do not claim operators are ready while their runbook and drill pack remain stale,
- do not claim appeals are preserved while packet joins or retention schedules lag behind the change.

Closure rules should be explicit rather than left to social memory.

### 6. Preserve a durable closure packet

When follow-through is complete, the archive should preserve a compact closure packet showing:

- the triggering change,
- the linked surfaces reviewed,
- the state transition of each,
- outstanding exceptions if any,
- final approver or closer,
- and the date of closure.

That packet becomes future evidence that the institution governed the whole change, not only the code.

### 7. Reopen the matrix when downstream drift appears

Closure should not be treated as permanent if later evidence shows drift, such as:

- a stale mirror resurfaces,
- training remains out of sync with the live path,
- monitoring thresholds still reflect the old behavior,
- or a supplier-side change invalidates part of the closed packet.

Follow-through should be reopenable when the linked reality diverges again.

## Guardrails

- Do not let technical deployment status stand in for full governance closure.
- Do not collapse multiple linked surfaces into one “updated” label.
- Do not hide stale runbooks, notices, or appeal joins behind an otherwise green release.
- Do not treat “not applicable” as a free pass without justification.
- Do not discard the closure evidence once the remaining chores are done.

## Failure modes

- **code-first completion myth**: the implementation is live, so teams assume the governance work is effectively complete.
- **green deploy / red archive**: runtime surfaces are current while public or review surfaces remain stale.
- **training lag drift**: operators act on the old workflow after the system changed.
- **partial-completion silence**: a live system outruns its own documentation without any visible warning.
- **orphaned correction**: a fix lands but never propagates to the records needed for appeals, monitoring, or later review.

## Practical tests

A follow-through-honest change regime passes when it can answer yes to all of the following:

1. Does every material change open one explicit object listing the linked governance surfaces it affects?
2. Does each linked surface carry a distinct closure state instead of one blended status?
3. Are implementation completion and governance closure kept separate?
4. Do partial-completion warnings surface when live operation outruns follow-through?
5. Are strong claims blocked until the critical linked surfaces are actually closed?

## Compression rule for the archive

If a consequential change can say **the system is updated** but cannot also say **which linked governance surfaces are current, stale, blocked, or closed**, then it is still letting **implementation completion impersonate governance completion**.
