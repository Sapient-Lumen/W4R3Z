# ADR 0383: Implement signed self-swarm roster v1

Status: accepted
Date: 2026-09-17

## Context

ADR 0382 introduced `--mode self` as the explicit product mode for owner-controlled machines. That
mode selects the Ratox host and local terminal controller by default, but it intentionally does not
grant terminal authority, choose a profile, enable sudo, or treat Tox friendship as ownership.

The next gap was multidevice membership above Tox. An owner should be able to log into machines they
control, prove the RecallRoot-derived owner key locally, name those machines, and coordinate narrow
self-machine grants without depending on Tox multidevice semantics or copying Tox savedata.

## Decision

Add a native `iotox self-swarm ...` CLI surface backed by an owner-signed canonical roster:

```text
iotox-self-swarm-v1
owner=OWNER_PUBLIC_KEY_HEX
generation=N
previous-digest=PREVIOUS_UNSIGNED_ROSTER_DIGEST_HEX
member-count=N
member=ALIAS|PRINCIPAL_HEX|TOX_ROUTE_KEY_HEX|ROLE|CAPABILITIES_HEX16|active|0
member=ALIAS|PRINCIPAL_HEX|TOX_ROUTE_KEY_HEX|ROLE|CAPABILITIES_HEX16|retired|GENERATION
signature=OWNER_SIGNATURE_HEX
```

The roster is signed by the RecallRoot-derived owner key over a BLAKE2b-256 digest of the unsigned
canonical body under the `iotox-self-swarm-roster-digest-v1` domain. Member aliases sort
canonically; duplicate aliases, duplicate stable principals, duplicate route keys, unknown roles,
empty capabilities, owner-role grants, retired-only rosters, malformed text, noncanonical hex, and
tampered signatures fail closed.

The public commands are:

```sh
iotox self-swarm help

cat RECALLROOT.txt | \
  iotox self-swarm create-recall-stdin ROSTER ALIAS PRINCIPAL_HEX TOX_KEY_HEX ROLE CAPS

cat RECALLROOT.txt | \
  iotox self-swarm join-recall-stdin ROSTER ALIAS PRINCIPAL_HEX TOX_KEY_HEX ROLE CAPS

cat RECALLROOT.txt | \
  iotox self-swarm retire-recall-stdin ROSTER ALIAS [verification options]

iotox self-swarm inspect ROSTER \
  [--min-generation N] [--expect-owner HEX] \
  [--expect-member ALIAS PRINCIPAL_HEX] [--expect-route ALIAS TOX_KEY_HEX]

iotox self-swarm verify ROSTER \
  [--min-generation N] [--expect-owner HEX] \
  [--expect-member ALIAS PRINCIPAL_HEX] [--expect-route ALIAS TOX_KEY_HEX]

iotox self-swarm grant-plan ROSTER \
  [--from ALIAS] [--role ROLE] [--capabilities CAPS] \
  [--min-generation N] [--expect-owner HEX] \
  [--expect-member ALIAS PRINCIPAL_HEX] [--expect-route ALIAS TOX_KEY_HEX]

cat RECALLROOT.txt | \
  iotox self-swarm grant-recall-stdin ROSTER ALIAS [verification options]

iotox self-swarm retire-plan ROSTER ALIAS [verification options]

cat RECALLROOT.txt | \
  iotox self-swarm revoke-retired-recall-stdin ROSTER ALIAS [verification options]
```

`create-recall-stdin` is no-clobber. `join-recall-stdin` and `retire-recall-stdin` require the
current roster owner to match the reconstructed RecallRoot owner, increment the generation, and link
the previous digest. `grant-plan` renders reviewed authority commands and excludes retired members.
`grant-recall-stdin` applies exactly one active roster member through the existing remote
self-delegation path only after any supplied generation/owner/member/route expectations pass.
`retire-recall-stdin` and `retire-plan` accept the same verification options before mutation or plan
rendering. `revoke-retired-recall-stdin` applies exactly one retired member through the existing
remote revocation path after the same optional roster checks pass.

## Consequences

Self-swarm membership is now an IoTox-owned authority-adjacent artifact above Tox, not a Tox
multidevice feature. It helps an owner coordinate their self machines, but it does not replace the
signed authority ledger. The roster is a plan/apply source for existing authority operations, not a
second constitutional ledger.

The explicit verification knobs are part of the security boundary. Operators and future automation
must carry expected owner, minimum generation, expected stable principal, and expected route key when
they have those facts. A stolen Tox savedata file is not enough: a route key mismatch refuses before
plan output. A retired roster member is not enough: grant apply refuses retired members.

This decision intentionally does not add:

- automatic live fan-out of roster files between Agents;
- an independent per-machine minimum-generation high-water floor;
- a live route proof inside `grant-plan`;
- self-domain route privacy policy or Tor/I2P fallback refusal;
- automatic profile installation or profile binding;
- automatic sudo;
- arbitrary remote exec, port forwarding, or SSH agent forwarding; or
- daemon-side automatic authority widening merely because a roster exists.

Those remain future ADRs if product experience proves they are worth the new state and failure
surface.

## Evidence

The construction evidence is source-level and process-tested:

- `include/iotox/self_swarm.hpp` and `src/self_swarm.cpp` implement canonical encode/decode, digest,
  owner signature, creation, join, retirement, file load/store, inspection, and plan rendering;
- `src/cli.cpp` exposes the native self-swarm commands and keeps RecallRoot input on stdin;
- `tests/test_self_swarm.cpp` covers signed creation, canonical joins, generation floors,
  wrong-member refusal, duplicate alias/principal refusal, tamper refusal, retirement, grant-plan
  retired-member exclusion, retire-plan rendering, and no-clobber creation;
- `tests/test_human_cli.py` drives create/join/inspect/verify/grant-plan/retire flows through the
  real binary, including wrong principal, wrong route key, stale-generation refusal, wrong-route
  grant-apply refusal, stale grant-apply refusal, and retired-member grant refusal; and
- the focused gate passed on 2026-09-17:

```text
ctest --test-dir build/gcc-debug -R 'iotox\.(unit-and-integration|human-cli|docs-coherence)' --output-on-failure
3/3 tests passed
```
