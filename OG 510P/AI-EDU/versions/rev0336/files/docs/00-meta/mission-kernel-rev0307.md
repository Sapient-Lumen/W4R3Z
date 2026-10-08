# rev0307 mission kernel

`rev0307` keeps the mission pointed at the same scarce event: real owner-reviewed `FT-0181` evidence that can move through the local rail without local byproducts pretending to be source truth. The archive still has no accepted owner packet, no accepted `SRC2+` evidence, no real live-window result, no public-claim upgrade, and no closure.

## Heart of the work

The next completion risk is not broad policy. It is the near-acceptance seam after a returned CSV has survived intake, workbench, review, decision, and change-ticket gates. At that point, an activation receipt asks for a `SOURCE_PACKET` with the same hash as the decision-chain source. Before this pass, a byte-identical checker or release scratch artifact could still be named there.

The correct mission behavior is simple: a real activation source packet must come from outside the archive or from the deliberate live field lane. Checker, release, legacy, smoke, test, and fixture scratch can test the rail, but they cannot become the activation source packet.

## rev0307 correction

`rev0306` blocked fake returned CSV intake from non-field scratch. `rev0307` applies the same operational boundary to activation-receipt `SOURCE_PACKET` paths. Allowed packet locations are now explicit:

```text
/path/outside/the/archive/real-owner-packet.csv
scratch/field/ft0181/.../real-owner-packet.csv
```

Blocked packet locations include:

```text
scratch/checks/...
scratch/releases/...
scratch/<legacy-non-field-lane>/...
*/check-*
*/smoke-*
*/test-*
*/fixture-*
```

## Non-evidence boundary

This revision does not accept evidence. It only prevents a local checker or release artifact from serving as the last source-packet argument before an active-change receipt. Activation receipts remain local controls: not evidence, not custody, not public support, not service-record authority, not lifecycle movement, and not closure.
