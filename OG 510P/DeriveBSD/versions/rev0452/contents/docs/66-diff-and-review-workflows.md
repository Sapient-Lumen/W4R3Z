# Diff and review workflows (LLM-friendly)

To avoid “Nix monster drift”, every change must be reviewable as a small diff.

## Key commands (design)
- `derive diff plan A B --json`
- `derive diff system genX genY --json`
- `derive diff --blast-radius plan A B --json`
- `derive explain <artifact|instance> --json`

## Output requirements
- stable schemas (docs/38)
- minimal change sets:
  - what changes
  - why it changes (dependency edge)
  - policy decision deltas
  - authority deltas (blast radius; see `docs/106-blast-radius-diff.md`)

## LLM workflow
- generate candidate patch
- run `derive validate`
- produce diff + explanation
- optionally produce a repro capsule if something fails

See RFC-0042.
Last updated: 2026-02-23

## LLM-facing protocol pointer

See `docs/81-llm-facing-interfaces.md` for the least-privilege “patch loop” protocol.
