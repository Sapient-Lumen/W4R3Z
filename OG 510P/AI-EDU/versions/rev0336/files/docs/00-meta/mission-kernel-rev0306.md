# rev0306 mission kernel

`rev0306` keeps the live mission narrow: make `FT-0181` easier to complete with
real owner-reviewed evidence and harder to advance with local byproducts. The
archive still has no real accepted owner packet, no accepted `SRC2+` evidence, no
real live-window result, no public-claim upgrade, and no closure.

## Heart of the work

The next scarce event is not another registry. It is a real owner return that can
survive source, minimization, review, custody, acceptance, public-language,
lifecycle, and closure checks without laundering local scratch into evidence.

The cube should therefore optimize for three things:

1. one obvious command for the next field step;
2. no plausible way for checker/release scratch to impersonate owner input;
3. no new doctrine unless a real returned packet exposes a concrete gap.

## rev0306 correction

`rev0304` split field scratch from checker scratch. `rev0305` fixed operator-local
clock drift. `rev0306` closes the returned-input seam: a CSV under
`scratch/checks`, `scratch/releases`, legacy `scratch/<other>`, or any
check/smoke/test/fixture lane is not a returned owner packet.

The intended returned CSV locations are now explicit:

```text
/path/outside/the/archive/returned-owner-reply.csv
scratch/field/ft0181/.../returned-owner-reply.csv
```

The normal path remains:

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv
```

Then execute only the emitted command. Direct intake remains a repair/debug path,
not the ordinary operator path.

## Non-evidence boundary

This revision adds no evidence class and no closure authority. A returned-reply
session, field-next docket, intake bundle, workbench seed, review brief, context
receipt, audit, checker fixture, or release-control example remains local
routing material only. It is not owner evidence, not `SRC2+` acceptance, not
custody, not public-summary support, not service-record authority, not lifecycle
movement, and not closure.
