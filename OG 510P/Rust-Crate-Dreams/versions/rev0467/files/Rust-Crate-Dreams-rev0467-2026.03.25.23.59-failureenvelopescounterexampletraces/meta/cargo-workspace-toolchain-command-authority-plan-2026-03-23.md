# Cargo Workspace Toolchain Manifest Kit — command-authority plan (2026-03-23)

This note sharpens the next implementation step for **P-0055**.

## Main judgment

The next `0.2`-quality surface should make three additional truths boring to export:

1. **what command family answered the request**,
2. **what optional component/toolchain surface was actually checked**,
3. **what strongest support claim still survives after fallback is considered**.

## New receiver-facing artifacts worth shipping

- `command-authority.receipt.json`
- `component-availability.report.json`
- `fallback-ceiling.report.json`
- `tool-support-bundle.manifest.json`

## What each artifact should do

### `command-authority.receipt.json`
Record:
- requested command,
- authority class (`rustup_component_proxy`, `cargo_external_subcommand`, `workspace_managed_bin`, `path_fallback`, etc.),
- resolution route,
- source of the claim,
- whether the result is component-backed, subcommand-backed, workspace-backed, or fallback-only.

### `component-availability.report.json`
Record:
- expected component name if relevant,
- active toolchain context,
- whether the component was installed, merely available, missing, or not applicable,
- what check basis produced that answer,
- and what fallback policy the workspace declared.

### `fallback-ceiling.report.json`
Record:
- the strongest honest outward-facing claim,
- route observed,
- whether component parity is proven,
- and why stronger claims stop.

### `tool-support-bundle.manifest.json`
Bundle the above with existing `install-root.receipt` / `tool-route.receipt` / `tool-run.receipt` objects without flattening them.

## What the crate should provide other people

A good implementation should let another person answer these support questions without re-running the machine setup:

- “Was this tool request actually satisfied by a rustup component?”
- “Did a cargo-home or PATH binary win instead?”
- “Which toolchain context did we really check for optional components?”
- “Can I claim workspace-governed support here, or only that some compatible binary happened to run?”

## Scope guardrails

Keep separate:
- install-root posture,
- command authority,
- component availability,
- actual run receipt,
- and fallback claim ceiling.

A crate that only installs tools or only shells out to one binary still sits below the missing support layer.
