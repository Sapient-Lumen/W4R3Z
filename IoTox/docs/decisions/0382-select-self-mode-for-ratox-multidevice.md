# ADR 0382: Select self mode for Ratox-first multidevice

Status: accepted for documentation and product direction; first implementation slice present
Date: 2026-09-17

## Context

IoTox's terminal story is no longer only “a default-off construction surface
exists.” The desired product is that an owner can log into two machines they
control and do SSH-like work over IoTox. Tox does not provide a satisfactory
multidevice identity model for that goal, and IoTox should not pretend that a
Tox friend list, a synchronized Tox account, or a route key is the ownership
domain.

The existing ingredients are already IoTox-shaped:

- a RecallRoot-derived owner principal;
- independent stable device principals;
- a signed authority ledger with `interactive.terminal`;
- profile-bound Ratox terminal execution;
- peer aliases and explicit pairing;
- route identities that remain separate from authority; and
- a single binary that can be both Agent and local terminal controller.

The missing decision is where the product default changes. If Ratox remains
globally default-off forever, IoTox never becomes the self-machine remote
control tool the project now wants. If Ratox becomes silently default-on for
ordinary upgrades, the repo widens the terminal attack surface without a
deliberate owner decision.

## Decision

Introduce and document `--mode self` as the explicit self-machine mode.

In self mode:

- the Ratox host role is selected by default;
- the same-user terminal controller is selected by default;
- the init porch writes explicit Ratox profile-store and helper paths into the
  canonical config;
- direct Agent invocation fills safe defaults for omitted Ratox profile-store
  and helper paths; and
- all existing Ratox authority/profile/process boundaries stay in force.

Manual mode remains default-off for Ratox. `--enable-ratox-terminal` and
`--enable-ratox-terminal-client` remain the explicit low-level role flags, but
the human product path for owner-controlled machines is now:

```sh
iotox init plan --root ~/.local/state/iotox --mode self --enable-sync
iotox init write-config --root ~/.local/state/iotox --mode self --enable-sync
iotox terminal profile plan shell self-shell "$USER" --store ~/.local/state/iotox/ratox
cat RECALLROOT.txt | \
  iotox authority-delegate-self-recall-stdin alias:laptop operator interactive.terminal
iotox terminal alias:laptop --reconnect
```

Self mode does not install a shell, bind a principal, grant authority, enable
sudo, choose a privacy route, or make Tox friendship authoritative. The remote
peer still cannot choose executable, argv, environment, cwd, profile, port
forwarding, or sudo policy.

## Consequences

Documentation must stop saying simply “Ratox is default-off.” The accurate
claim is:

```text
manual mode: Ratox roles are off unless explicitly enabled
self mode:   Ratox host/controller are selected by default, then
             profile binding and authority decide all effects
```

The next architectural target is self-machine multidevice above Tox:

1. a reviewable self-join artifact or ceremony for a new machine that has the
   owner key;
2. an owner-signed roster of self machines, aliases, route identities, and
   minimum accepted generations;
3. reciprocal narrow grants selected by the owner, starting with
   `interactive.terminal`;
4. retirement and revocation for lost, sold, reinstalled, or distrusted self
   machines;
5. route-policy representation that refuses silent Tor/I2P-to-native fallback;
   and
6. rejection tests for wrong owner, wrong stable principal, stolen Tox route
   identity, stale roster, revoked member, missing profile, and missing
   `interactive.terminal`.

This is not a Tox multidevice project. Tox remains the carrier. IoTox owns the
self-domain semantics above it.

## Evidence

The first slice is source-level and process-tested:

- `--mode self` is accepted by Agent/config parsing;
- self mode selects Ratox host and local terminal controller;
- init plan/write-config persist `--mode self`, profile-store, and helper
  paths;
- `iotox help self` describes the activation and authority boundary; and
- docs coherence/human CLI tests check the new topic and self-mode config
  rendering.

ADR 0383 supplies the first separate implementation ADR and evidence gate for
the signed self-swarm roster. Further authority widening still requires later
ADRs; the roster v1 workflow remains reviewed, explicit, and bounded to the
existing authority grant/revoke paths.
