# IoTox rev0051 repository manifest

The official development repository uses an ordinary source-tree checkout. Historical hidden
`.datacube/` handoffs remain documented under `docs/history/` and in `docs/foundation.md`; new
revisions use the verified repository-datacube package described by `PACKAGE.md`.

## Governing entrance

```text
BOOTSTRAPROSE.md
```

`BOOTSTRAPROSE.md` is the authoritative wake-from-amnesia entrance. It governs an ordinary repository
root containing the product source, tests, tools, active documents, retained evidence, and Git
history. Packaging creates a separate commit-addressed datacube and does not rearrange this checkout.

## Product source

```text
CMakeLists.txt
nix/patches/c-toxcore-0.2.23-tcp-connect-timeout-120.patch
CMakePresets.json
REVISION
include/iotox/
src/
cmake/
```

The public product is one C++20 executable named `iotox`. Internal static libraries are build
organization only.

Current product areas include:

```text
agent and one-binary CLI
typed complete command registry, generated help index, and Bash/Zsh/Fish command-name completion
private Unix SOCK_SEQPACKET local control
private ratox-style runtime tree and generalized hardened FIFO service
root outgoing-request record decoder
Tox adapter, one serialized owner thread, bootstrap/relay configuration, savedata
starvation-safe interactive/control/bulk owner scheduling and bounded iteration cadence
friend request/accept/reject/remove lifecycle keyed by public key
normal/action Tox text and read receipts
unadvertised confirmed-session lossless/lossy carrier diagnostics
bounded admission-aware custom-packet impairment bursts
content-free auxiliary carrier/local-boundary/confirmed-peer route health without epoch mutation
canonical Ratox v1 framing, admission pacer, pure R1 host session engine, and default-off R4 coordinator
pure R5 Ratox controller, finite-admission private terminal protocol/socket, and one-binary terminal CLI
IoTox frame/session negotiation
stable device identity and RecallRoot-derived owner principal
signed v1/v2 authorization ledger and transcript-bound authority proof
durable command codec/store/executor and device.describe
finite Tox file send/receive/control and safe local publication
default-off signed release verification, release-signer operations, recoverable slot quarantine, health-gated rollback, and sealed Linux service deployment
native route model, strict construction-enabled Tox/Tor SOCKS policy, and fail-closed I2P reservation
canonical terminal profile v7 with frozen non-root account groups, explicit default-denied elevation,
exact optional shell/rescue payload SHA-256 pins,
profile-scoped process/memory/swap/CPU and exact-device I/O
budgets, exact aggregate process/memory/swap/CPU reservation admission, host-local PSI hysteresis plus continuous trigger-tripwire admission, retained kernel session outcomes, capability floor, argument-fenced tiered Linux confinement, procfd-pinned/
pidfd-signaled fallback supervision, optional boot-bound delegated-cgroup kill/quiescence/orphan
recovery, and a sealed process boundary reachable only through the explicit host gate
owner-private same-user terminal controller stream reachable only through its independent Agent gate
stable-device-signed bounded content-free flight recorder and identity-free inspected support bundle
stable-device-signed one-to-one human peer aliases and shared unambiguous selector grammar
forward-only retained tree-v2 history/diff/conflict/restore planning and higher-generation recovery
recipient-local tree-v2 sparse custody, selected-object transfer, policy-safe widening, and partial repair/GC truth
tree-v2 primary-frontier exact-probe availability and complementary primary-lane object recovery
optional fail-closed fscrypt-v2 complete-state closure before runtime creation and an authenticated
authority/application/Ratox/route-generation/terminal-policy/command-effect/sync-policy/
update-lifecycle/per-namespace-four-root/tree-v2-semantic-state exact-CAS rollback-witness
coordinator/service with durable
signed intents or guards, dedicated witness identity, separate device-signed enrollment,
complete-store signed checkpoint floors, and pre-runtime fail-closed reconciliation
path-free diagnostics configuration commitment v9 binding protected-state and authority plus
application/Ratox incarnation/route-generation/terminal-policy/command-effect/sync-policy/
update-lifecycle/sync-guarded-state witness presence
separate optional static x86_64/AArch64 oksh/Toybox rescue deployment payload, validated SPDX
records, qemu-user/binfmt evidence, x86_64 production-PTY VM gate, and AArch64-kernel system-emulation gate
```

The rev0051 freshness-explicit projection-recovery boundary is centered in:

```text
include/iotox/sync_multiwriter.hpp
include/iotox/sync_multiwriter_maintenance.hpp
include/iotox/sync_multiwriter_reconcile.hpp
include/iotox/sync_multiwriter_store.hpp
include/iotox/sync_multiwriter_subscriber.hpp
include/iotox/sync_multiwriter_worktree.hpp
src/sync_multiwriter.cpp
src/sync_multiwriter_maintenance.cpp
src/sync_multiwriter_reconcile.cpp
src/sync_multiwriter_service.cpp
src/sync_multiwriter_store.cpp
src/sync_multiwriter_workspace.cpp
src/sync_multiwriter_subscriber.cpp
src/sync_multiwriter_worktree.cpp
src/agent.cpp
src/cli.cpp
src/local/control_protocol.cpp
src/protocol/session.cpp
tests/test_sync_multiwriter_maintenance.cpp
tests/test_sync_multiwriter_reconcile.cpp
tests/test_sync_multiwriter_service.cpp
tests/test_sync_multiwriter_store.cpp
tests/test_sync_multiwriter_workspace.cpp
tests/test_sync_multiwriter_worktree.cpp
docs/decisions/0334-make-object-pipeline-recovery-durable.md
docs/decisions/0335-qualify-tree-v2-branch-publication-prefixes.md
docs/decisions/0336-cut-post-rename-directory-durability-windows.md
docs/decisions/0337-refuse-corrupt-tree-v2-metadata-until-exact-restoration.md
docs/decisions/0338-preserve-bounded-exchanged-projection-descriptor-writes.md
docs/decisions/0339-make-metadata-freshness-and-co-resident-corruption-explicit.md
docs/decisions/0340-qualify-exchanged-projection-open-descriptor-retention.md
docs/evidence/2026-09-08-sync-tree-v2-co-resident-metadata-corruption.md
docs/evidence/2026-09-08-sync-whole-vmm-object-pipeline-power-cut.md
docs/evidence/2026-09-08-sync-whole-vmm-branch-publication-power-cut.md
docs/evidence/2026-09-08-sync-whole-vmm-directory-durability-power-cut.md
docs/evidence/2026-09-08-sync-tree-v2-metadata-corruption.md
tests/test_agent.cpp
tests/test_local_control_protocol.cpp
tests/test_session.cpp
tools/run-sync-three-writer.py
tools/run-sync-storage-fault-rehearsal.py
tools/verify-sync-three-writer-sandwurm.py
tools/export-sync-three-writer-sandwurm.py
tools/run-sync-power-cut-rehearsal.py
tools/run-sync-power-cut-sandwurm.py
tools/verify-sync-power-cut-sandwurm.py
tools/export-sync-power-cut-sandwurm.py
tools/run-sync-metadata-corruption-rehearsal.py
tools/verify-sync-metadata-corruption-sandwurm.py
tools/export-sync-metadata-corruption-sandwurm.py
tools/iotox-sandwurm-lab.sh
tools/clean-workspace.py
nix/iotox-sandwurm-three-writer.nix
nix/iotox-sandwurm-sync-power-cut.nix
nix/iotox-sandwurm-sync-metadata-corruption.nix
flake.nix
docs/protocol-sync-tree-v2.md
docs/decisions/0275-bound-tree-v2-history-and-retire-writers.md
docs/decisions/0330-batch-tree-v2-file-object-commits.md
docs/decisions/0331-effect-fence-cached-tree-v2-cas-inventory.md
docs/decisions/0332-qualify-one-whole-vmm-tree-v2-workspace-cut.md
docs/decisions/0333-target-both-workspace-exchange-sides.md
docs/everyday-sync-plan.md
docs/evidence/2026-09-01-sandwurm-sync-three-writer-lifecycle.md
include/iotox/sync_service.hpp
include/iotox/sync_content_service.hpp
src/sync_service.cpp
src/sync_content_service.cpp
tests/test_sync_service.cpp
tests/test_sync_content_service.cpp
tools/run-sync-shadow.py
tools/verify-sync-shadow-sandwurm.py
tools/export-sync-shadow-sandwurm.py
tools/qualify-route-policy-campaign.py
nix/iotox-sandwurm-sync-shadow.nix
docs/decisions/0276-qualify-unattended-one-writer-sync.md
docs/decisions/0277-freeze-founding-machine-completion-scope.md
docs/decisions/0278-freeze-selective-tree-v2-projection-and-owner-mode.md
docs/decisions/0279-close-the-founding-route-policy-campaign.md
docs/decisions/0280-extend-tree-v2-manifest-identity-to-its-quota.md
docs/decisions/0281-close-the-bounded-tree-v2-adversarial-gate.md
docs/decisions/0282-roll-sync-read-replay-as-a-bounded-window.md
docs/decisions/0283-accept-the-founding-sync-shadow-and-close-the-roadmap.md
docs/decisions/0284-separate-sync-confidence-from-backup-trust.md
docs/evidence/2026-09-01-route-policy-campaign.md
docs/evidence/2026-09-01-sandwurm-sync-automation.md
docs/evidence/2026-09-01-sync-adversarial-scale.md
docs/evidence/2026-09-01-sandwurm-iotox-resilio-shadow.md
docs/sync-trust-graduation.md
nix/ratox-rescue-toolbox-test.nix
nix/ratox-cgroup-test.nix
nix/ratox-rescue-toolbox-aarch64-test.nix
nix/ratox-rescue-toolbox-aarch64-system-test.nix
nix/protected-state-test.nix
nix/rollback-witness-service-test.nix
nix/oksh-no-curses.patch
docs/decisions/0285-add-owner-local-ratox-operations.md
docs/decisions/0286-make-owner-shells-real-login-accounts-with-explicit-sudo.md
docs/decisions/0287-ship-an-explicit-static-rescue-toolbox.md
docs/ratox-rescue-toolbox.md
include/iotox/sync_doctor.hpp
src/sync_doctor.cpp
tests/test_sync_doctor.cpp
docs/decisions/0288-add-read-only-sync-doctor-preflight.md
docs/sync-doctor.md
docs/decisions/0289-add-exact-session-ratox-reconnect.md
include/iotox/agent_config.hpp
include/iotox/agent_preflight.hpp
src/agent_config.cpp
src/agent_preflight.cpp
tests/test_agent_config.cpp
docs/decisions/0290-add-canonical-agent-configuration-and-preflight.md
docs/agent-configuration.md
include/iotox/diagnostics.hpp
src/diagnostics.cpp
tests/test_diagnostics.cpp
docs/decisions/0291-add-authenticated-content-free-diagnostics.md
docs/diagnostics.md
include/iotox/peer_alias.hpp
src/peer_alias.cpp
tests/test_peer_alias.cpp
docs/decisions/0292-add-durable-human-peer-aliases.md
docs/peer-aliases.md
include/iotox/peer_invitation.hpp
src/peer_invitation.cpp
tests/test_peer_invitation.cpp
docs/decisions/0293-add-explicit-signed-peer-invitations.md
docs/peer-invitations.md
include/iotox/sync_time_machine.hpp
src/sync_time_machine.cpp
tests/test_sync_time_machine.cpp
docs/decisions/0294-add-forward-only-sync-time-machine.md
docs/sync-time-machine.md
docs/decisions/0295-add-tree-v2-sparse-custody.md
docs/sync-sparse-custody.md
docs/decisions/0296-add-tree-v2-exact-probe-multi-source.md
include/iotox/sync_health.hpp
src/sync_health.cpp
tests/test_sync_health.cpp
docs/decisions/0297-add-signed-tree-v2-namespace-health.md
docs/sync-health.md
docs/decisions/0298-join-namespace-health-to-diagnostics.md
docs/decisions/0299-add-normalized-host-capability-diagnostics.md
docs/decisions/0300-qualify-production-ratox-reconnect.md
docs/decisions/0301-reproduce-aarch64-rescue-and-pin-payloads.md
docs/decisions/0302-freeze-protected-state-and-witness-boundary.md
include/iotox/protected_state.hpp
include/iotox/policy_witness.hpp
include/iotox/rollback_witness.hpp
include/iotox/rollback_witness_service.hpp
include/iotox/sync_policy_witness.hpp
include/iotox/sync_guarded_witness.hpp
include/iotox/sync_tree_v2_witness.hpp
src/policy_witness.cpp
src/protected_state.cpp
src/rollback_witness.cpp
src/rollback_witness_service.cpp
src/sync_policy_witness.cpp
src/sync_guarded_witness.cpp
src/sync_tree_v2_witness.cpp
src/update_witness.cpp
tests/test_protected_state.cpp
tests/test_policy_witness.cpp
tests/test_rollback_witness.cpp
tests/test_rollback_witness_service.cpp
tests/test_sync_guarded_witness.cpp
tests/test_sync_tree_v2_witness.cpp
docs/decisions/0303-enforce-fscrypt-state-and-pilot-authority-witness.md
docs/decisions/0304-qualify-aarch64-rescue-through-arm-kernel.md
docs/decisions/0305-deploy-authenticated-authority-witness-service.md
docs/decisions/0306-witness-application-and-ratox-incarnations.md
docs/decisions/0307-witness-route-generation-policy.md
docs/decisions/0308-witness-terminal-policy-tree.md
docs/decisions/0309-witness-command-effect-frontier.md
docs/decisions/0310-witness-complete-sync-policy-tree.md
docs/decisions/0311-witness-update-policy-and-lifecycle.md
docs/decisions/0312-witness-per-namespace-sync-four-root-state.md
docs/decisions/0313-add-complete-witness-service-checkpoint-floors.md
docs/decisions/0314-witness-tree-v2-semantic-state.md
docs/decisions/0315-join-sync-doctor-to-live-managed-headroom.md
docs/decisions/0316-qualify-repeated-production-ratox-reconnect.md
include/iotox/cli_registry.hpp
src/cli_registry.cpp
docs/decisions/0317-add-typed-cli-registry-and-completion.md
docs/cli-completion.md
docs/decisions/0318-enforce-sync-doctor-filesystem-contract.md
include/iotox/sync_recovery_verify.hpp
src/sync_recovery_verify.cpp
tests/test_sync_recovery_verify.cpp
docs/decisions/0319-verify-independent-sync-restore-drills.md
docs/sync-recovery-rehearsal.md
docs/evidence/2026-09-03-sync-recovery-verify.md
docs/evidence/2026-09-03-sync-capacity-controls.md
docs/decisions/0320-measure-persistent-three-writer-capacity.md
docs/decisions/0321-batch-tree-v2-projection-durability.md
docs/decisions/0322-recover-live-writes-across-tree-exchange.md
docs/evidence/2026-09-03-sandwurm-sync-persistent-capacity.md
docs/decisions/0323-automate-tree-v2-node-loss-recovery.md
docs/evidence/2026-09-03-sync-node-loss-recovery.md
docs/decisions/0324-supersede-unfinished-authority-rounds.md
docs/evidence/2026-09-03-authority-round-supersession.md
docs/decisions/0325-exercise-bounded-sync-storage-faults.md
docs/evidence/2026-09-03-sync-storage-fault-recovery.md
docs/decisions/0326-qualify-ratox-password-sudo-through-pty.md
docs/evidence/2026-09-03-ratox-password-sudo.md
docs/decisions/0327-qualify-ratox-cgroup-under-nixos-systemd.md
docs/evidence/2026-09-03-ratox-cgroup-kernel-qualification.md
docs/decisions/0328-fence-open-descriptor-sync-source-mutation.md
docs/evidence/2026-09-03-sync-open-descriptor-source-mutation.md
docs/evidence/2026-09-03-sync-near-ceiling-timeout.md
docs/evidence/2026-09-04-sync-cas-inventory.md
docs/evidence/2026-09-04-sync-whole-vmm-power-cut.md
docs/evidence/2026-09-04-sync-whole-vmm-post-exchange-power-cut.md
docs/decisions/0329-pipeline-tree-v2-exact-object-lanes.md
tools/run-sync-recovery-rehearsal.py
docs/protected-local-state.md
docs/protocol-witness-service-checkpoint-v1.md
docs/evidence/2026-09-02-protected-state-authority-witness.md
docs/evidence/2026-09-02-remote-authority-witness-service.md
docs/evidence/2026-09-02-incarnation-rollback-witness.md
docs/evidence/2026-09-02-route-generation-rollback-witness.md
docs/evidence/2026-09-02-terminal-policy-rollback-witness.md
docs/evidence/2026-09-02-command-effect-rollback-witness.md
docs/evidence/2026-09-02-sync-policy-rollback-witness.md
docs/evidence/2026-09-02-update-lifecycle-rollback-witness.md
docs/evidence/2026-09-03-configured-sync-headroom.md
docs/evidence/2026-09-02-sync-guarded-state-rollback-witness.md
docs/evidence/2026-09-02-witness-service-checkpoint-floor.md
docs/evidence/2026-09-02-tree-v2-state-rollback-witness.md
```

Format-2 checkpoints explicitly negotiate feature bit 31 and bound authenticated predecessor walks
without changing ordinary format-1 bytes. Exact pins and signed workspace roots feed a graph-aware
collector that supports dry-run, no-replace quarantine, and authenticated restore but no purge.
Terminal per-writer cutoffs freeze an exact final record independently on every survivor; they do
not replace general authority revocation. Quiet observation retains a derived manifest beneath the
signed workspace journal instead of creating acknowledgement-only branches.

ADRs 0277--0283 define and close the founding-machine completion boundary. Canonical recipient-local
selection and owner-mode metadata, a finite named adversarial/scale matrix, a populated route-policy
campaign, and a two-hour networkless IoTox/Resilio shadow now pass. Synchronization publisher reads
use bounded rolling exact-replay windows so a long-lived authorized peer cannot exhaust a finite
lifetime table. Six hosted/independent/physical/public-history gates remain permanently struck, and
the retained evidence continues to identify same-machine Sandwurm limitations explicitly.

The retained rev0044 signed-update construction boundary is centered in:

```text
include/iotox/update_bundle.hpp
include/iotox/update_state.hpp
include/iotox/update_witness.hpp
include/iotox/update_service.hpp
src/update_bundle.cpp
src/update_state.cpp
src/update_witness.cpp
src/update_service.cpp
include/iotox/protocol/command.hpp
src/protocol/command.cpp
src/command_engine.cpp
src/command_store.cpp
src/agent.cpp
tests/test_update_bundle.cpp
tests/test_update_state.cpp
tests/test_update_witness.cpp
tests/test_update_service.cpp
tests/update_service_fixture.cpp
tests/test_command.cpp
tests/test_command_store.cpp
tests/test_agent.cpp
tests/fuzz_update_bundle.cpp
tests/corpus/update/
docs/protocol-signed-update-bundle-v1.md
docs/protocol-command-v1.md
docs/decisions/0184-separate-update-intent-from-sync-delivery.md
docs/decisions/0185-qualify-the-signed-update-slot-lifecycle.md
docs/decisions/0186-authorize-remote-update-staging-through-durable-commands.md
docs/decisions/0187-freeze-release-signer-revocation-policy.md
docs/decisions/0188-operate-release-keys-and-quarantine-update-slots.md
docs/decisions/0189-freeze-linux-service-deployment-adapter.md
docs/update-operations.md
docs/update-linux-service-v1.md
docs/evidence/2026-08-26-sandwurm-signed-update.md
docs/evidence/2026-08-26-sandwurm-remote-update-stage.md
docs/evidence/2026-08-27-sandwurm-linux-service-update.md
docs/evidence/2026-08-27-source-linked-tox-tor-route.md
docs/evidence/2026-08-27-sandwurm-tox-tor-route.md
artifacts/rev0045/tox-tor-smoke.json
artifacts/rev0045/actual-tor-path-population.json
artifacts/rev0045/SHA256SUMS
```

Sync delivery remains independent of release intent. Feature bit 20 and remote `update.stage` exist
only after local construction and exact `install.firmware` admission; apply/restart/confirm remain
owner-local. Opaque policy v1/v2 slots remain inert. Policy v3 and manifest/state kind 2 admit only
the separately gated sealed `linux-service-v1` adapter. Update policy v2
adds a local signer-policy epoch plus bounded revoked release keys for future-staging denial without
changing the signed bundle manifest. Release signer creation is explicit and no-clobber; policy
rotation emits a new reviewable epoch. Historical inactive slots may move only to bounded
owner-private recoverable quarantine, and no purge operation exists.

The rev0045 strict routed-privacy construction boundary is centered in:

```text
include/iotox/network.hpp
include/iotox/route_health.hpp
include/iotox/transport.hpp
include/iotox/route_binding.hpp
include/iotox/route_inventory.hpp
include/iotox/route_worker.hpp
include/iotox/local/runtime_tree.hpp
src/network.cpp
src/route_health.cpp
src/route_binding.cpp
src/route_inventory.cpp
src/route_store.cpp
src/route_worker.cpp
src/agent.cpp
src/protocol/frame.cpp
src/protocol/session.cpp
src/toxcore/transport.cpp
src/local/runtime_tree.cpp
src/cli.cpp
tests/test_network.cpp
tests/test_toxcore_transport.cpp
tests/test_runtime_tree.cpp
tests/test_route_binding.cpp
tests/test_route_worker.cpp
tests/test_agent.cpp
tests/test_protocol.cpp
tests/test_session.cpp
tests/test_socks5_forwarder.py
tests/test_socks5_adversary.py
tests/test_i2p_sam_socks.py
tests/test_i2p_sam_forward.py
tests/test_route_target_process.py
tools/run-socks5-forwarder.py
tools/run-socks5-adversary.py
tools/run-i2p-sam-socks.py
tools/run-i2p-sam-forward.py
tools/run-i2p-sam-smoke.py
tools/run-i2p-tox-fronts.py
tools/verify-i2p-sam-smoke.py
tools/run-tox-tor-smoke.py
tools/run-tox-operator-tor-smoke.py
tools/verify-tox-operator-tor-smoke.py
tools/run-sandwurm-pair.py
tools/verify-sandwurm-pair.py
tools/export-sandwurm-pair.py
tools/analyze-ratox-route-impairment.py
tools/analyze-ratox-route-loss.py
tools/ratox-cli-reconnect-probe.py
tools/analyze-actual-tor-path-population.py
docs/networks.md
docs/decisions/0190-freeze-strict-tox-tor-route.md
docs/decisions/0191-qualify-operator-tor-public-route.md
docs/decisions/0192-separate-auxiliary-route-health.md
docs/decisions/0193-bound-persistent-route-and-ratox-heartbeats.md
docs/decisions/0194-probe-only-the-configured-socks-target.md
docs/decisions/0195-bind-the-configured-target-to-tor-control.md
docs/decisions/0196-qualify-ratox-under-bounded-route-impairment.md
docs/decisions/0197-freeze-ratox-total-loss-recovery.md
docs/decisions/0198-separate-route-identities-and-private-inventory.md
docs/decisions/0199-split-private-route-inventory-from-member-proof.md
docs/decisions/0200-gate-private-workers-on-primary-inventory.md
docs/decisions/0201-qualify-private-routes-across-network-contexts.md
docs/decisions/0202-bind-workers-to-independent-rendezvous-catalogs.md
docs/decisions/0203-qualify-two-independent-tor-route-workers.md
docs/decisions/0204-attribute-sync-payload-to-an-actual-tor-member.md
docs/decisions/0205-count-real-carrier-recovery-and-fault-the-tor-process.md
docs/decisions/0206-qualify-ratox-across-actual-tor-process-loss.md
docs/decisions/0207-qualify-ratox-duration-across-actual-tor-circuit-churn.md
docs/decisions/0208-repeat-ratox-churn-across-a-distinct-relay-record.md
docs/decisions/0209-construct-an-adversarial-local-tor-boundary.md
docs/decisions/0210-account-for-actual-tor-path-populations.md
docs/decisions/0211-construct-strict-i2p-sam-boundary.md
docs/decisions/0212-qualify-actual-i2p-sam-streams.md
docs/decisions/0213-freeze-the-i2p-tox-service-construction.md
docs/decisions/0214-budget-slow-overlay-tcp-establishment.md
docs/decisions/0215-preserve-tox-node-addresses-across-i2p-fronts.md
docs/decisions/0216-qualify-the-sandwurm-i2p-baseline.md
docs/decisions/0217-qualify-i2p-router-loss-and-recovery.md
docs/decisions/0218-qualify-i2p-service-front-replacement.md
docs/decisions/0219-qualify-bounded-i2p-sync-payload.md
docs/decisions/0220-add-fail-closed-sync-route-policy.md
docs/decisions/0221-freeze-failover-intent-per-sync-pull.md
docs/decisions/0222-pin-sync-pulls-to-a-constructed-route-class.md
docs/i2p-route-construction.md
docs/protocol-private-route-binding-v2.md
docs/evidence/2026-08-27-operator-tor-public-route.md
docs/evidence/2026-08-27-sandwurm-ratox-route-impairment.md
docs/evidence/2026-08-27-sandwurm-ratox-route-loss.md
docs/evidence/2026-09-02-sandwurm-ratox-cli-reconnect.md
docs/evidence/2026-09-03-sandwurm-ratox-cli-reconnect-repeated.md
docs/evidence/2026-09-02-aarch64-rescue-capsule.md
docs/evidence/2026-08-27-sandwurm-actual-tor-ratox-loss.md
docs/evidence/2026-08-28-sandwurm-actual-tor-ratox-churn.md
docs/evidence/2026-08-28-sandwurm-actual-tor-adversarial-boundary.md
docs/evidence/2026-08-28-actual-tor-path-population.md
docs/evidence/2026-08-28-actual-i2p-sam-streams.md
docs/evidence/2026-08-28-actual-i2p-real-peer-e2e.md
docs/evidence/2026-08-28-sandwurm-actual-i2p-baseline.md
docs/evidence/2026-08-28-sandwurm-i2p-router-recovery.md
docs/evidence/2026-08-28-sandwurm-i2p-service-front-recovery.md
docs/evidence/2026-08-28-sandwurm-actual-i2p-private-sync-payload.md
docs/evidence/2026-08-27-sandwurm-private-route-mixed-context.md
docs/evidence/2026-08-27-sandwurm-two-peer-actual-tor.md
docs/evidence/2026-08-27-sandwurm-actual-tor-payload.md
docs/evidence/2026-08-27-sandwurm-actual-tor-process-loss.md
artifacts/rev0045/tox-operator-tor-smoke.json
artifacts/rev0045/actual-tor-path-population.json
artifacts/rev0045/i2p-sam-two-router-smoke.json
```

It construction-enables explicit Tox/Tor with numeric SOCKS, bootstrap, and relay records; disables
native DNS and every UDP discovery seam; injects no native defaults; and has no native fallback.
The source-linked local gate proves exact socket containment plus proxy-loss/recovery but explicitly
does not claim that the laboratory SOCKS implementation is Tor. Its retained clean-source receipt
binds the exact product/fixture/tool hashes and measures 8.038-second initial TCP, 77.993-second
provider loss detection, and 4.921-second exact-endpoint recovery.
The distinct two-guest `tox-tor proxy-restart` gate binds both TAP captures, proxy audits,
source-linked peer receipts, proxy loss/recovery, and fresh application traffic. Its accepted compact
proof is `pair.zyy913jf`; the laboratory boundary remains explicitly non-Tor.
ADR 0201 adds exact-key local worker network contexts and race-safe private-context adoption. The
two-guest `sync-tree-route-private-mixed` cell joins one native primary, one native bulk member, and
one strict generic-SOCKS bulk member per role under independent route keys. Accepted compact proof
`pair.z948jeii` records two ready bulk routes per role, exact signed 4,194,389-byte tree convergence,
four admitted/zero denied proxy connections, native UDP plus proxied TCP on both TAPs, and no TCP
outside the configured host-local endpoints. This closes generic-SOCKS mixed-context operation, not
actual-Tor two-peer behavior or anonymity.
The independent operator-Tor gate binds Tor 0.4.8.11 and its exact normalized configuration, joins
initial and recovered configured-target streams from new Agent source ports to distinct three-hop
`CONFLUX_LINKED` application circuits, proves
IoTox owns only loopback SOCKS TCP and no UDP/direct route, and holds an offline no-bypass window
between Tor death and restart. Its ADR 0192 companion observes local refusal in 35 ms while the
authoritative carrier remains TCP, then independently observes offline after 74.602 seconds. This
is a single-host/relay/time route claim, not anonymity or automatic recovery policy. Accepted
compact proof `pair.2mycvy9n` separately binds two exact Tor auxiliaries to distinct three-hop
circuits and private-v2 readiness inside one converged sync topology. Accepted compact proof
`pair.lzsyitvy` additionally binds the complete signed-tree job to the exact Tor member with zero
reassignment and strict Tor/control plus TAP containment. Accepted compact proof `pair.iompvehf`
then externally kills that Tor process after positive object progress and binds one loss, native
reassignment, real carrier return, zero IoTox worker restarts, and zero unexpected-context TAP
packets. Accepted compact proof `pair.2waqdpgk` separately binds primary client Tor process loss to
heartbeat-before-offline behavior, one detached live PTY, and explicit exact-session generation-2
resume with zero IoTox daemon restarts and TCP-only TAP containment. These are bounded route
samples, not anonymity, physical path independence, or
long-duration/multi-relay reliability.
ADR 0193 adds strict canonical report parsing, independent process-local persistent route latches,
and one exact Ratox PING identity per attachment. The terminal warns after three one-second misses
without changing carrier or session state; deterministic Agent/controller evidence crosses remote
PING/PONG, route loss, exact resume, and post-resume PONG. It is not impaired-route or PTY-progress
evidence.
ADR 0194 adds explicit one-shot SOCKS5 negotiation and CONNECT only to the first numeric relay in the
validated route. Whole-binary evidence separates target success, target refusal, and proxy refusal
while carrier truth remains TCP; no endpoint enters the command or content-free report.
ADR 0195 binds initial/recovered successes to authenticated Tor control, exact stream lifecycles,
new Agent source ports, configured relay zero, and qualifying linked-Conflux circuits without
putting Tor credentials into the ordinary Agent.
ADR 0196 adds an independently analyzed two-guest Ratox impairment matrix. Direct UDP, forced TCP,
and strict generic SOCKS each keep one session across 20 baseline, 80 seeded-delay/loss, and 20
recovered heartbeat-plus-PTY observations. Carrier presence, heartbeat, PTY progress, and visible
stall remain distinct; bounded partial impairment warns without mutating the attachment. The SOCKS
cell is not an actual-Tor claim; total-loss retention/resume was the next policy gate at that
boundary.
ADR 0197 closes that native/strict-SOCKS gate with three independently verified 100%-loss cells.
A heartbeat miss warns while the route remains confirmed; authoritative offline returns typed
`unavailable` locally and leaves one detached live PTY remotely. A higher authenticated epoch then
permits explicit exact-session generation-two resume with preserved incarnation and byte positions.
Automatic migration remains unclaimed. ADR 0206 constructs a distinct actual-Tor terminal
process-loss/explicit-resume gate. Accepted compact proof `pair.2waqdpgk` binds a real client Tor
`SIGKILL`, warning-before-offline semantics, one detached live PTY, exact-session generation-2
resume, three authenticated Tor phases, zero IoTox daemon restarts, and TCP-only TAP containment.
ADR 0207 accepts compact proof `pair.k8o54n2v` for a distinct 120-sample continuous-process cell:
exact client/device Tor circuits are closed and replaced while Tor and IoTox stay alive. Live science observed both a carrier-loss
attempt and a no-error attempt. The final contract sends post-replacement PING and accepts only
same-epoch/generation PONG continuity or exact `unavailable` plus higher-epoch explicit resume, with
one preserved session/incarnation/PTY and contiguous byte positions. The accepted run exercises both
branches with exact Tor inventory/event joins, unchanged processes, and TCP-only TAP containment.
ADR 0208 repeats the unchanged gate through a distinct public Tox record as compact proof
`pair.9cx0jels`. Both Tor streams reopen while both Ratox checkpoints remain same-epoch/generation
continuous, proving that a Tor transition label cannot predict or authorize a session transition.
The two sequential samples still do not establish exit/time diversity, availability, or anonymity.
ADR 0209 accepts compact proof `pair.vx6z0csh` for the live interposer cell. A reachable listener
and fresh exact-target SOCKS CONNECT remain positive while established relay bytes are withheld;
Ratox warning precedes c-toxcore authoritative offline, the device retains one detached PTY, and
removing only the hold file permits exact generation-2 resume without Tor/interposer/IoTox restart.
Every interposer chain is joined to authenticated Tor control and TCP-only TAP containment.
ADR 0210 adds deterministic corpus accounting rather than another live route claim. The analyzer
strictly reverifies all seven compact actual-Tor roots and resolves 24 exact-target/churn path
declarations to 20 normalized three-hop paths, 17 first hops, and 19 last hops. It emits only
content-free counts and set commitments. Zero cross-proof complete-path/last-hop reuse is observed,
but independent exit/operator review and separated time windows remain unqualified.
ADR 0211 begins the still-reserved I2P route with a lab-only strict numeric SOCKS-to-SAM v3.1
adapter. Exact b32 mapping, one transient session, eight simultaneous streams, admission withdrawal,
higher-generation recovery, and destination-redacted audit pass an independent process double.
ADR 0212 then sends one warm-up plus four barrier-released, byte-verified STREAM connections through
two distinct live i2pd 2.60.0 processes on the founding host. This is actual I2P stream-seam
evidence, not Tox-over-I2P, Sandwurm packet containment, anonymity, or product enablement.
ADRs 0216–0219 extend that seam through two source-linked Sandwurm guests: a contained baseline,
exact client-router replacement, and exact three-front replacement over unchanged private
Destination keys all reach transcript-confirmed bilateral application truth. Router PIDs are joined
to owned SAM listeners and established public TCP remote-set commitments. The fourth proof assigns
one exact 131,369-byte signed tree to an authenticated actual-I2P member with zero reassignment while
native fallback remains ready. Product `tox/i2p`, large privacy-pinned payload behavior, anonymity,
and availability claims remain excluded.

ADRs 0225–0229 add the explicit privacy-policy boundary above that construction. Route-set v2 signs
each member's native/Tor/construction-I2P class; per-job class pins and fail-closed policy cannot
silently select native. The frozen range-v1 frames now carry a bounded changed region through an
exact authenticated auxiliary when both primary and worker negotiate the feature. Accepted compact
proof `pair.a9zwongf` additionally faults a live 1 MiB I2P range after 86,373 bytes, proves strict
partial cleanup and zero downgrade, recovers the same member without worker restart, and permits
only an explicit distinct job to fetch a fresh complete range, reuse 3 MiB of verified basis, and
activate the exact 4 MiB target. This qualifies safe fresh recovery, not I2P carrier-loss prefix
resume; production `tox/i2p`, anonymity, independent paths, availability, and performance remain
excluded.
ADR 0229 and compact proof `pair.ip5q0at9` reverify and reuse the exact 786,496-byte durable manifest
on the distinct recovery job. Only one 1 MiB range is transport-requested while both immutable
objects commit, removing 42.86% of that recovery phase's object bytes without reusing the failed
71,292-byte prefix or changing peer framing.

ADR 0230 separately optimizes the ordinary bounded same-carrier range retry. The first byte now lands
in an exact attempt-owned resumable inode; after an incomplete terminal, fresh signed attempt and
FileId identities may inherit only a strictly revalidated prefix and seek before suffix receive.
Compact proofs `pair.cj5y5vgt` and `pair.qeb99i4o` retain/resume 15,081 direct-UDP bytes and 24,678
forced-TCP bytes with zero discard/fallback while preserving complete reconstruction, HEAD-last
acceptance, and explicit activation. This does not change ADR 0228's I2P carrier-loss cleanup.

ADR 0231 applies that exact-prefix primitive to native `available` carrier loss. The old range
attempt, FileId, and transport truth are fenced before a distinct authenticated range-capable
carrier receives the unchanged plan under fresh identities. Compact proofs `pair.urbhf0je` and
`pair.n76biwao` retain/resume 283,797 UDP and 293,394 TCP bytes exactly with zero discard/fallback
and full final verification. Fail-closed I2P, restart continuation, and multi-source striping remain
excluded. Deterministic coverage now repeats the boundary through three distinct carriers: a 50%
prefix grows to 75% between losses and reaches a third fresh attempt without consuming the ordinary
range-retry budget. ADR 0232 and compact proofs `pair.le38qcl5`/`pair.8u14ddcy` close the genuine
two-loss native row: cumulative exact prefixes of 542,916 UDP or 564,852 TCP bytes survive two
sequential carrier deaths under three fresh attempts, with two stale-terminal fences and recoveries,
zero discard/fallback, full reconstruction, HEAD-last acceptance, and explicit activation. The
bounded request hold that orders recovery before refault is qualification-only. ADR 0233 then closes
one 15/16 late-loss row: compact `pair.tev4u3rs` preserves 984,378 UDP bytes and `pair.1z7_d0jn`
preserves 995,346 TCP bytes, with one exact reassignment/recovery and zero discard/fallback before
full verification/activation. Repeated-late/final-chunk races, three-plus loss, restart continuation,
and multi-source striping remain open.

The rev0039 Ratox host, controller, local-IPC, confinement, supervision, recovery, resource-policy,
aggregate/PSI admission, kernel-outcome observability, and attested evidence construction is centered in:

```text
include/iotox/terminal_profile.hpp
include/iotox/terminal_seccomp_policy.hpp
include/iotox/terminal_cgroup.hpp
include/iotox/security/process_hardening.hpp
src/terminal_profile.cpp
src/terminal_cgroup.cpp
src/terminal_posix.cpp
src/security/process_hardening.cpp
include/iotox/interactive_service.hpp
src/interactive_service.cpp
include/iotox/latency_histogram.hpp
src/latency_histogram.cpp
include/iotox/retained_send_telemetry.hpp
src/retained_send_telemetry.cpp
include/iotox/interactive_incarnation.hpp
src/interactive_incarnation.cpp
include/iotox/interactive_client.hpp
src/interactive_client.cpp
include/iotox/local/terminal_protocol.hpp
src/local/terminal_protocol.cpp
src/local/seqpacket_security.hpp
src/local/seqpacket_security.cpp
include/iotox/local/control_socket.hpp
src/local/control_socket.cpp
include/iotox/local/terminal_socket.hpp
src/local/terminal_socket.cpp
include/iotox/terminal_cli.hpp
src/terminal_cli.cpp
src/agent.cpp
tests/test_terminal_cgroup_recovery_process.cpp
tools/ratox_r7_evidence.py
tools/prepare-ratox-r7.py
tools/analyze-ratox-r7.py
```

The host advertises feature bit 23 only after pre-network activation validation and dispatches packet
`0xA2` only through the current transcript/epoch/principal/exact-head authority gate. The independent
controller gate publishes one owner-private same-user `SOCK_SEQPACKET` stream, binds it to the exact
live peer/principal route, retains bounded immutable input/output/retry state, and exposes one-binary
OPEN/RESUME operation. rev0020 adds a finite first-OPEN lease, a bounded consume-and-deny contention
handshake, exact loser stream identity, active-death-before-contention replacement ordering, a bounded
two-phase DETACH/OUTPUT_ACK close, and a separate-process replacement/replay/restart gate. The host
also reserves a signed device-bound incarnation through a durable descriptor-relative lane before any
service/listener/network advertisement. Both roles remain disabled by default and publish content-free lifecycle evidence.
rev0021 added
exact-at-the-gate queue tails, coherent provider outcomes, retained-head streak/age, monotonic
lifecycle time, and a bounded R7 analyzer. rev0022 binds exact message/input/output/event coordinates,
a reconstructable balanced schedule, raw same-clock timestamp derivation, auxiliary evidence digests,
and two ephemeral capture-role signatures into one canonical R7 v2 bundle. The same revision adds
profile v2 confinement, a verified common capability floor, default baseline seccomp, and opt-in fail-closed MDWE
plus Landlock ABI 10 strict confinement without changing the Ratox wire format or remote profile
choice. rev0023 adds argument-aware denials for the reviewed terminal/console ioctl set and legacy clone
namespace flags, forces clone3 through the inspectable legacy fallback while proving ordinary fork and
thread creation, freezes the established session/parent-death lifecycle, proves closure of descriptors
above the rlimit ceiling, and requires pidfd-revalidated session-wide teardown for baseline/strict.
rev0024 verifies and pins the procfs inventory/member directories, binds PID/session/start-time
witnesses around pidfd acquisition, requires three consecutive empty full-session inventories before
leader reap, denies payload process-handle interfaces, and seals an enabled terminal host's dump/core
policy before Agent construction. rev0025 adds an explicit optional cgroup-v2 delegation, creates and
inode-pins one domain leaf per hardened PTY, attaches the helper before manifest release, routes KILL
through `cgroup.kill`, requires recursive `populated 0`, and removes the exact leaf before leader reap.
Empty configuration retains rev0024 supervision and configured failure never silently downgrades.
rev0026 adds one shared message-bound local-IPC layer: every request and response on both private
seqpacket planes carries mandatory kernel credentials, optional kernel pidfds, exact peer matching,
and fail-closed ancillary parsing. Terminal ownership follows the sender process through pidfd exit;
administrative requests have a finite lease and exact listener/stale/replacement inode ownership.
rev0027 multiplexes the administrative pending set and the active terminal contender set: each peer
has an independent lease, global and per-process descriptor quotas, bounded accept refills, and bounded
per-cycle record work. Active terminal events remain ahead of contender work, and no contender path
waits inside the active controller loop.
rev0028 binds every new delegated PTY leaf to the creator's canonical Linux boot ID, PID, pinned
procfs field-22 start time, and local sequence. Startup acquires the signed host-incarnation lease
before it preflights the complete bounded reserved namespace. It preserves exact live owners,
recursively kills and removes only proved-stale versioned leaves, removes empty legacy leaves, and
refuses populated legacy or malformed reserved entries before PTY-factory or transport activation.
rev0029 adds one optional global cgroup resource envelope. It requires requested controllers to be
both available and active, proves controller files are daemon-owned and payload-unwritable, writes and
exactly reads back `pids.max`, `memory.max`, `memory.swap.max`, `memory.oom.group`, and `cpu.max`, and
repeats the policy before attaching each blocked helper. rev0030 advances canonical profiles to v3 and
composes profile-scoped budgets monotonically beneath that host ceiling. Startup, after lease
acquisition but before orphan recovery or PTY-factory/network activation, preflights every distinct
`(payload identity, effective budget)` pair. The production factory recomputes the same exact policy at
spawn, and runtime status publishes aggregate host/profile/preflight counts only. rev0031 adds one
production-factory-wide exact reservation ledger over configured process, memory, and swap maxima.
rev0032 extends the same ledger to exact rational CPU bandwidth at one explicit aggregate accounting
period. rev0033 adds a profile-scoped soft memory throttle below the hard ceiling, exact kernel
readback, and teardown-time local PID, memory, and CPU outcome counters. rev0034 advances canonical
profiles to v5 with one exact numeric block device plus read/write BPS and IOPS ceilings, requires
matching host/profile device identity, semantically verifies complete `io.max` policy before helper
attachment, and retains saturating `io.stat` read/write/discard bytes and operations after quiescence.
rev0035 adds protected optional CPU, memory, and I/O PSI records for every session leaf, verifies zero
absolute microsecond baselines, captures final `some` and optional `full` totals after recursive
quiescence, and aggregates them with explicit capability counts. Completed and incomplete observations
are aggregated separately with content-free totals.
rev0036 adds independently optional zero-baseline PID, memory, and swap lifetime peaks plus
quota-independent CPU usage/user/system accounting with complete optional bandwidth and burst tuples.
Owner-private projection preserves capability counts, saturation-safe peak sums/maxima, and CPU
work/throttle/burst totals without labels or live-policy claims.
rev0037 adds protected memory-work, swap-event, local-freeze, and IRQ-pressure evidence. It
retains bounded page-fault, reclaim, swap-page, swap-threshold/failure, local frozen-time, and IRQ full
stall totals only after recursive quiescence. Mandatory policy-linked files fail closed, optional newer
interfaces carry explicit capability counts, and owner-private projection remains content-free.
rev0038 adds an optional descriptor-pinned delegated-root PSI controller for new PTY admission. It is
constructed under the signed host lease before resource probes, orphan recovery, listener, or network
mutation; requires enabled accounting before and after complete CPU/memory/I/O `avg10` samples; and
applies exact integer basis-point thresholds plus hysteresis before aggregate reservation or spawn
mutation. Sampling failure returns local unavailability, latches closed, and retains bounded typed
last-sample evidence privately. Sequential reads are not claimed atomic, and the construction host's
missing per-cgroup PSI remains a named capability skip rather than positive kernel evidence.
rev0039 adds one dedicated kernel PSI trigger descriptor for each configured CPU `some`, memory
`full`, or I/O `full` metric. A bounded monitor polls `POLLPRI`, transfers typed event counts through
atomics, latches admission closed for at least one configured tracking window, and requires the full
rev0038 avg10 hysteresis sample before reopening. Monitor setup, polling, source-loss, and handoff
failures fail closed. Owner-private status exposes monitor health, remaining hold time, bounded typed
failure, total/per-resource events, failures, and trigger-caused close transitions. Shutdown wakes the
monitor through `eventfd` before monitored descriptors close; already admitted sessions are not
preempted.
Configuration also fails closed if CMake, `REVISION`, and the executable identity header drift. Every enabled
effective policy must carry finite matching values, fit once before activation,
and map to an integral normalized CPU quota; no ratio is rounded. Admission atomically charges the
complete vector before mutable spawn work, move-only RAII releases every early failure, and successful
sessions retain the charge through cgroup quiescence/removal and leader reap. Owner-private status
retains configured maxima and CPU period, current/peak totals, active counts, capacity rejections, and
stranding without profile, identity, path, command, or terminal content.


The rev0015 root request record is implemented in:

```text
include/iotox/local/friend_request_fifo.hpp
src/local/friend_request_fifo.cpp
include/iotox/local/peer_fifo.hpp
src/local/peer_fifo.cpp
src/local/runtime_tree.cpp
src/agent.cpp
```

It carries a complete 38-byte Tox address as 76 hexadecimal characters, one literal TAB, and a
1..921-byte request message. The FIFO is an adapter to the same typed Agent operation used by the
local control protocol; it owns no second friendship model and no durable queue.

## Tests and exact doubles

```text
tests/
```

This includes the C++ test registry, a separate-process one-binary fixture, an independent native
PTY process fixture, exact shared-library c-toxcore and Argon2 doubles, and twelve parser/state fuzz
targets. The direct owned registry contains 844 checks and the default suite contains 62 CTest
entries; the preserved Mutorr incubator adds its own registry and two CTest entries.

rev0045 retains rev0044's signed-update coverage and adds the routed-privacy construction gate:

```text
canonical fixed-size manifest and owner-private policy codecs plus hostile-input fuzzing
no-clobber stable bundle creation, digest/signature binding, and unsafe-path/tamper refusal
device-signed stage/apply/health/confirm state with exact incarnation fencing
state-first apply and pointer-first rollback crash recovery plus abrupt process interruption
non-destructive eight-slot exhaustion, immutable mode-0400 inactive-slot validation, and protected-slot quarantine
real-Agent sync publication through accepted HEAD, confirmation, and automatic rollback
genuine two-guest 4 MiB direct-UDP and forced-TCP Sandwurm lifecycle qualification
policy-v2 signer epoch, retired-signer denial, active/revoked overlap rejection, CLI lint/template/rotation, and corpus coverage
no-clobber release signer creation/public inspection, last-signer refusal, and two-epoch overlap retirement
dry-run and bounded no-replace quarantine, Agent-local reporting, partial-move restart continuation, and unsafe-entry refusal
fixed ICQ2/IUS1 codecs, feature dependencies, authority/replay/store/restart binding, and public CLI
genuine two-guest remote durable stage before local apply/restart/confirm on direct UDP and forced TCP
policy-v3 and manifest/state kind binding without opaque-state reinterpretation
selected-slot revalidation into a sealed anonymous executable image through the exact internal helper
sequence-bound readiness, live confirmation gating, exit-before-readiness rollback, and confirmed-service relaunch
genuine dual-carrier process-interruption qualification for the sealed service adapter inside two Sandwurm guests
genuine two-guest strict-SOCKS packet containment, proxy loss/recovery, and restored text qualification
whole-binary configured-target SOCKS success/target-refusal/proxy-refusal qualification
718 fixture-aware direct checks, 54 default CTest targets, and 12 fuzz targets
```

rev0039 adds focused continuous delegated-root PSI-trigger coverage for:

```text
portable 2-second-quantum trigger-window and per-resource stall validation with matching avg10 policy
typed canonical NUL-terminated kernel trigger encoding and one trigger per descriptor
pure trigger-hold close, repeat, expiry, and avg10-hysteresis reopen boundaries
bounded eventfd monitor shutdown and fail-closed monitor/source failure projection
owner-private health, hold, hold-rejection, per-resource event, failure, and transition counters
359 fixture-aware direct checks and nineteen default CTest targets
live quiet-monitor registration qualification or one explicit code-77 capability skip
```

rev0038 adds focused delegated-root PSI-admission coverage for:

```text
exact canonical PSI percentage parsing without floating point
strict threshold, equality, close, latch, and reopen hysteresis boundaries
controller construction before recovery/network mutation and sampling before reservation/spawn mutation
cgroup.pressure enabled-state proof before and after configured descriptor-pinned reads
normalized local-unavailable rejection with typed private last-sample cause and preserved last valid values
mutex-serialized concurrent admission with exact saturating counters
356 fixture-aware direct checks and nineteen default CTest targets
real private-cgroup process qualification or one explicit code-77 capability skip
```

rev0037 adds focused memory-work, swap-event, freeze, and IRQ-pressure coverage for:

```text
strict bounded keyed parsing of memory.stat, memory.swap.events, cgroup.stat.local, and irq.pressure
complete page-fault, major-fault, reclaim-scan/reclaim-steal, and swap-in/swap-out memory work tuples
mandatory policy-linked descriptors plus explicitly optional newer kernel capability descriptors
protected pre-attachment descriptor opening, exact zero baselines, and post-quiescence final capture
whole-session incomplete outcomes instead of partial evidence when any acquired final record fails
explicit capability counts and saturation-safe aggregate page, event, freeze, and IRQ-full totals
owner-private content-free projection without session, profile, path, device, peer, or command labels
351 fixture-aware direct checks, eighteen default CTest targets, and extended cgroup-record fuzz coverage
live page-fault and cgroup freeze/unfreeze oracle with direct final-file equality comparison
```

rev0036 adds focused peak-resource kernel-accounting coverage for:

```text
strict bounded canonical pids.peak, memory.peak, and memory.swap.peak single-value parsing
protected independently optional peak descriptors opened before attachment with exact zero baselines
post-quiescence/pre-removal lifetime high-water marks with explicit absent-versus-zero semantics
quota-independent cpu.stat observation and mandatory usage/user/system work tuple
optional all-or-none bandwidth and nested burst tuples with partial/detached rejection
peak observed-session counts, saturation-safe sums/maxima, and nested CPU capability counts
owner-private content-free CPU user/system/throttle/burst and peak projection
348 fixture-aware direct checks, eighteen default CTest targets, and extended cgroup-record fuzz coverage
live unlimited-CPU accounting and available-peak equality oracle with explicit named controller skips
```

rev0035 adds focused pressure-stall kernel-accounting coverage for:

```text
bounded LF-terminated PSI parsing with canonical some fields, optional full, and unordered keyed values
strict rolling-percentage validation while retaining only absolute cumulative microsecond totals
future numeric key/class tolerance without assigning unreviewed semantics
protected optional cgroup.pressure plus CPU, memory, and I/O pressure descriptors opened before attach
exact enabled-control and zero-baseline proof for every available pressure interface
post-quiescence/pre-removal one-shot capture with whole-outcome failure instead of partial aggregation
independent CPU/memory/I/O some/full availability counts and saturating cumulative totals
twelve owner-private content-free runtime projection fields without session, profile, peer, path, or device labels
346 fixture-aware direct checks, eighteen default CTest targets, and extended cgroup-record fuzz coverage
capability-aware live memory/CPU/I/O equality oracles with explicit named delegation skips
```

rev0034 adds focused device-I/O policy and kernel-accounting coverage for:

```text
canonical profile v5 encode/decode and exact v1/v2/v3/v4 migration without invented I/O policy
canonical MAJOR:MINOR validation, complete policy pairing, and same-device host/profile composition
independent monotone minima for read/write BPS and IOPS while preserving older resource invariants
bounded unordered io.max parsing with exact standard-key readback and future-key tolerance
bounded multi-device io.stat parsing with an optional complete discard pair and saturating totals
protected zero-baseline io.stat capture after recursive quiescence and before exact removal
one-shot complete/incomplete outcome aggregation and six owner-private cumulative runtime fields
CLI validation for exact device identity and four rate options
344 fixture-aware direct checks and eighteen default CTest targets
dedicated kernel-cgroup parser fuzzing and complete eleven-target retained fuzz verification
capability-aware live I/O route with an explicit named delegation skip instead of synthetic qualification
```

rev0033 adds focused memory-throttle and kernel-outcome coverage for:

```text
canonical profile v4 encode/decode and exact v1/v2/v3 migration without invented memory.high
page-aligned memory.high validation, monotone host/profile composition, and hard-ceiling clamping
exact memory.high write/readback plus controller-specific preflight and production enforcement
bounded canonical pids.events, memory.events, and cpu.stat parsers with future-key tolerance
local-event preference with unsupported-interface fallback for childless session leaves
one-shot complete/incomplete teardown outcomes retained after recursive quiescence and before removal
saturating PID, memory-high/max/OOM/kill, CPU usage/period/throttle runtime totals
independent lifecycle, memory/PID, and CPU live-kernel routes with per-controller named skips
CMake/REVISION/header product-identity lock preventing stale executable stamps
344 fixture-aware direct checks and eighteen default CTest targets
```

rev0032 adds focused exact-rational CPU aggregate-admission coverage for:

```text
aggregate semantic validation for missing, oversized, unaligned, meaningful-zero, and exact CPU dimensions
1,120 bounded quota/period combinations checked against an independent integer oracle
atomic exact process/memory/swap/normalized-CPU charging with monotone current and peak evidence
move-only, idempotent explicit release plus fail-closed complete-charge stranding
barrier-driven deterministic process/CPU saturation with typed capacity rejections
invalid unaccountable or nonrepresentable session refusal before any charge
Agent pre-network refusal of unrooted, missing-dimension, oversized, and rounded CPU policy
production-factory charge before helper-path validation with exact early-failure rollback
owner-private configured/quota/period/current/peak/rejection/stranding runtime rendering
GCC and Clang warning-as-error matrices plus sanitizer and process-oracle routes
344 fixture-aware direct checks and eighteen default CTest targets
```

rev0030 adds or retains coverage for:

```text
shared host/profile cgroup-policy validation in CLI, codec, Agent, production factory, and direct constructor
requested-controller availability and activation checks before session-leaf creation
exact `(identity, effective budget)` pre-network probe creation, control read-back, and empty-leaf removal
pre-attachment pids/memory/swap/OOM-group/CPU control application and exact read-back
real-kernel pids exhaustion and CPU-throttling oracle branches on a qualifying topology
canonical boot UUID, owner-incarnation, and versioned session-cgroup name parsing
exact live/exited/zombie/start-time/boot-mismatch owner classification through procfs and pidfd
bounded delegated-root recovery configuration and ordinary-filesystem refusal
host-lease acquisition before cgroup mutation, PTY-factory construction, or transport activation
real isolated cgroup-v2 live preservation and deliberate creator-crash orphan reclamation
recursive payload death, populated-zero completion, exact stale-leaf removal, and empty-legacy cleanup
populated-legacy, malformed-reserved-name, and candidate-overbound fail-closed refusal
per-record request and response credential binding against connection-time peer identity
optional SCM_PIDFD identity agreement and terminal-owner pidfd exit release
optional SO_PEERPIDFD connection-process pinning before control requests and terminal OPEN
control-client server-exit release while an accepted descriptor survives elsewhere
fork-inherited client and server descriptor impersonation rejection
request-side and response-side SCM_RIGHTS closure and fail-closed rejection
administrative silent-request timeout, active-listener preservation, and replacement-inode survival
silent administrative coexistence without lease head-of-line blocking
control global/per-process pending-client admission bounds and post-close recovery
active-terminal PING/PONG completion while a silent contender retains its independent lease
terminal global/per-process contender bounds, accept refills, and per-cycle record budgets
queued-successor admission when active death and listener readiness coincide
bounded strict and future-field-compatible cgroup.events parsing
missing, duplicate, malformed, signed, and non-Boolean cgroup state rejection
inherited/root/daemon-equal identity, compatibility, relative-root, and injected-factory rejection
ordinary-directory cgroup-v2 lookalike rejection and configured fail-closed process startup
canonical profile v4 encode/decode, v1/v2/v3 migration, memory-high canonicality, exact composition, and strict-root refusal
genuine procfs mount verification and descriptor-relative member identity reads
reported PID, fixed session, live state, and field-22 start-time parsing
same-procfd identity revalidation after pidfd acquisition and before pidfd signaling
three consecutive quiescent inventories before waitable-leader reap
bounded fork churn in separate process groups during session shutdown
payload pidfd_open, pidfd_send_signal, process_madvise, and process_mrelease denial
idempotent terminal-host nondumpability and irreversible zero core limits before Agent construction
runtime capability-ceiling discovery and zero ambient/effective/permitted/inheritable verification
privileged securebits locking and complete capability-bounding-set removal
architecture mismatch killing, x32 refusal, filter installation, and hazardous syscall denial
one shared build-header-derived terminal/console ioctl policy table used by both filter and payload oracle
request-level denial of every compiled table entry, exact request-count reporting, and an ordinary-ioctl negative control
architecture-correct legacy-clone namespace-bit denial, clone3 ENOSYS fallback, and post-filter fork/thread creation
lifecycle freeze for setsid, controlling-terminal detach/reassignment, and parent-death mutation
high inherited descriptor closure through two-pass procfs inventory
forced and natural-exit cleanup of descendants in separate process groups
required live pidfd retention, exact P_PIDFD/P_PID wait observation, and waitable-leader session-wide sweeps
textual/numeric product identity coherence through the protocol HELLO fields
strict writable-cwd mutation with outside mutation, TCP, UDP, pathname Unix, signal, and MDWE denial
named fail-closed strict startup when MDWE, Landlock ABI 10, or seccomp cannot be installed
exact content-free INPUT admission/whole-frame commit joins and OUTPUT append spans
balanced deterministic two-route/six-load scheduling and run-bound trial tokens
raw controller-local and host-local timestamp derivation without cross-host subtraction
canonical schedule/sample/route/bulk digests and changed-auxiliary-evidence refusal
two distinct Ed25519 capture attestations with local boot-ID and key-consistency checks
global timestamp/event/span monotonicity, uniqueness, and overlap refusal
complete 12,000-sample signed self-test plus row/signature/event/symlink tamper cases
332 fixture-aware direct checks and sixteen default CTest targets
```

rev0030 adds focused profile-budget coverage for:

```text
canonical v3 budget round trip and byte-for-byte re-encoding
canonical v1/v2 migration to v3 with an empty budget
invalid period-without-quota, page-alignment, mixed-case none, and leading-zero refusal
scalar host/profile minimum composition including meaningful zero swap
exact overflow-free CPU ratio selection and deterministic host representation on ties
Agent refusal of an enabled profile budget without an explicit delegated root
production-factory recomposition before cgroup filesystem or spawn work
aggregate host/profile/preflight runtime metrics without policy content
current v3 terminal-profile fuzz corpus plus retained v1 seed
332 fixture-aware direct checks and sixteen default CTest targets
```

rev0029 adds focused cgroup recovery and resource-envelope coverage for:

```text
strict canonical boot-ID and owner-incarnation round trips plus malformed/overflow refusal
live creator preservation and stale creator classification without PID-only guesses
Agent recovery only after the signed host lease and before factory or network startup
competing daemon lease refusal before delegated-root inspection or mutation
real cgroup-v2 deliberate-crash orphan kill, recursive quiescence, and exact removal
empty legacy cleanup with populated legacy and malformed reserved-name refusal
complete-set scan-bound failure with no premature mutation
330 fixture-aware direct checks and sixteen default CTest targets
```

rev0020 adds coverage for:

```text
silent same-user controller expiry before OPEN and immediate successor admission
bounded contender OPEN consumption without dispatch into the active session handler
exact contender stream-ID preservation and typed resource-exhausted CLI reporting
real-process winner/loser contention with no Broken-pipe or false stream-corruption outcome
abrupt controller death, replacement resume, retained output render-before-ACK, and exact cumulative ACK
queued successor admitted when active death and listener readiness are observed in the same cycle
explicit local server-restart not-found behavior for nonpersistent session state
signed incarnation advancement, process exclusion, tamper/link/mode/identity/wraparound refusal
first-start hierarchy durability and enabled-service zero-sentinel enforcement
post-DETACH ACK-only dispatch fencing with final OUTPUT/DETACHED drain
284 fixture-aware direct checks and thirteen default CTest targets
```

rev0019 adds coverage for:

```text
pure controller route, identity, replay, queue, generation, and lifecycle fencing
canonical 32-byte ITTS local protocol with a frozen golden wire vector and bounded payloads
absolute-path, embedded-NUL, owner/mode/type, SO_PEERCRED, and pre/post inode socket checks
one-client admission, live-listener protection, stale-inode reclamation, and exact unlink ownership
Agent controller activation, exact peer resolution, typed denial, route loss, resume, and revocation
one-binary terminal argument, absent-daemon, raw-mode restoration, resize, output-before-ACK, and escapes
269 fixture-aware direct checks, eleven default CTest targets, and a tenth protocol fuzzer
```

rev0018 adds coverage for:

```text
fail-closed Ratox activation before toxcore startup, including missing/insecure/empty profile policy
runtime HELLO selection with default-off local support, one-sided non-negotiation, and bilateral bit 23
live Agent packet-0xA2 dispatch through transcript, online epoch, stable principal, and exact authority
v1-owner terminal denial returning a canonical result without touching the PTY factory
coordinator OPEN/ATTACH/RESUME/DETACH/INPUT/ACK/RESIZE/CLOSE/EXIT lifecycle and exact replay
whole-frame staged PTY commitment, partial-write terminalization, output suffix and explicit gap
bounded session/tombstone/replay/outbound/event resources and exact duplicate/conflict behavior
retained SENDQ output, stale-route detachment, authority-revocation closure, and finite shutdown drain
Agent-level OPEN_RESULT SENDQ retention followed by signed revocation, queue purge, and no later send
round-robin service fairness under global read/write/frame budgets
private mode-0600 ratox-events rotation and content exclusion for terminal bytes, argv, environment,
cwd, paths, profile IDs, and error strings
retained rev0017 profile/process, rev0016 authority, and rev0015 session/carrier regressions
```

rev0017 adds coverage for:

```text
strict canonical terminal profile and principal-binding encodings
owner-only no-follow whole-store load, including path/link/mode/owner/extra-entry rejection
locale-independent canonical bytes and malformed/noncanonical decoder rejection
allowlisted frozen environment, hazardous-name rejection, dimensions, limits, and identities
atomic registry replacement and generation-coherent concurrent resolve/snapshot behavior
bounded nonblocking terminal controller and observe-before-signal HUP/TERM/KILL lifecycle
real Linux PTY cwd/environment/window, descriptor hygiene, no-new-privileges, ambient-capability clearing, and core limits
complete signal reset plus parent-death contract under destructor-free supervisor loss
current and exact UID/GID behavior, supplementary-group clearing, and post-drop parent-death re-arm
backend byte bounds, binary exact-byte echo, resize clamps, setup-stage errors, and reap
terminal-profile fuzzer seeds plus retained seven prior parser/state fuzzers
retained rev0016 authority-ledger v2 migration, negotiation, rollback-guard, and CLI regressions
retained rev0015 Ratox R1 replay, attachment, quota, pacing, and state-fuzz regressions
retained exact outgoing-request, provider, process, command, text, and finite-file regressions
```

The doubles prove only the API subset and controlled event behavior IoTox consumes. They are not
substitute implementations of the public Tox network, official Argon2, or routed transports.

## Build and run tools

```text
tools/test.sh
tools/build-matrix.sh
tools/focused-static-analysis.py
tools/fuzz-smoke.sh
tools/agent-session-stress.sh
tools/run-mock-node.sh
tools/build-standalone.sh
tools/verify-standalone.sh
tools/run-real-peer-smoke.sh
tools/run-four-route-lab.sh
tools/run-socks5-forwarder.py
tools/run-socks5-adversary.py
tools/run-i2p-sam-socks.py
tools/run-i2p-sam-forward.py
tools/run-i2p-sam-smoke.py
tools/run-i2p-tox-fronts.py
tools/verify-i2p-sam-smoke.py
tools/run-tox-tor-smoke.py
tools/run-ratox-latency-lab.sh
tools/run-ratox-impairment-lab.sh
tools/run-ratox-pacing-lab.sh
tools/fetch-pinned-dependencies.sh
tools/check-lone-entrance.sh
tools/refresh-retained-artifacts.sh
tools/make-revision-archive.sh
tools/make-repository-datacube.sh
tools/clean-workspace.py
tools/qualify-route-policy-campaign.py
tools/run-sync-shadow.py
tools/verify-sync-shadow-sandwurm.py
tools/export-sync-shadow-sandwurm.py
```

`tools/fuzz-smoke.sh` copies reviewed seeds into build-local corpora and can validate/decode the
Ratox and signed-update hexadecimal seeds with `xxd`, Python 3, or Perl; it fails closed if no decoder
exists.

## Active documents

```text
README.md
BUILDING.md
PACKAGE.md
CHANGELOG.md
LICENSE.md
dependencies.lock
docs/architecture.md
docs/README.md
docs/vision.md
docs/what-iotox-is-becoming.md
docs/ratox-successor-assessment.md
docs/ratox-interactive-plan.md
docs/ratox-service-implementation-plan.md
docs/ratox-ssh-status.md
docs/ratox-rescue-toolbox.md
docs/sync-doctor.md
docs/sync-recovery-rehearsal.md
docs/future-cli-contract.md
docs/security-ratox-v1.md
docs/protocol-ratox-v1.md
docs/ratox-friend-lifecycle-v1.md
docs/ratox-message-fifo-v1.md
docs/ratox-command-fifo-v1.md
docs/ratox-file-fifo-v1.md
docs/protocol-draft.md
docs/protocol-session.md
docs/protocol-authority-v1.md
docs/protocol-authority-v2.md
docs/terminal-profile-v1.md
docs/terminal-profile-v2.md
docs/terminal-profile-v4.md
docs/terminal-profile-v5.md
docs/terminal-profile-v6.md
docs/terminal-profile-v7.md
docs/terminal-profile-v3.md
docs/terminal-client-v1.md
docs/protocol-command-v1.md
docs/protocol-signed-update-bundle-v1.md
docs/update-linux-service-v1.md
docs/command-store-v2.md
docs/command-store-v3.md
docs/recovery-and-ownership.md
docs/networks.md
docs/threat-model-draft.md
docs/testing.md
docs/roadmap.md
docs/everyday-sync-plan.md
docs/sync-trust-graduation.md
docs/workspace-retention.md
docs/open-questions.md
docs/revision-packaging.md
docs/decisions/
docs/governance/
docs/research/
```

The current decision and source review are:

```text
docs/decisions/0056-genuine-tests-reuse-clean-key-baselines.md
docs/evidence/2026-08-15-reusable-and-fresh-test-identities.md
docs/decisions/0057-synchronous-file-chunks-and-coalesced-progress.md
docs/evidence/2026-08-15-four-route-lab.tsv
docs/research/c-toxcore-0.2.23-four-route-file-lab-rev0015.md
docs/decisions/0058-cache-unchanged-transfer-projections.md
docs/evidence/2026-08-15-stream-sweep-udp.tsv
docs/evidence/2026-08-15-stream-sweep-tcp.tsv
docs/research/c-toxcore-0.2.23-stream-concurrency-lab-rev0015.md
docs/decisions/0059-prioritize-interactive-work-and-qualify-custom-carriers.md
docs/decisions/0060-pace-interactive-traffic-and-separate-reliable-control-from-replaceable-state.md
docs/decisions/0061-freeze-ratox-v1-as-a-fenced-paced-lossless-byte-protocol.md
docs/decisions/0062-complete-ratox-r1-with-a-fail-closed-pure-session-engine.md
docs/decisions/0063-explicit-signed-authority-ledger-v2-migration.md
docs/decisions/0064-seal-local-terminal-profiles-behind-fork-safe-pty-adapter.md
docs/decisions/0065-gate-live-ratox-dispatch-before-network.md
docs/decisions/0066-separate-private-terminal-controller-stream.md
docs/decisions/0067-bound-local-controller-admission-and-contention.md
docs/decisions/0068-reserve-signed-ratox-host-incarnation-before-network.md
docs/decisions/0069-measure-queue-tails-and-typed-ratox-send-outcomes.md
docs/decisions/0070-qualify-ratox-r7-with-bounded-fail-closed-evidence.md
docs/decisions/0071-bind-ratox-r7-to-attested-raw-evidence.md
docs/decisions/0072-seal-terminal-capabilities-and-add-tiered-kernel-confinement.md
docs/decisions/0073-fence-terminal-lifecycle-and-contain-pty-sessions.md
docs/decisions/0074-pin-session-identities-and-seal-terminal-process-domain.md
docs/decisions/0075-own-hardened-pty-lifecycles-with-delegated-cgroup-v2.md
docs/decisions/0076-bind-local-seqpacket-records-to-kernel-sender-evidence.md
docs/decisions/0077-bound-and-multiplex-local-seqpacket-admission.md
docs/decisions/0078-pin-local-seqpacket-connections-to-peer-process-lifetimes.md
docs/decisions/0079-bind-delegated-cgroup-lifecycles-to-boot-and-process-incarnations.md
docs/decisions/0080-enforce-global-pty-resource-budgets-in-delegated-cgroups.md
docs/decisions/0081-compose-profile-cgroup-budgets-under-host-ceilings.md
docs/decisions/0082-admit-pty-sessions-under-exact-aggregate-cgroup-reservations.md
docs/decisions/0083-admit-exact-rational-aggregate-cpu-bandwidth.md
docs/decisions/0084-add-memory-throttle-and-retain-kernel-session-outcomes.md
docs/decisions/0085-add-device-io-ceilings-and-retain-kernel-io-accounting.md
docs/decisions/0086-retain-cgroup-pressure-stall-outcomes.md
docs/decisions/0087-retain-cgroup-lifetime-peaks-and-complete-cpu-work.md
docs/decisions/0088-retain-memory-work-swap-freeze-and-irq-outcomes.md
docs/decisions/0089-admit-new-pty-sessions-with-cgroup-psi-hysteresis.md
docs/decisions/0090-latch-ratox-admission-with-continuous-cgroup-psi-triggers.md
docs/ratox-r7-evidence-v2.md
docs/terminal-profile-v3.md
docs/terminal-profile-v2.md
docs/research/linux-cgroup-psi-admission-rev0038.md
docs/research/linux-cgroup-psi-trigger-tripwire-rev0039.md
docs/research/clang-path-sensitive-analysis-rev0039.md
docs/research/cloudtainer-build-report-rev0039.md
docs/research/cloudtainer-build-report-rev0038.md
docs/research/memory-work-swap-irq-freeze-kernel-accounting-rev0037.md
docs/research/cloudtainer-build-report-rev0037.md
docs/research/peak-resource-kernel-accounting-rev0036.md
docs/research/pressure-stall-kernel-accounting-rev0035.md
docs/research/cloudtainer-build-report-rev0035.md
docs/research/io-bandwidth-kernel-accounting-rev0034.md
docs/research/cloudtainer-build-report-rev0034.md
docs/research/memory-high-kernel-outcome-telemetry-rev0033.md
docs/research/exact-rational-cpu-reservation-admission-rev0032.md
docs/research/aggregate-cgroup-reservation-admission-rev0031.md
docs/research/profile-scoped-cgroup-budget-ceilings-rev0030.md
docs/research/ratox-r7-attested-evidence-chain-rev0022.md
docs/research/terminal-confinement-rev0022.md
docs/research/terminal-session-containment-rev0023.md
docs/research/terminal-process-domain-hardening-rev0024.md
docs/research/message-bound-local-ipc-hardening-rev0026.md
docs/research/bounded-local-ipc-admission-rev0027.md
docs/research/process-pinned-local-ipc-lifetimes-rev0027.md
docs/research/controller-enforced-cgroup-resource-budgets-rev0029.md
docs/research/boot-bound-cgroup-orphan-recovery-rev0028.md
docs/research/delegated-cgroup-session-containment-rev0025.md
docs/research/ratox-r7-observability-rev0021.md
docs/evidence/2026-08-17-ratox-restart-fence-process.md
docs/research/ratox-controller-fault-gate-rev0020.md
docs/research/ratox-restart-fence-rev0020.md
docs/research/ratox-controller-stream-rev0019.md
docs/terminal-client-v1.md
docs/research/ratox-agent-dispatch-rev0018.md
docs/research/linux-pty-profile-process-boundary-rev0017.md
docs/research/authority-v2-terminal-capability-migration-rev0016.md
docs/research/c-toxcore-0.2.23-ratox-r1-fail-closed-state-review-rev0015.md
docs/evidence/2026-08-15-ratox-latency-udp.tsv
docs/evidence/2026-08-15-ratox-latency-tcp.tsv
docs/evidence/2026-08-15-ratox-impairment/
docs/evidence/2026-08-15-ratox-pacing/
docs/research/c-toxcore-0.2.23-ratox-latency-lab-rev0015.md
docs/research/c-toxcore-0.2.23-ratox-impairment-lab-rev0015.md
docs/research/c-toxcore-0.2.23-ratox-pacing-lab-rev0015.md
docs/decisions/0055-durable-offline-outbox-lifecycle.md
docs/command-store-v3.md
docs/evidence/2026-08-15-durable-offline-lifecycle.md
docs/decisions/0049-root-request-fifo-is-an-exact-complete-address-adapter.md
docs/research/c-toxcore-0.2.23-ratox-outgoing-request-ingress-rev0015.md
docs/research/cloudtainer-build-report-rev0015.md
docs/research/cloudtainer-build-report-rev0016.md
docs/research/cloudtainer-build-report-rev0017.md
docs/research/cloudtainer-build-report-rev0018.md
docs/research/cloudtainer-build-report-rev0019.md
docs/research/cloudtainer-build-report-rev0020.md
docs/research/cloudtainer-build-report-rev0021.md
docs/research/cloudtainer-build-report-rev0022.md
docs/research/cloudtainer-build-report-rev0023.md
docs/research/cloudtainer-build-report-rev0024.md
docs/research/cloudtainer-build-report-rev0025.md
docs/research/cloudtainer-build-report-rev0026.md
docs/research/cloudtainer-build-report-rev0027.md
docs/research/cloudtainer-build-report-rev0029.md
docs/research/cloudtainer-build-report-rev0030.md
docs/research/cloudtainer-build-report-rev0033.md
docs/research/cloudtainer-build-report-rev0032.md
docs/research/cloudtainer-build-report-rev0031.md
docs/research/cloudtainer-build-report-rev0028.md
docs/research/cloudtainer-build-report.md
artifacts/README.md
artifacts/rev0045/
```

The immediately preceding friendship decision remains in force where not superseded:

```text
docs/decisions/0048-friendship-mutations-are-public-key-bound-exact-token-decisions.md
docs/research/c-toxcore-0.2.23-ratox-friend-lifecycle-rev0014.md
```

Historical entrances and old reports live under `docs/history/` or carry their revision in the
filename. They are provenance, not current governance.

## Pinned external inputs

```text
dependencies.lock
third_party/README.md
third_party/eff_large_wordlist_2016-07-18.txt
```

The embedded EFF word list is a product input to RecallRoot-v1 and is retained with provenance and
digest. c-toxcore, libsodium, and Argon2 source are pinned but not embedded in this cube.

## Retained evidence

```text
artifacts/README.md
artifacts/rev0045/tox-tor-smoke.json
artifacts/rev0045/tox-operator-tor-smoke.json
artifacts/rev0045/i2p-sam-two-router-smoke.json
artifacts/rev0045/actual-tor-path-population.json
artifacts/rev0045/content-lane-counterbalance.json
artifacts/rev0045/SHA256SUMS
```

The tracked source tree keeps only small, source-referenced receipts. Historical bulky revision
transcripts, prebuilt binaries, fuzzer executables, CTest logs, standalone attempts, and generated
matrix reports are not part of the public source snapshot. They belong in ignored build/export
locations or in explicitly verified datacubes. Host-generated standalone material remains separate
from source and is included in a delivered repository datacube only when its recorded
`source-commit` matches the exact datacube commit. Retained evidence contains no live identity,
secret, customer state, or broadened public-network success claim.

## Incubator

```text
incubator/mutorr/
```

Mutorr remains preserved and buildable but is not linked into the default product or immediate
northstar. Its history is retained without allowing it to displace the ratox successor.

## Intentionally absent

The release cube must not contain:

```text
real RecallRoot phrases
live Tox savedata or secret keys
live IoTox device identities
signed customer authority ledgers
command stores or received user files
runtime sockets, FIFOs, journals, or staging files
build directories or fetched dependency source
vendor reassignment keys
unqualified Tor/I2P anonymity, production Tox-over-I2P claims, or independent actual-Tor exit/time claims
```
