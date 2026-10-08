# CLI Surface Contract Kit — lane boundaries (2026-03-21)

**P-0531** is about the receiver-facing support contract for command-line interfaces and command-line tools.

It answers questions like:

- What command surface is actually being promised?
- Which output mode is for humans and which is for automation?
- What changes when stdout/stderr are not terminals?
- Where do progress, prompts, and diagnostics go?
- What does each exit outcome mean?

## It is not:

### Not `crate-example-surface-pack-kit`
That lane is about official quickstarts, first-success witnesses, docs linkage, and example normalization.
**P-0531** is about the CLI contract itself once a tool is already being run.

### Not `crate-test-surface-pack-kit`
That lane is about fixture support, fake backends, isolation, reset posture, and scenario corpora.
**P-0531** uses testing substrate, but it is about what behavior a CLI publishes as contract, not how tests are arranged.

### Not `crate-guidance-pack-kit`
That lane is about diagnostics, recovery recipes, message stability, and guidance channels.
**P-0531** is broader and more operational: output modes, TTY posture, stream ownership, and exit semantics.

### Not `crate-diagnosis-surface-pack-kit`
That lane is about self-checks, symptom catalogs, probes, and support bundles.
**P-0531** is about ordinary command behavior, even when no diagnosis command exists.

### Not a TUI framework
Ratatui/crossterm/full-screen interaction work can consume these receipts, but **P-0531** does not define widget trees, rendering loops, or alternate-screen behavior.

### Not another parser crate
`clap`, `bpaf`, `pico-args`, and others already cover parser ergonomics.
**P-0531** publishes the support contract above those parser choices.

### Not another snapshot-test harness
`trycmd`, `snapbox`, `assert_cmd`, and related tools already verify CLI output.
**P-0531** defines which tested surfaces another team may rely on.
