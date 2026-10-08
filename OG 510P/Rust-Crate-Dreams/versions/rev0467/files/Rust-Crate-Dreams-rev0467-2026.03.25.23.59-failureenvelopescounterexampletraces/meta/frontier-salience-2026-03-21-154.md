# Frontier salience snapshot — 2026-03-21-154

This pass did **not** add another crash collector, another hosted dashboard, or another debugger UI.
It deepened **P-0101 Crash Artifact & Symbolication Workbench Kit**.

## Why this frontier moved up

The current substrate now makes the missing layer much sharper:

- `rust-minidump` provides parsing and analysis for minidump artifacts, but not one shared support contract;
- `minidump-stackwalk` now exposes symbol stats, soft errors, direct symbol-file inputs, native-debuginfo routes, and server-backed symbol lookup;
- `wholesym` now makes native debug-info and symbol-server lookup across Windows, macOS, and Linux concrete;
- `symbolic` remains strong multi-format symbolication substrate;
- `minidumper` and `minidump-writer` make external-monitor capture and capture-side posture concrete;
- Mozilla’s deployment/fuzzing lessons show that reliability and artifact discipline matter as much as parsing.

That combination means “we have crash reporting” is now too vague as a crate claim.
A worthy crate in this frontier should publish at least:

1. **capture basis** truth,
2. **module identity** truth,
3. **symbol route** truth,
4. **analysis coverage** truth,
5. **report determinism** truth,
6. **share-safety** truth.

## Main conclusion

Promote **P-0101** again, but keep it narrow.
The sharper next move is not another stackwalker and not another SaaS wrapper.
It is a boring contract that keeps **capture**, **identity**, **symbol route**, **coverage**, **replayability**, and **share-safety** separately reviewable.

## Ranked near-term frontier from this pass

1. **P-0101 Crash Artifact & Symbolication Workbench Kit** — strengthened because the substrate is real but the contract layer is still missing.
2. **P-0256 Evidence Bundle Core Kit** — remains strong because crash bundles want shared, portable bundle substrate.
3. **P-0073 Async Replay Debugger Kit** — remains adjacent because crash incidents often need replay follow-on without conflating postmortem artifacts with schedule replay.
4. **P-0083 Debugger UX** — remains adjacent because crash bundles are not live-debugger support.
5. **P-0012 Desktop Shipkit** — remains adjacent because shipping crash collection is not the same as making crash artifacts reviewable.

## Keep these boundaries sharp

- **P-0101** is capture + module identity + symbol route + coverage + report determinism + share-safety.
- hosted crash services are separate.
- live debugger/visualizer work is separate.
- generic evidence-bundle substrate is separate.
- async replay/debugging is separate.

Do not let “crash reporting support” flatten those into one fake crate.
