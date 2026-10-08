# rev0307 activation source-packet firebreak refactor

## Problem

Activation receipts are near the point where the rail could authorize an active-change ticket. They already require the source packet hash to match the decision-chain source CSV hash. Hash matching is necessary but not sufficient: a checker or release artifact can be byte-identical to the field packet and still be the wrong operational source.

If a maintainer can pass `--source-packet scratch/checks/.../real-owner-packet.csv`, the rail may waste review effort or create false confidence that validator output is owner material.

## Change

`source_packet_path_allowed()` now mirrors the returned-CSV lane firebreak. Activation receipt source packets are allowed only when they are external to the archive or deliberately staged under:

```text
scratch/field/ft0181/
```

They are blocked from:

```text
scratch/checks/
scratch/releases/
scratch/<legacy-non-field-lane>/
*/check-*
*/smoke-*
*/test-*
*/fixture-*
```

The activation receipt CLI help now says the source packet must be outside archive-controlled surfaces or deliberately under `scratch/field/ft0181/`.

## Regression coverage

`tools/check_ft0181_activation_receipt.py` creates a valid field-lane packet, then copies the same bytes into checker scratch. The checker-scratch packet must fail with `ACTIVATION-RECEIPT-SOURCE-PACKET-BLOCKED` even though the hash is valid. Downstream activation/live-window and post-readout checker fixtures now source their activation packets from field-lane validation directories rather than checker scratch.

## Boundary

This is a source-path control, not evidence. No owner is contacted, no CSV is accepted, no `SRC2+` packet is imported, no live window is authorized by this revision alone, and no public claim or closure state changes.
