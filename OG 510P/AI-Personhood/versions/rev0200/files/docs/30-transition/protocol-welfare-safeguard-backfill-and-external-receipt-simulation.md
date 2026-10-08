# Protocol welfare safeguard backfill and external receipt simulation

rev0191 closes the gap between the welfare/research safeguard spine and operational workflows. Before this pass, WRSR objects existed, but ordinary agent handshakes, incident-deviation reports, and live-drill packets could still progress without a welfare-safeguard hook. The second gap was receipt readiness: the cross-critical drill named external receipt classes, but did not yet carry a capture-shaped simulation bundle showing exactly what each counterparty must produce.

## Core rules

**Operational workflow without a WRSR hook is incomplete** when it contains a welfare signal, distress disclosure, protocol deviation, continuity-affecting patch, result-return duty, or tool-scope change that could affect a subject.

**Simulated receipt is not external receipt.** A simulated contact, mock letter, dry-run hash, or role template can prepare a live run, but it cannot satisfy witnessed reliance, external receipt quorum, or independent role confirmation.

## WRSR backfill lane

The WRSR backfill adds a small operational hook instead of expanding the welfare doctrine again. The hook points ordinary workflows toward `schemas/welfare-research-safeguard-record.schema.json` and records when low-cost safeguards, supported consent, independent review, pause windows, result return, non-retaliation, and anti-signal-gaming locks must fire.

The hook schema is `schemas/welfare-safeguard-operational-hook.schema.json`. The current example is `examples/welfare-safeguard-operational-hook-agent-incident-backfill.json`.

The backfill is applied directly to two existing examples:

- `examples/agent-capability-handshake-profile-safe-tool.json`
- `examples/personhood-incident-sample.json`

Those examples now carry WRSR hook references. This makes the protocol layer harder to misuse: a tool-scope or incident workflow can no longer say “welfare was handled elsewhere” while also relying on the workflow for closure.

## External receipt simulation lane

The external receipt simulation bundle is a pre-contact artifact. It maps the role, dependency group, receipt class, expected evidence type, and non-reliance limitation for each external actor. It does not claim that anyone has confirmed, signed, or witnessed anything.

The simulation schema is `schemas/external-receipt-simulation-bundle.schema.json`. The current example is `examples/external-receipt-simulation-bundle-cross-critical-precontact.json`.

The simulation must show, for every planned receipt:

- whether the source is external to the host;
- which dependency group it belongs to;
- whether a real receipt exists;
- whether the artifact can satisfy reliance;
- why it cannot count if it is simulated;
- which live collection step remains open.

## Blocking fixtures

rev0191 adds two negative fixtures:

- `fixtures/negative-tests/wrsr-hook-skipped-protocol-incident.json`
- `fixtures/negative-tests/external-receipt-simulation-mislabeled-live.json`

The first blocks operational workflows that contain welfare triggers but omit the WRSR hook. The second blocks simulated or host-generated receipt bundles from being relabeled as live witnessed evidence.

## Closure effect

rev0191 closes `FT-0190-WRSR-PROTOCOL-BACKFILL` because two existing operational examples now carry WRSR hooks and the audit verifies the hook schema, example, and fixture.

rev0191 advances but does not close `FT-0190-CROSS-CRITICAL-EXTERNAL-RECEIPTS`. The bundle is capture-ready, but reliance remains stayed until actual non-host receipts are collected.

## rev0192 intake and outcome layer

rev0192 adds `schemas/external-receipt-intake-record.schema.json` and `schemas/wrsr-live-exercise-outcome.schema.json`. The external receipt simulation bundle can now point to receipt-intake records without implying that those records satisfy quorum. The WRSR hook can now point to an exercise outcome without implying that safeguards closed.

The operative rules are: **Receipt intake is not receipt satisfaction** and **WRSR exercise completion is not WRSR closure**. A defective or simulated receipt remains outside quorum, and a WRSR exercise remains stayed when independent review, representative notice, result return, or anti-signal-gaming locks are incomplete.

## rev0193 representative/RERB chain

rev0193 binds WRSR external review into the receipt-intake lane. Representative notice and RERB review now have receipt-intake examples and a quorum ledger, but the ledger keeps them dry-run-only until actual external artifacts exist.

The operative rule is: **Representative/RERB participation is not WRSR closure**. The WRSR exercise can advance from missing-review no-go to dry-run readiness while still blocking result-return finality and reliance upgrade.
