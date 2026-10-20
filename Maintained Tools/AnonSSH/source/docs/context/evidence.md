# Verification and Evidence

This document explains what AnonSSH tests, where results live, and how to interpret
them. It does not replace the [specification ledger](../../specs/spec_ledger.json): the
ledger is authoritative for contract status and exit conditions. Exact values belong to
the JSON artifact from a specific invocation, not to timeless product documentation.

## Evidence hierarchy

AnonSSH uses four evidence levels:

1. **Deterministic core tests** prove codecs, state machines, policies, timeouts,
   allocation behavior, and faults under fixed inputs and virtual time.
2. **Controlled real-socket tests** prove asynchronous progress and scheduling against
   paced local lanes without public-network variation.
3. **Packaged local tests** prove the exact Nix/static artifact, embedded programs,
   OpenSSH-to-Dropbear login, service lifecycle, and external-consumer boundary.
4. **Live public-overlay campaigns** prove end-to-end integration and collect descriptive
   Tor/I2P behavior under the conditions of one run.

Levels 1-3 can enforce deterministic thresholds. Public Tor and I2P are non-stationary;
live campaigns enforce exact delivery, bounded lifecycle, required topology, and cleanup,
but throughput and latency values are observations rather than universal release
guarantees.

## Artifact rules

Normal targets write machine-readable output beneath ignored `artifacts/`. Stdout and
stderr are operator diagnostics, never the source of truth. Live targets write a
versioned JSON result only after their hard checks pass; long campaigns additionally
write atomic checkpoints so completed scenarios and the causal failure survive an
interruption.

Review an artifact's `schema`, `status`, exact hashes/byte counts, active and protected
lanes, provider contribution, outstanding sender state, process cleanup, and failure
cause before interpreting performance fields. Do not compare values from different
schema generations as if missing fields were zero. Migrated endurance history labels
unavailable old measurements instead of inventing them.

Artifacts are disposable except for an intentionally retained endurance corpus. The
endurance evidence keeps fixed cumulative aggregates, a bounded cold baseline, and a
bounded rolling window. Router state has an explicit disk ceiling. Normal exit, signal,
or failure stops owned processes and removes leases/sockets while preserving only that
bounded router corpus. `make reset-bond-endurance` removes it when no campaign owns the
lease.

## Deterministic and packaged gates

| Target | Contract |
| --- | --- |
| `make test-quick` | Formatting, Clippy, and all workspace unit/integration tests. |
| `make test-bond` | Focused core, runtime, provider, compatibility, and controlled-capacity bond tests. |
| `make check-i2p-bootstrap` | Embedded corpus schema, digest, source, longevity, and RouterInfo-age validation. |
| `make test-service-lifecycle` | Isolated user-service install/unlock/start/status/stop/uninstall and systemd verification. |
| `make test-package-consumer` | External `pkgs.callPackage` consumption through caller-selected nixpkgs. |
| `make package-monsternix` | Nix-integrated package, external store runtimes, and absent embedded executable payloads. |
| `make smoke` | Wrapped package version, doctor, and embedded deterministic test reports. |
| `make package-static` | Self-contained x86-64 artifact, static embedded programs, local SSH, complete materialized source inventory, zero source-archive symlinks, and release metadata. |
| `make package-static-reproducible` | Independent rebuilds with identical executable digest. |
| `make gate` | Required review gate combining deterministic, package, consumer, service, static, and smoke proofs. |
| `make test-fuzz` | Fixed-seed malformed and valid-roundtrip parser campaigns emitted by the shipped binary. |

`make gate` deliberately does not run public-overlay campaigns. Review must not become
dependent on mutable internet conditions or multi-hour resource use.

## Live campaign catalog

| Target | Primary purpose | Principal artifact |
| --- | --- | --- |
| `make live-tor` | Direct Tor derived-key SSH. | `artifacts/live/tor.txt` |
| `make live-i2p` | Direct I2P derived-key SSH using retained state. | `artifacts/live/i2p.txt` |
| `make live-i2p-fresh` | Fresh managed i2pd login with ordinary reseed disabled. | `artifacts/live/i2p-fresh.json` |
| `make live-i2p-pool` | One bond uses two independent owned i2pd routers. | `artifacts/live/i2p-pool.json` |
| `make live-bond` | Mixed Tor/I2P non-SSH striping and redundant realtime delivery. | `artifacts/live/bond.json` |
| `make live-bond-ssh` | Default progressive 8+8-candidate bonded SSH path. | `artifacts/live/bond-ssh.json` |
| `make live-bond-tools` | Rsync, Git, Borg, modern scp/SFTP, legacy scp, SSHFS, remote process semantics, and bond-session reuse. | `artifacts/live/bond-tools.json` |
| `make live-bond-tor-ssh` | Four-required-lane Tor-only bond without i2pd. | `artifacts/live/bond-tor-ssh.json` |
| `make live-bond-i2p-ssh` | Four-required-lane I2P-only bond without Tor. | `artifacts/live/bond-i2p-ssh.json` |
| `make live-adaptive-bond-ssh` | Load-driven expansion, contribution, typing isolation, and contraction. | `artifacts/live/adaptive-bond-ssh.json` |
| `make live-auto-topology` | Authenticated automatic selection of mixed and homogeneous bonds. | `artifacts/live/auto-topology.json` |
| `make live-auto-fallback` | Delayed direct recovery wins while bond formation is deliberately stalled. | `artifacts/live/auto-fallback.json` |
| `make live-concurrent-bond-ssh` | Three SSH clients, two destination sessions, six bond streams, and one shared four-router low-profile pool. | `artifacts/live/concurrent-bond-ssh.json` |
| `make live-bond-forward` | Exact bidirectional named local TCP forwarding over the mixed bond. | `artifacts/live/bond-forward.json` |
| `make live-bond-native` | Concurrent hash-verified ALP bulk and real-time streams over one reused mixed bond. | `artifacts/live/bond-native.json` |
| `make live-pool-recovery` | Tor, I2P, and temporary zero-lane failure with exact repair on fixed 8+8 stress topology. | `artifacts/live/pool-recovery.json` |
| `make live-process-restart` | Broker/server crash, stale-state reclamation, retained roots, and exact reconnect. | `artifacts/live/process-restart.json` |
| `make live-bond-scale` | Repeated 1+1, 2+2, 4+4, and 8+8 fixed-cardinality directional scaling. | `artifacts/live/bond-scale.json` |
| `make live-bond-soak` | Explicit 1+1 through 16+16 high-resource fixed-cardinality campaign. | `artifacts/live/bond-soak.json` |
| `make live-bond-endurance` | Operator-selected continuous adaptive workload over a retained router corpus. | `artifacts/live/bond-endurance.json` |

The scale and soak targets label state age, exclude router startup from measured transfer
goodput, keep raw rounds, report adjacent-cardinality ratios, and overlap fixed-cadence
realtime probes with bulk. Directional hashes prevent crossed-stream success. A slow
realtime echo remains evidence even when it outlives the bulk phase; otherwise severe
tails would be censored.

## Hard checks versus observations

Hard live checks include, as appropriate:

- exact byte counts and independent payload hashes;
- authenticated expected topology and failure domains;
- actual acknowledged contribution from required lanes/providers;
- protected-pool use derived from runtime state;
- bounded retransmission, repair, and terminal deadlines;
- zero final unacknowledged payload;
- expected process count during the scenario; and
- complete cleanup of owned processes, endpoints, sockets, and leases.

Descriptive fields include absolute goodput, latency percentiles, startup time, CPU, RSS,
disk, queue delay, provider share, and ratios between public-overlay trials. They are
useful for controller tuning and regression hunting. They are not SLAs and cannot prove
a universal scaling curve from one host or time window.

## Retained engineering conclusions

The campaigns have changed product policy in several durable ways:

- More lanes are not monotonically faster. The 4+4/8+8 campaigns varied materially by
  direction and run. The 16+16 soak improved simultaneous bidirectional median goodput
  but regressed or barely changed unidirectional medians while roughly doubling resource
  cost. The release therefore keeps an 8+8 candidate inventory and 16-active-lane
  ceiling; 16+16 remains evidence-only.
- A 1+1 mixed topology has no spare lane outside its two-lane protected pool, so it
  cannot physically isolate bulk from realtime. Larger healthy topologies can.
- Unequal lanes must be scheduled by predicted delivery and periodically reprobed, not
  round robin or equal provider share. Controlled six-lane evidence requires every path
  to contribute while preserving at least 80 percent of independently measured aggregate
  capacity.
- Long adaptive runs exposed two lifetime limits that short tests missed: bounded stream
  tombstones and the former 256-random-nonce repair horizon. The current retirement
  watermarks and v3 sliding join window crossed both former boundaries in a completed
  24-hour run.
- Protected mixed-provider racing can produce winners from both overlays, but retained
  quiet evidence was usually won by Tor. Provider-diverse protection is therefore a
  resilience policy, not a claim that I2P generally lowers minimum latency.
- Independent SSH streams prevent one bond stream's ordered bulk backlog from directly
  blocking another command. Public overlays still impose propagation and tunnel tails;
  no retained result justifies a LAN-like typing SLA or blind local echo.
- Process restart reliably restores new connections from retained roots, but it does not
  preserve the in-memory bytes of an existing SSH stream. Documentation and tests require
  explicit old-stream failure rather than pretending otherwise.

Exact dated measurements that established these conclusions remain in the relevant
ledger assumptions/exit conditions and generated artifacts. They are intentionally not
copied into the README, architecture, and protocol documents.

## Longitudinal I2P evidence

I2P bootstrap observation is different from a performance campaign. The versioned
[`bootstrap/i2p-observations.json`](../../bootstrap/i2p-observations.json) ledger is
monotonic identity history; generated observation/curation reports live under
`artifacts/`.

As of the 2026-10-19T18:01:46Z observation, the retained ledger has 2,259 identities:
863 with one distinct UTC observation day, 658 with two, and 738 with three. Of these,
637 meet the three-day/seven-day policy. Curation selected all 636 qualifying identities
that were still corroborated by both mature sources; one temporarily absent identity
remains retained in the ledger. The promoted v3 corpus has a shortest qualifying span of
610,535 seconds and manifest SHA-256
`10afd55f062a1acd23cbc9023443bb7b413e99145b5c17c76b2f80b9209b612c`.

`make live-i2p-fresh` then built the packaged product, disabled ordinary network reseed,
started fresh managed i2pd state, and completed derived-key SSH login over I2P. At the
end of the final 2026-10-19 proof, i2pd retained 645 RouterInfos: the 636 packaged records
plus nine learned through normal peer exchange after joining. This proves recovery from the
packaged corpus without claiming that the embedded RouterInfos remain static afterward.

Collection and release are separate operations:

1. `make status-i2p-bootstrap` reports the committed ledger and policy without scanning
   or changing either live router.
2. `make status-i2p-sources` applies the observer's exact positive-evidence and 24-hour
   recency rules without changing the ledger. Its per-root counts and evidence ages show
   whether the long-lived sources are still contributing.
3. `make observe-i2p-bootstrap` records at most one day from both configured mature roots.
4. Once identities qualify, `make curate-i2p-bootstrap` stages every currently
   corroborated identity meeting the policy and writes a complete diff.
5. A human reviews `bootstrap/i2p.next` and `artifacts/i2p-bootstrap.diff`.
6. `make promote-i2p-bootstrap` validates and replaces the reviewed release corpus.
7. `make check-i2p-bootstrap` and `make live-i2p-fresh` validate integrity and
   reseed-disabled product login.

Repeated observation on the same UTC day is safe but cannot advance longevity. Missing
an observation day does not erase history. RouterInfo age remains diagnostic because a
long-lived identity can publish changed addresses; i2pd signature/age checks and normal
certificate-verified reseeding remain authoritative at runtime.
