# rev0304 cube deep audit

## Audit focus

This audit focused on the cube's current vice: documentation mass can grow faster
than field evidence. The question was where a small implementation change could
reduce the chance of another explanatory turn and increase the chance of real
owner-route progress.

## Highest risk found

The live `FT-0181` route is clean but fragile to local operator context. The cube
has many valid validators, examples, and late-stage gates; the real shortage is not
governance coverage. The shortage is owner-reviewed input. Any local ambiguity that
makes the maintainer inspect scratch instead of preparing or routing the owner
packet is operationally expensive.

Rev0303 fixed contamination by filtering checker scratch. Rev0304 lowers the
cognitive load further by moving default field work into `scratch/field/ft0181` and
checker work into `scratch/checks`.

## Substantive correction

The router no longer starts from the whole scratch tree by default. A clean run of:

```bash
make owner-field-work
```

now writes and scans only the field lane. The safe local first-contact packet is
prepared at:

```text
scratch/field/ft0181/owner-request-packets/aiedu-sr-003-first-contact/
```

The immediately returned router command is the real human boundary:

```text
make owner-after-human-send ... OUT=scratch/field/ft0181/owner-after-human-send/...
```

That is the useful stopping point. The archive still cannot claim a send, response,
owner review, learning outcome, service improvement, custody, acceptance, public
support, or closure.

## Refactor audit

The refactor touched the field execution plane rather than the registry plane:

- field router defaults;
- router command templates;
- FT-0181 tool default output roots;
- checker scratch fixture roots;
- field-next regression expectations;
- current operator-facing navigation.

No new schema family was added. No followthrough was closed. No public claim word
was upgraded.

## What should change in behavior

Maintainers should now treat `scratch/field/ft0181` as the only default live rail.
They should not pass `SCRATCH=scratch` casually. Passing `SCRATCH=scratch` is a
legacy/debug move and should be named as such in the local session.

The right next external action is still one of two things:

1. prepare/adapt/send the bounded first-contact packet outside the archive, then
   record only the local after-human-send state; or
2. if a real owner CSV/context already exists, run `owner-field-next` with that
   file and execute only the emitted guarded command.

## Remaining waste to resist

The cube contains enough late-stage gates to protect against fake closure. More
doctrine would now be low yield unless a real returned packet exposes a concrete
failure. The work should bias toward running the field lane, not designing a more
complete theory of the field lane.
