# Transfer packets, reviewed-datacube sets, disposition classes, and overflow tests

This is the compact successor surface for `OQ-0112`.

DelayBasin already had a real `DATACUBE-TRANSFER-LEDGER.json`, but one pressure kept recurring in durable rereads:
later careful passes could still see that a comparison happened and yet have to replay the whole narrative to recover **which reviewed datacubes mattered, which disposition actually applied, and which tempting neighboring move was consciously left out**.
Some comparison passes produce a bounded take.
Some only lend supporting pressure.
Some explicitly defer, reject, or retire a transfer move.
When that compact outcome stays ambient, the ledger exists on paper but not yet as an easy successor surface for future reuse.

The compact repair is:
**preserve one explicit transfer packet that says the existing transfer-ledger plus admitted `assimilation_state` family is already the right bounded place to keep multi-datacube comparison outcome truth public, while leaving fuller rationale, evidence excerpts, and rich comparison prose in surrounding surfaces.**

This does **not** justify a transfer court, import senate, comparative precedent board, or standing cross-datacube governance layer.
It only resolves the missing compact successor surface for a ledger DelayBasin already admitted.

## Practice / observation

DelayBasin's transfer ledger already records reviewed datacubes, local gap, bounded take, explicit non-take, and open transfer question.
That was enough to stop many comparison passes from dissolving completely into one revision receipt.
But a smaller gap remained:
- some later rereads still had to reconstruct whether the pass ended in **imported** pressure or only **supporting-only** pressure;
- some still had to reconstruct whether a larger neighboring controller was explicitly **deferred** or **rejected** rather than merely forgotten;
- and some needed an explicit compact reminder that the **reviewed set itself** is load-bearing archive state, not just color around whichever imported ratchet happened to land.

The archive therefore did not need a bigger comparative controller first.
It needed one compact packet that says the admitted ledger plus controlled disposition family is already the right public place to preserve **comparison outcome class**.

## External pressure from decision logs, review states, lineage, and migration practice

Current decision and migration systems repeatedly separate reviewed options, exact lineage, and explicit outcome classes.

1. Google Cloud's ADR overview says ADRs capture the key options available, the requirements driving a decision, the decision itself, and the record of prior decisions when choices change. That pressures DelayBasin to keep reviewed alternatives and changed decisions compactly recoverable instead of leaving them trapped in long narrative recap. ([`REF-0807`](../00-meta/bibliography.md))

2. The ADR Templates guidance says considered options with pros and cons are crucial, and that status metadata belongs alongside the decision. That pressures DelayBasin to keep explicit non-takes and disposition class visible rather than flattening a comparison pass into one winning import summary. ([`REF-0808`](../00-meta/bibliography.md))

3. GitHub's required-review flow keeps comment, approve, request-changes, dismissal, and re-approval distinct rather than treating review as one vague recap. That pressures DelayBasin to preserve discrete comparison outcomes and rereview posture instead of collapsing them into remembered judgment. ([`REF-0809`](../00-meta/bibliography.md))

4. SageMaker lineage tracking preserves exact artifacts and workflow history, while model approval status keeps `PendingManualApproval`, `Approved`, and `Rejected` distinct and actionable. That pressures DelayBasin to keep exact reviewed-source lineage and disposition state queryable rather than ambient. ([`REF-0810`](../00-meta/bibliography.md), [`REF-0811`](../00-meta/bibliography.md))

5. OpenTelemetry's HTTP semantic-convention migration explicitly allows `http/dup` during phased rollout rather than forcing a binary old-versus-new collapse. That pressures DelayBasin to keep supporting-only or dual-carry comparison posture visible rather than pretending every reviewed pattern was either fully imported or fully discarded. ([`REF-0812`](../00-meta/bibliography.md))

## Working synthesis

> DelayBasin should preserve one compact **transfer packet / reviewed-datacube set / disposition class** on multi-datacube comparison passes, and the admitted family should stay the existing `assimilation_state` tokens **`imported`**, **`supporting-only`**, **`deferred`**, **`rejected`**, and **`retired`**. Use the packet only to foreground the reviewed set, the active disposition class, the bounded take if any, the explicit non-take, the anchor surfaces, and the still-open transfer question. Keep rich rationale, evidence excerpts, and comparative prose in the surrounding ledger rows and cited sources. Keep the family narrow. Extend only explicitly and fail closed on drift.

## Reviewed set vs disposition vs anchor surfaces

This distinction is the heart of the successor surface.

- **reviewed datacube set** says which neighboring archives or external systems were actually inspected.
- **disposition class** says what outcome currently applies: imported, supporting-only, deferred, rejected, or retired.
- **bounded take / explicit non-take** says what compact move was admitted and what tempting move stayed out.
- **anchor surfaces** say where the admitted result now lives inside DelayBasin.
- **open transfer question** says what comparison pressure is still live after the pass.

A pass can review six datacubes, stay `supporting-only`, still admit one compact packet, and explicitly reject a broader governance story.
A pass can be `deferred` even when the reviewed sources are high quality.
A pass can be `retired` even when the underlying comparison history remains valuable.

So the packet does not add a new court.
It only makes the already-admitted separation easier to reopen honestly.

## Countermodels / probes

1. **Existing-transfer-ledger-is-already-enough countermodel**
   - Maybe the current ledger rows are already compact enough and a packet adds no real reuse value.
   - Probe: compare later rereads and inspect whether operators still need to replay the surrounding prose to recover reviewed-set and disposition truth.

2. **Status-without-reviewed-set countermodel**
   - Maybe disposition alone is enough and the reviewed datacube set is just narrative ornament.
   - Probe: try to recover which neighboring archives were consciously not taken and whether that answer survives without the reviewed-set foregrounded.

3. **Need-a-broader-transfer-court-now countermodel**
   - Maybe DelayBasin should jump directly to standing comparative governance.
   - Probe: first test whether one compact packet over the existing ledger plus `assimilation_state` family already stops repeated transfer re-argument before paying for a larger court.

## Design consequences

- keep the controlled `assimilation_state` family unchanged in `WITNESS-VOCABULARY.json` for now;
- use the packet only on real multi-datacube comparison passes that already justify transfer-ledger rows;
- preserve one compact successor surface for the family so later passes can reopen comparison outcome truth directly;
- keep richer rationale and source detail in the surrounding ledger row and bibliography-backed method note rather than in the compact class token;
- and quarantine any stronger transfer court, import senate, or comparison-memory board unless repeated overflow shows that one compact packet is no longer enough.

## Overflow test

Reopen the stronger machinery only if one compact packet is no longer enough — for example, if the archive honestly needs standing comparative precedent, cross-pass transfer arbitration, or durable import-governance classes that cannot be expressed as one bounded reviewed-set plus existing disposition family.

Until then, prefer this compact successor surface over a transfer court, import senate, or comparison-memory board.

## Transformer-facing implication

If this frame survives, then DelayBasin is preserving something slightly sharper than “we compared some neighboring archives.”
It is also preserving **what class of comparison outcome currently applies and which reviewed set earned that class**.
That matters because later stateless passes can otherwise inherit the fact that comparison happened while still losing the compact public answer to what was actually taken, left supporting-only, or consciously left out.
