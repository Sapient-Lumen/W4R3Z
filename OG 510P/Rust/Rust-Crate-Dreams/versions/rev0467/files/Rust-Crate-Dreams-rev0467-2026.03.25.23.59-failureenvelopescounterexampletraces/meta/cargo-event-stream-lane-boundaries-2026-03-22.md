# Cargo event-stream lane boundaries — 2026-03-22

When future revisions touch **P-0042 cargo-event-stream**, keep these lanes separate.

## The six truths that must not be collapsed

1. **native Cargo/rustc events** — messages that Cargo intentionally emits in structured form.
2. **foreign output** — build-script, proc-macro, runner, or arbitrary tool text that can contaminate the stream.
3. **rendering policy** — whether diagnostics were embedded, ANSI-rendered, or Cargo-rendered.
4. **session identity** — which command, workspace lane, profile, target posture, and toolchain produced the stream.
5. **historical warehouse** — durable multi-run storage and trend adjudication.
6. **replay container** — append-only output/event archives meant for rerun or postmortem analysis.

## Do not let these stand in for an honest answer

- “we parse `cargo_metadata::Message`,”
- “the stream was mostly JSON,”
- “we kept lines starting with `{`,”
- “Cargo now has structured logging work,”
- or “we saved the raw stdout log.”

A tool can have all of those truths and still leave foreign-output containment, rendering policy, session provenance, or export safety unresolved.

## Adjacent proposals that must remain distinct

- **P-0035 cargo-build-insights** — historical session import and trend adjudication.
- **P-0469 Cargo Rebuild Explanation Kit** — why this build rebuilt.
- **P-0057 run-record-kit** — portable whole-run event/output replay containers.
- **P-0508 Cargo Build Script Delegation Kit** — unit topology, output-lane ownership, and override authority for delegated build work.

P-0042 should own the live event-handoff contract, not every build-analysis or replay story.
