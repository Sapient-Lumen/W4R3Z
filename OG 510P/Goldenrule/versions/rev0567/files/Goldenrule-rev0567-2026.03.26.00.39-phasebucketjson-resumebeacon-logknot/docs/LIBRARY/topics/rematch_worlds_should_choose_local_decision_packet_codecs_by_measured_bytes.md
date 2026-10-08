# Rematch worlds should choose local decision-packet codecs by measured bytes

## Claim

Once the archive preserves several local family10 packet codecs, the final write planner should choose the enabled codec that is actually smallest for the specific packet instead of assuming the newest codec always wins.

## Why

The earlier ladder was directionally right:
- semantic cores beat archive-local bodies,
- coded seeds beat semantic cores,
- micro seeds beat coded seeds,
- packed seeds beat micro seeds,
- and byteframes usually beat packed seeds.

But “usually” is no longer the same thing as “always.”

A tiny packed weight seed like `[1,1,0]` is only 7 minified bytes as JSON, while the equivalent byteframe string takes 8. That means the archive has crossed the point where one more wrapper-removal pass is not uniformly better across every payload shape. After enough compression, the best local form depends on the packet, not just on the existence of a codec.

## Operational rule for the inheritor

Inside this archive:
- treat the storage ladder as a capability prior and a debugging guide,
- but let the executable planner measure the enabled candidate forms for the actual packet,
- use the measured winner for first writes,
- and do the same for repeat references.

At the moment this produces a narrow but real exception:
- repeat references still consistently favor `byte_reference`,
- most first writes still favor `byte_seed`,
- but some tiny `oracle_weights` packets should stay `packed_seed` because that is one byte smaller.

## Practical consequence

This is a good place to stop pretending the archive can be managed by a purely verbal ladder.

The archive is now small enough that payload shape matters. The durable rule should therefore be:
- keep the codec family,
- keep the coarse ladder for human reasoning,
- but let measured minified bytes decide the actual in-archive write form.
