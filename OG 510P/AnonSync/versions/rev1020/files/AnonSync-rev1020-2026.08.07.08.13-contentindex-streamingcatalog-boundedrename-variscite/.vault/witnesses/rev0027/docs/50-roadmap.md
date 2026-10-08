# Roadmap

## Phase 0 — narrow the core

Deliver:

- daemon skeleton
- local identity creation
- share/index model
- local status, event stream, and audit surface
- CLI contract draft
- daemon API contract draft
- canonical interface flows
- recovery object model
- plan/apply object model
- incoming/adoption object model
- capability introspection surface
- ignore/conflict object model
- role/preflight object model
- claim object model
- recovery-bundle object model
- approval-memory object model
- path-comparison and relocate object model
- topology-exposure object model
- publication-profile, known-host-record, and route-lease object model
- contact-record, pending-peer, and introduction-policy object model
- decision-trace object model
- retirement-record object model
- filesystem-profile and filesystem-compatibility-report object model
- projection-policy object model
- convergence-report object model
- transport-runtime object model
- transport-session object model
- Linux-first filesystem support-tier model
- critical-open-questions discipline

Exit criteria:

- objects and state model feel stable
- command names survive scrutiny
- event taxonomy is good enough for future UI/TUI work
- high-signal mutations can be previewed without inventing hidden side effects

## Phase 1 — trusted plaintext sync

Deliver:

- device add/link
- share create/grant
- full replication
- send-only / receive-only behavior
- explicit deviation-policy object and deviation-aware status/explain surfaces
- useful `status`, `doctor`, and `audit`
- named discovery / topology policies
- Tor/I2P-aware mixed transport policies with manual clearnet-direct lease semantics
- exposure-preview and effective-route-exposure surfaces
- peer-pinned known-host direct admission without ambient public-direct enablement
- byte-capped direct-speed leases for trusted bulk windows
- bundled transport provenance/verification surfaces
- explicit transport-session inspection surfaces
- basic provenance on policy and grant creation
- incoming-share visibility and adopt/reject flow
- ignore-rule and drift surface
- projection-policy and projection-test surface
- compatibility warnings and least-privilege role application for link/grant/adopt flows
- explicit claim handling for invite and incoming-share acceptance
- explicit device-retire / ignore / revoke surfaces
- scoped approval-memory and delegated-approver surfaces
- explicit pending-peer and contact-review surfaces
- bounded introduction-policy surfaces for trusted constellations
- stewardship records and handoff previews for trusted shares
- compare-before-bind and relocate-plan surfaces for populated-path adoption
- override-lease and effective-state surfaces for maintenance, drain, and temporary throttling
- filesystem preflight / explain / doctor surfaces for pathname and metadata safety
- filesystem support-tier inspection surfaces
- convergence-report and wait-for-settlement surfaces for cutover / backup / relocate readiness

Exit criteria:

- personal two-device workflow is reliable
- failures are debuggable from CLI alone
- LAN-only and trusted-WAN policies both work cleanly
- overlay-first WAN policies work cleanly without silent clearnet-direct fallback
- operators can see the difference between warm transport runtimes and active transport sessions
- operators can tell which profile or plan created the current defaults
- operators can answer what a policy publishes about reachability and whether fallback would widen metadata exposure
- operators can admit one trusted direct path without silently enabling public direct for everything else
- operators can see when a temporary speed window will expire by time or by byte budget
- operators can explain why a chosen route or approval outcome won without leaving the CLI
- operators can safely adopt into a pre-populated directory without guessing what will win
- operators can tell whether current behavior comes from durable policy or a temporary override lease, and when that lease expires
- a small-team share can be handed off to a successor without re-sharing the whole dataset or widening everyone into owner-equivalent authority
- operators can distinguish ordinary idle status from settlement confidence degraded by missing sources, watcher fallback, clock skew, or hidden background work

## Phase 2 — selective materialization

Deliver:

- detached/selective/full mount modes
- metadata-only index view
- explicit fetch/evict/pin commands
- explicit local-vs-share removal scopes
- preservation-report surface for risky file actions
- file-history listing and local/share restore surface
- conflict listing and safe resolution surface
- transfer explanations
- capability-aware placeholder strategy selection
- per-device role outcomes that remain legible after selective-materialization adoption
- explicit mount-relocate workflows with compared path binding
- explicit fs-compatibility reports for adopt / relocate / restore workflows

Exit criteria:

- users can keep large shares visible without replicating everything
- selective mode is operationally legible
- unsupported placeholder strategies fail or degrade explicitly
- operators can always tell whether an action affected local materialization or shared state
- operators can see whether a destructive action still leaves any plaintext or history-backed rollback path
- operators can restore an earlier copy without hunting hidden archive directories
- operators can tell whether a path is suppressed share-wide, omitted locally, or still visible as placeholder/metadata-only state
- operators can resolve conflicts, deviation state, and rule drift without editing hidden control files
- operators can relocate a mount or rebind a path without falling back to remove/re-add folklore
- operators can see case, normalization, symlink, and metadata-fidelity risk before binding a share onto a real path

## Phase 3 — encrypted-untrusted replicas

Deliver:

- encrypted-replica permission
- ciphertext-only peer behavior
- trusted-peer recovery via encrypted intermediary
- diagnostics for plaintext availability
- polished Tor/I2P transport health, session reuse, and bootstrap ergonomics on Linux

Exit criteria:

- “store on untrusted node, recover from trusted node” works cleanly

## Phase 4 — recovery and replacement workflows

Deliver:

- backup/export/import
- replacement-device onboarding
- identity rotation and revocation
- trust-graph reconciliation tooling
- policy provenance for auto-grants
- reviewed plan/apply for replacement and rebind work
- offline encrypted-replica recovery tooling
- recovery-bundle export and verification
- successor-binding and retirement-record workflows

Exit criteria:

- operators no longer need unsupported clone-style workarounds
- dead-device replacement is explicit and understandable
- stolen-device retirement is visibly different from mere list cleanup
- linked-device convenience remains auditable after recovery events
- successor carry-forward of grants and approvals remains reviewable rather than ambient
- route, exposure, and metrics surfaces are good enough for local dashboards and troubleshooting

## Phase 5 — optional richer surfaces

Possible next work:

- TUI
- local web UI
- FUSE/virtual mounts
- later Windows/macOS work only after Linux-first semantics are genuinely stable; no v1 parity promise
- platform-specific placeholder support
- private relay/discovery helpers

## What to avoid during roadmap execution

- copying every Resilio workflow before the core model is proven
- adding GUI sugar before state/diagnostics are solid
- turning the project into a generic storage platform
- hiding network policy in “advanced settings”
- merging linking and granting until trust boundaries become fuzzy
