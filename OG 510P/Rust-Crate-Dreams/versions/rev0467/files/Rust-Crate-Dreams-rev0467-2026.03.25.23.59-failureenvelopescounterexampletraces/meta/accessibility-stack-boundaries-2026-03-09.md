# Accessibility stack boundaries — 2026-03-09

This note exists to keep future passes from collapsing several different accessibility problems into one fuzzy “a11y crate” story.

## Main judgment

The archive should treat at least two distinct missing layers here:

1. **authoring / doctor / gating layer** — emitted semantics, rule evaluation, baseline diffs, and CI truth (**P-0087**),
2. **observer / capture / interop layer** — what AT-SPI2 / UIA / AX actually exposed, how event streams behaved, and what a repro bundle captured (**P-0202**).

Those layers can share vocabulary and even compare expected vs observed semantics.
They should **not** be merged into one vague proposal.

## What this means for P-0087

Read **P-0087 UI Accessibility Doctor Kit** as:

> semantic contract → doctor findings → baseline diff → release/CI gate result

This is the toolkit/app-facing side of accessibility quality.
It should stay **AccessKit-first** and should not quietly become a platform capture lab.

## What this means for P-0202

Read **P-0202 Accessibility Capture & Interop Lab** as:

> platform capture → normalized tree/event model → semantic diff → redacted repro bundle → capability/caveat report

This is the observer-facing side of accessibility truth.
It should not quietly become a lint/doctor tool for emitted widget trees.

## Working rule

When touching accessibility work in this archive, do **not** collapse:

- widget semantics emitted by a toolkit,
- release/CI gating policy,
- platform backend translation,
- observer-side capture,
- and legal/compliance claims

into one generic claim that “the accessibility crate handles it”.

Future passes should prefer:

- explicit expected-vs-observed comparisons,
- redaction-aware repro bundles,
- capability and caveat reporting,
- and clear boundaries between authoring-side semantics and platform-side exposure.

They should avoid:

- turning WCAG/ARIA into a fake automatic compliance oracle,
- proposing another GUI framework when the sharper gap is diagnostics/capture,
- or assuming that a clean authoring-side semantic tree proves every backend exposes the same truth.
