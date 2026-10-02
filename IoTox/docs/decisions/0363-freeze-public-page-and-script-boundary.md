# ADR 0363: Freeze public page and script boundary

Status: accepted design direction.

Date: 2026-09-10

## Context

IoTox now has enough implemented surface that a new reader needs a coherent
product entrance before reading the full revision log. The local Sandworm copies
show the desired public-document shape: a single-file introduction with strong
visual identity, direct first commands, and authority warnings placed near the
operator actions they govern.

MonsterNix, especially the m16-derived Foundation/Werx objects, shows a separate
lesson: host integration should be object- and receipt-oriented. Source
admission, machine-specific projection, proof execution, and switch/apply
authority belong to the host management layer, not to an upstream project
wrapper pretending to understand every machine.

IoTox also needs a public script path. That script must make Bash/Nix operation
easier without becoming a second product binary or a second authority plane.

## Decision

Add `docs/product-page.md` as the publishable human entrance. It describes IoTox
as one self-owned device-agent binary over Tox, with ordinary Unix operation,
explicit authority, synchronization, Ratox/SSH-shaped control, route boundaries,
and evidence/nonclaim language.

Add `docs/script-distribution-plan.md` as the accepted split between:

- a script for everyone: repository/operator guidance for doctor, build, test,
  run, sync, terminal setup, datacube export, and cleanup;
- a script for Monsternix: an inert adapter that admits exact IoTox source or
  package objects, runs proof loops, emits receipts, and projects host-specific
  service configuration only through explicit MonsterNix acceptance;
- the IoTox product binary: the only layer that owns device identity, authority,
  sync protocol behavior, route policy, and Ratox terminal authorization.

Neither script may grant device authority, invent a second sync signer, choose
remote-visible paths, enable sudo, import secrets, publish content-bearing
evidence, or install a service by mere presence.

Commit the first two scripts inside that boundary:

- `tools/iotox-repo.sh` provides `help`, `doctor`, `build`, `test quick`,
  `test full`, `datacube`, and `clean` over existing repository tools.
- `tools/iotox-monsternix-adapter.sh` provides read-only `help`, `doctor`, and
  `plan` so the intended MonsterNix porch is inspectable before any
  MonsterNix-side writer exists.

## Consequences

The public page becomes the short explanation for outsiders and future ChatGPT
or website contexts. It is explanatory material, not protocol authority.

The first script implementation should stay deliberately small. Read-only
doctor/status/plan behavior, exact underlying command display, clean build/test
entry points, dry-run cleanup, and datacube export come before guided mutating
operations.

Monsternix support should be developed as an adapter after MonsterNix accepts an
exact command/projection contract. IoTox should donate useful packaging and proof
objects to that ecosystem, but it must not couple its portable device semantics
to one host manager.

This ADR freezes the boundary those scripts must preserve. The committed
scripts are only the first safe subset of that surface.
