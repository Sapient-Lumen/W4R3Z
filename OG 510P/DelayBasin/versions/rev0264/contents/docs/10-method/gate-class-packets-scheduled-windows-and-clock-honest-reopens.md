# Gate-class packets, scheduled windows, and clock-honest reopens

This is the compact successor surface for `OQ-0115`.

DelayBasin already had a live gate-class family, but one pressure kept recurring in durable ledgers:
some future-change truth is not mainly “check again someday” and not mainly “wait for new evidence.”
It is **clock-governed**.
A rollout changes at a named future time.
A shadow test starts later and stops automatically after a duration.
A cooldown, expiry, soak window, or review horizon is already doing real public work.

The compact repair is:
**preserve one explicit `scheduled-window` gate class when the load-bearing future trigger is a named time, duration, cadence, or bounded time window rather than a generic repeat pass.**

This does **not** justify a calendar court, scheduler constitution, or general timing board.
It only sharpens the controlled family that DelayBasin already uses on discharge-bearing rows.

## Practice / observation

DelayBasin's current ledgers already distinguish state, action lane, and gate class.
That was enough to keep many rows from collapsing into blocker folklore.
But a smaller ambiguity remained:
- some rows are truly waiting for **another deliberate pass** without a precommitted clock;
- some rows are truly waiting for **new evidence** that may arrive at an unknown time;
- some rows are truly waiting for **overflow** beyond the compact family;
- some rows are waiting on a **negative-transfer / non-fit** judgment;
- and some rows are actually governed by a **scheduled window / cooldown / expiry / soak horizon / named future time** that the archive already knows.

Flattening the last case into `repeat-pass` loses something real.
A row with `repeat-pass` says “someone should come back and check again.”
A row with `scheduled-window` says “the governing trigger is already clock-shaped, and the prose must preserve the relevant time, duration, cadence, or horizon honestly.”

## External pressure from scheduled systems and bounded timed comparisons

Current workflow and rollout systems repeatedly separate timed triggers from generic reread or review posture.

1. LaunchDarkly documents **scheduled flag changes** that change targeting rules at future points in time rather than waiting for a later operator to remember the moment. That pressures DelayBasin to distinguish explicit future-time triggers from generic repeat-pass prose. ([`REF-0796`](../00-meta/bibliography.md))

2. EventBridge Scheduler documents **one-time, rate-based, and cron-based** schedule types as first-class schedule families. That pressures DelayBasin to preserve time-governed trigger kind as a compact family member rather than reconstructing it from local prose. ([`REF-0797`](../00-meta/bibliography.md))

3. GitHub Actions documents `schedule` as a distinct workflow trigger family and even exposes the triggering schedule in workflow context. That pressures DelayBasin to keep the difference between “scheduled window fired” and “someone manually reran a repeat pass” legible. ([`REF-0798`](../00-meta/bibliography.md))

4. GitHub also documents that scheduled workflows may be delayed or dropped under load. That pressures DelayBasin to preserve not only that a trigger is clock-governed but also that exact timing certainty still belongs in neighboring prose rather than in the token alone. ([`REF-0799`](../00-meta/bibliography.md))

5. SageMaker shadow tests can be scheduled to start later, run for a specified duration, and complete automatically when that duration ends. That pressures DelayBasin to distinguish bounded timed windows from ambient “revisit later” language even in comparison workflows it already uses as pressure. ([`REF-0790`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **gate-class packet / future-trigger kind** on durable live items when the future trigger would otherwise drift across prose, and the admitted family should now be **`concrete-evidence`**, **`repeat-pass`**, **`scheduled-window`**, **`overflow`**, and **`negative-transfer`**. Use **`scheduled-window`** only when the decisive trigger is already a named future time, duration, cadence, cooldown, expiry, soak horizon, or scheduled observation window in neighboring prose. Keep the exact time, timezone, cadence, or tolerance in prose. Keep the family narrow. Extend only explicitly and fail closed on drift.

## `scheduled-window` vs `repeat-pass`

This distinction is the heart of the successor surface.

- **`repeat-pass`** — a later operator should deliberately rerun, revalidate, or reconsider the item, but the archive is not claiming that a named clock edge is what mainly governs the change.
- **`scheduled-window`** — a named time, duration, cadence, cooldown, expiry horizon, soak end, or other clock-shaped window is already the governing trigger class, even though the exact timing details still live in prose.

A row may still have action lane `rereview` under either gate class.
The difference is whether the rereview is merely expected later or is explicitly tied to a clock-governed window the archive already knows.

## Countermodels / probes

1. **Repeat-pass-is-enough countermodel**
   - Maybe every legitimate timed case is just a repeat pass with extra prose.
   - Probe: compare later rereads on rows with explicit cooldown or expiry language and inspect whether operators keep reconstructing timing truth inconsistently when only `repeat-pass` is preserved.

2. **Calendar-inflation countermodel**
   - Any timed token may start a broader scheduler or calendar court.
   - Probe: keep only one extra token, preserve time details in prose, and quarantine any broader scheduling-governance import.

3. **Token-without-causal-force countermodel**
   - `scheduled-window` may look neat without changing interpretation.
   - Probe: inspect whether later passes more honestly preserve soak-end, expiry, or cooling posture once the token is explicit.

## Design consequences

- extend the controlled `gate_class` family by **one** token only: **`scheduled-window`**;
- use it only on governed discharge-bearing durable queues and ledgers where the future trigger is already clock-shaped in neighboring prose;
- keep exact dates, durations, timezones, or review horizons outside the token itself;
- do **not** turn the token into a scheduler, calendar court, or lifecycle board;
- and quarantine any stronger timing-governance story unless repeated overflow shows that one compact token is no longer enough.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something slightly sharper than “what is live” and “what is next.”
It is preserving whether the next legitimate move is governed by **evidence**, **a human-chosen repeat pass**, **a clock-shaped window**, **overflow**, or **non-fit**.
That matters because later stateless passes can otherwise remember the row yet still misread what kind of future event is actually allowed to move it.
