# NATrav

NATrav is a Rust connectivity engine for authenticated peers that need to
communicate through difficult NATs. It combines same-socket discovery, ICE,
mutual-TLS QUIC and Path Proof, TURN/UDP, TURN/TCP, TURN/TLS, and authenticated
HTTPS-CONNECT-carried TURN/TLS relay, controlled hard-NAT birthday probing,
PCP/NAT-PMP/UPnP mapping and evidence-driven policy behind one product owner.

The project is constitutionally LLM-native, not LLM-only. Humans and LLMs can
inspect state, explain evidence, compare policy, propose bounded changes, and
roll them back. An LLM is never ambient authority: credentials, packet sends,
filesystem access, and runtime actions remain explicit and typed.

## Status

`natrav-node` 0.52.0 is the production v0.52 binary inside the explicit
`natrav.node.production_envelope.v52` support envelope. The version response
reports `production_node_claim=true`. Production means that the packaged binary
and declared envelope are supported; it does not mean universal traversal or
that every research mechanism is complete.

The single-node envelope includes:

- persistent identity and managed state, authenticated HTTP/operator and Unix
  application boundaries, bounded resources, recovery, backup, Nix packaging,
  and a hardened NixOS service;
- useful QUIC datagrams and uni/bi streams, graceful close, live redacted
  events and trace snapshots, cancellable operations, and explicit cleanup;
- Direct, TURN/UDP Relay, standalone TURN/TCP, pinned TURN/TLS, and pinned
  HTTPS CONNECT plus inner TURN/TLS Relay, with ordered automatic local
  selection across those Relay service carriers,
  direct-first fallback, Relay-first continuity, multi-TURN,
  role-reversed Direct companion, destination-varied prediction, Trickle, and
  Birthday manual/autopilot profiles with optional bilaterally signed,
  bounded low-TTL priming on retained hard-pool sockets, plus PCP/NAT-PMP/UPnP
  IGD selected-socket Direct through explicit controls, bounded active UPnP
  discovery, or bounded Linux PCP/NAT-PMP source-route discovery, with
  proactive solicited PCP and NAT-PMP epoch-loss detection and same-endpoint recovery, and
  native same-family IPv6 Direct and prediction;
- signed replacement and replenishment protocols, durable application
  reconciliation without payload replay or exactly-once claims, typed
  backpressure, storage-fault outcomes, and restart non-resumption; and
- governed measured-strategy evidence, hidden holdouts, reversible calibrated
  priors, bounded witness custody, issuer/source admission and completion
  records, and adversarial campaigns whose non-claims remain explicit.

NATrav has real local socket and separate-process tests plus Linux,
OpenWrt, FreeBSD/PF, Coturn, KVM, two-NAT, hard-NAT, Relay, Trickle/EOC, and
differential-peer evidence. The active frontier is not first integration. It is
materially distinct ordinary-ICE causality, hard-NAT cohorts and strategies,
independent TURN evidence, continuity/recovery soak, Sentinel trust, and an
independently built NATravOverlay adapter.

Low-TTL kernel-send and ICMP evidence are not NAT-state or traversal proof.
The exact-public one-hop TTL1 control now joins ICMP, pcap, and conntrack and
proves no postrouting mapping in that topology; the matched unprimed arm
traverses. A routed nested Linux-KVM mechanism cohort now shows TTL2 creating
CPE-only state and TTL3 creating CPE-plus-CGNAT state, while an ordinary-TTL
control reaches the peer. Authenticated Birthday effect, router-mapping breadth,
and the wider research portfolio are tracked without product overclaim in
[`docs/TRAVERSAL_PORTFOLIO.md`](docs/TRAVERSAL_PORTFOLIO.md).

Read [the documentation map](docs/README.md) before using a dated report as
current authority. Exact production operation and non-claims live in
`docs/PRODUCTION_NODE_READINESS_HANDOFF.md`; current work lives in
`docs/ACTIVE_EXECUTION_PLAN.md` and `docs/NEXT_ACTIONS.md`.

## Production Binary

The GitHub executable is NATrav itself and carries this source and documentation:
```sh
chmod +x natrav-v0.52.0-x86_64-linux-<commit>
./natrav-v0.52.0-x86_64-linux-<commit> version
./natrav-v0.52.0-x86_64-linux-<commit> datacube project-summary
```
For a pinned local build, run `make doctor`, `make natrav-node-package-build`,
then `./result/bin/natrav-node version`. Operational details and the explicit
source-inspection namespace are in the
[self-carrying executable contract](docs/DATACUBE_DISTRIBUTION.md).

## Architecture

- `natkit-api` exposes consuming capabilities and the public session contract.
- `natkit-core` owns policy, authentication, planning, evidence, and
  deterministic conformance decisions.
- `natkit-net` owns concrete sockets, candidate custody, control carriers, and
  PCP/NAT-PMP leases.
- `natkit-ice` and `natkit-quic` own authenticated ICE and QUIC/Path Proof.
- `natkit-executor` owns attempt execution, lifecycle, fallback, and cleanup.
- `natkit-cli` provides development, proof, and operator command surfaces.
- `natkit-adversarial-if` contains explicitly enabled adversarial mechanisms.
- `natrav-node` is the product owner. Do not create another daemon or sender.
- `SPECS/` is normative; accepted decisions live under `docs/adr/`.

The product endpoint is NATrav-to-NATrav. External systems help build and
challenge NATrav; they are not intended product dependencies:

- Pion ICE and libnice are differential peers.
- Coturn and other TURN services are independently implemented infrastructure.
- Linux, OpenWrt, FreeBSD/PF, and appliance lanes are router subjects.
- NITE is an optional scenario compiler/render/golden lab.
- Sandwurm is the unattended development execution substrate.
- NATravOverlay is a peer sibling connected by the typed integration contract.

No external tool owns NATrav policy or certifies a product claim.

## Trust And Participation

NATrav begins in hope of cooperation and learns from plural evidence. Direct
behavior, authenticated continuity, capability conformance, temporal history,
peer and federated attestations, service to NATravOverlay, reputation,
redemption, and adversarial holdouts may all inform policy. No global score,
capability model, witness, human, or LLM judgment is sole authority.

Executing conforming NATrav software is consent to participate under the
published covenant. It is not consent on behalf of unrelated hosts.
Self-compilation is deliberate-participation evidence, not proof of honesty.
Authentication, packet authority, resource budgets, disclosure, and external
effects remain separate controls.

## Development

Bootstrap the supported environment:

```sh
make init
make bootstrap-rust
make install-hooks
make doctor
make dev-shell
make test-quick
```

Start a substantial human or LLM session with maintained context rather than
an old status document:

```sh
make llm-session-bootstrap
make test-llm-session-bootstrap
make context-pack
make session-plan
make test-session-plan
make workset-llm-bootstrap
make workset-implementation
make workset-quota-preserve
```

Read `AGENTS.md`, `docs/LLM_START_HERE.md`, and the relevant specs before
changing behavior. Keep paths repo-relative or run-relative.

## Validation

Use scoped checks while iterating:

```sh
make test-impact
make test-impact-contract
make test-rust-unit
make test-rust-integration
make test-rust-e2e
make test-rust-property
make test-determinism-smoke
make test-flake MODE=quick
make test-process-hygiene
make test-quick
```

For an ordinary behavior change, run one authoritative full surface:

```sh
make test
# Equivalent spelling: make test-full
```

At a merge or tranche handoff, use the gate instead. It already includes the
full surface, so do not run both on the same unchanged tree:

```sh
make test-run-gate
make test-verify-nix
make gate
```

Before a release or tag, run one strict rehearsal:

```sh
RELEASE_REHEARSAL_SBOM_STRICT=1 \
RELEASE_REHEARSAL_CLEAN_TREE_STRICT=1 \
make release-rehearsal VERSION=v0.52.0
```

Changes under `SPECS/` require `make update-specs-lock`; schema changes also
require `make sync-schemas`. Toolchain and build changes require
`scripts/verify_nix.sh`. See `docs/VALIDATION_EXECUTION_POLICY.md` for exact
precedence.

## Router And Scenario Evidence

Privileged labs are opt-in and capacity-gated:

```sh
make lab-host-doctor
make kvm-lab-prepare
make kvm-lab-start-safe
make kvm-lab-status
make kvm-linux-router-in-loop-proof
make openwrt-router-in-loop-proof
make freebsd-pf-router-in-loop-proof
make scenario-family-evidence-matrix
make scenario-traversal-science-campaign
make workset-scenario-router
make kvm-lab-stop
```

An accepted proof names exact binaries, topology, configuration, primary
transcripts or packet/conntrack evidence, cleanup, and bounded non-claims. A VM
boot, simulator render, packet capture, or aggregate green count alone is not
traversal proof.

## Repository Operations

Use managed process and storage controls:

```sh
make proc-list
make proc-stop-all
make storage-report
make storage-check
make clean-test-artifacts
make clean-build-cache
make git-hygiene
make test-git-hygiene
```

Generated build, VM, and evidence state dominates disk usage; tracked source is
small. Raw proof runs are ephemeral unless explicitly pinned. See
`docs/STORAGE_LIFECYCLE.md` before retaining snapshots.

End long sessions with an explicit handoff:

```sh
make llm-next-session-prep
make test-llm-next-session-prep
make workset-llm-next-session
```

Sandwurm starts through `make sandwurm-capability-probe` and
`make sandwurm-looper`; its receipts are development evidence, never product
state. NITE's retained boundary is exercised by `make test-nite-r0060-all`.
`docs/REPO_CONTROL.md` is the complete repository control model.

## Immediate Direction

Preserve the production v0.52 envelope while extending the traversal portfolio.
ADRs 0390-0395 accept the routed executor, matched low-TTL/Birthday outcomes, explicit/discovered MiniUPnPd mapping proof, and discovered-PCP route-loss retirement
plus fresh replacement establishment. The default product sequence
is a distinct mapping/router cohort, discovered NAT-PMP and advanced PCP, a
distinct hard-NAT allocator/filter cohort, Relay continuity,
and bounded multi-session extraction. Sentinel and Overlay evidence continue in
parallel. Do not rebuild features, owners, or governance merely for activity.
