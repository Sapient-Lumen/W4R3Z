# Roadmap

## Phase 0 — Skeleton archive and continuity
- establish top-level docs
- add schemas + machine-readable state
- add validation, context-pack, and release scripts
- create Rust workspace skeleton
- define architecture boundaries

## Phase 1 — Foundational design
- define trust model
- define peer identity and folder capability model
- draft sync metadata model
- draft transfer/session model
- define provider traits for I2P and Tor
- define invite-only sharing and LAN discovery semantics
- define resource profiles and benchmark matrix
- draft shared desktop/mobile UI information architecture

## Phase 2 — Managed bundled-runtime path
- bundled `i2pd` supervision model
- bundled tor-daemon supervision model
- internal config generation for child processes
- local discovery/service checks
- test harness and fixtures

## Phase 3 — Real sync engine
- manifests and chunking
- durable indexing and change detection
- placeholder model
- transfer scheduling
- resume/recovery
- conflict handling
- observability
- profile-aware throttling and adaptation

## Phase 4 — Product surface
- shared local-web UI shell across desktop, NAS, and mobile packaging
- desktop main view, folder detail, and history flows
- share dialog / invite flow with QR and permission posture
- mobile defaults and transport policy
- selective-sync ergonomics
- permission model stabilization
- runtime updates and integrity model
- profile selection and sane overrides

## Phase 5 — Future transport evolution
- Arti migration study
- advanced encrypted peer modes beyond encrypted sink
- deeper metadata-hiding work
- broader discovery studies only if invite posture remains intact

## Revision priorities right now

1. formalize the invite object and permission bundle
2. define LAN beacon rotation semantics
3. benchmark resource profiles and discovery backoff rules
4. specify supervised child-process runtime orchestration
5. draft the shared UI information architecture and first flows
6. define index + placeholder + rescan semantics
