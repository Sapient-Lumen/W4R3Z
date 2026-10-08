# Changelog

## rev0004 — 2026.03.08.01.18 — resiliouimirrorkeepingwatch

Made UI and Resilio comparison discipline first-class parts of the archive.

Added:
- a fifth numbered decision for UI posture and recurring Resilio research practice
- architecture note for a shared local-web UI surface across desktop, NAS, and mobile packaging
- research note summarizing current Resilio main-view, share-dialog, preferences, mobile, and change-log lessons
- Resilio research-watch runbook for future product-surface revisions
- new canonical link-registry entries for Resilio UI and change-log docs

Changed:
- project state now records the UI surface posture and the requirement for continuous Resilio behavior tracking
- must-read order now includes the new UI decision, architecture note, research note, and runbook
- roadmap and current brief now elevate shared UI IA to an immediate priority
- README now treats the UI surface as a first-class workstream

Notes:
- the repo now assumes one coherent product IA across desktop, NAS, and mobile packaging, even if exact frontend technology remains open
- future product-facing revisions should re-check current Resilio docs and change-log items before claiming alignment
- validation and context-pack generation were rerun after these updates

## rev0003 — 2026.03.08.00.58 — adaptiveprofilesbenchdiscovery

Extended the archive from product-default canon into performance and adaptation canon.

Added:
- a fourth numbered decision for performance profiles, local-state posture, and measured adaptation
- architecture note for profile-driven performance and bounded discovery adaptation
- research note covering Resilio, Syncthing, Tor, i2pd, SQLite, and BLAKE3 performance implications
- benchmark-plan runbook
- machine-readable config skeletons for resource profiles and discovery policy
- JSON Schemas for the new config skeletons

Changed:
- repository validation now schema-checks the new YAML config skeletons
- project state now records resource-profile and local-state defaults
- must-read order now includes the performance/adaptation decision
- roadmap now explicitly includes benchmark work and profile graduation

Notes:
- adaptation is treated as explicit profiles plus measurement, not vague auto-tuning
- exact piece size and final scheduler weights remain benchmark questions
- validation and context-pack generation were rerun after these updates

## rev0002 — 2026.03.08.00.22 — sealedbundleinvitebeaconmobile

Negotiated product defaults and turned them into canonical repo decisions.

Added:
- numbered decisions for bundled runtime posture, invite/LAN discovery semantics, and sync detection/mobile defaults
- research note aligning the archive more closely with Resilio's documented behavior
- runtime supervision runbook for bundled tor + bundled `i2pd`

Changed:
- project state now records bundled-runtime, invite-only, mobile, and change-detection defaults
- roadmap now assumes managed bundled runtimes rather than external-runtime-first as the main product path
- must-read order now includes the first settled decisions
- architecture notes now reflect bundled tor daemon first, bundled `i2pd`, and user-hidden transport internals

Notes:
- The product promise remains one sealed user-facing application, even though implementation may use supervised child processes internally.
- Arti remains a future migration path, not a present dependency.
- Validation and context-pack generation were rerun after these updates.

## rev0001 — 2026.03.07.23.07 — shadowmeshgreenrunbookbootstrap

Initial archive skeleton for AnonSync.

Added:
- top-level charter, roadmap, security, and contributing docs
- LLM/human continuity files (`AGENTS.md`, `MUST_READ_FIRST.md`)
- machine-readable metadata + JSON Schemas
- link registry
- validation, context-pack, service-check, and release scripts
- CI and Dependabot skeletons
- Rust workspace skeleton with core and CLI crates

Notes:
- Cargo was not available in the packaging environment used to assemble this archive, so Rust files were written but not compiled here.
- Python-based metadata and repository validation were executed locally for this archive.
