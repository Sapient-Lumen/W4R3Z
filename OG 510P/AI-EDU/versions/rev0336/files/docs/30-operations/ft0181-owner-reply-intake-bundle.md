# FT-0181 owner reply intake bundle

## Purpose

This is the default local command path after a real owner returns the eight-row `AIEDU-SR-003`
CSV. It keeps receipt, triage, and the routed next artifact together in one scratch bundle so the
maintainer does not copy owner content into root docs, release records, examples, or a broad
workbench too early.

Use it after a real returned CSV exists. Do not use it for the SRC0 smoke fixture; use
`make owner-reply-smoke` for plumbing rehearsal.

## Command

```bash
make owner-field-next CSV=/path/to/returned-owner-reply.csv OUT=scratch/field/ft0181/ft0181-field-next-action/returned-owner-reply
```

Then execute only the emitted returned-reply work command. For ordinary first/reask replies it includes the active contact-status source gate:

```bash
make owner-returned-reply-work CSV=/path/to/returned-owner-reply.csv SOURCE_CONTACT_STATUS=scratch/.../contact-status.json
```

For post-readout new owner context, the router first emits `owner-post-readout-context-receipt`; then returned-reply work must use the context receipt instead of an old contact clock:

```bash
make owner-returned-reply-work CSV=/path/to/returned-owner-context.csv SOURCE_POST_READOUT_CONTEXT_RECEIPT=scratch/.../post-readout-context-receipt.json
```

Direct intake tool use still exists as a repair/debug path and has the same provenance requirement:

```bash
python3 tools/intake_owner_reply_csv.py /path/to/returned-owner-reply.csv --source-contact-status scratch/.../contact-status.json
python3 tools/intake_owner_reply_csv.py /path/to/returned-owner-context.csv --source-post-readout-context-receipt scratch/.../post-readout-context-receipt.json
```

If `OUT`/`--output-dir` is omitted, the tool writes under
`scratch/field/ft0181/owner-reply-intakes/<csv-stem>-<sha-prefix>/`.

## What the bundle writes

| Output | Contains | Must not be treated as |
|---|---|---|
| `receipt.json` | content-minimized fingerprint, row-presence metadata, triage outcome, and next action | raw owner content, `SRC2+` acceptance, closure evidence |
| `triage.json` | outcome, row status, reason count/reasons, and next action | proof of learning, safety, access, workload, compliance, scale, or effectiveness |
| `proceed-staged.md` | minimized surviving owner answers, only when triage is `PROCEED-STAGED` | archive evidence, public-summary support, or closure-ready content by itself |
| `outcome-note.md` | local block, re-ask, or no-packet routing note without copying owner answers | justification to widen the ask or add a registry |
| `bundle-manifest.json` | file hashes, source CSV fingerprint, triage outcome, next local artifact, content-minimization flags, and a `self_hash_policy` | release manifest, custody acceptance, self-certifying hash, or signoff |

## Output boundary

The bundle may be written to `scratch/` or an external local path. It refuses output to root and to
archive-controlled folders: `docs/`, `examples/`, `fixtures/`, `schemas/`, `templates/`, and `tools/`.

This is intentional. `proceed-staged.md` may contain minimized owner answers, so it stays local until
downstream custody and workbench gates decide what, if anything, can enter archive surfaces.

## Routing rule

- `PROCEED-STAGED`: `owner-returned-reply-work` creates the NOT_ACCEPTED workbench seed locally, then the human opens [`ft0181-owner-packet-workbench.md`](ft0181-owner-packet-workbench.md) and copies only minimized survivor rows from `proceed-staged.md` after confirming the source is real and still `NOT_ACCEPTED`.
- `RE-ASK-ONCE`: use `templates/ft0181-owner-reask-once-message.md` once; do not ask for a broader
  export.
- `BLOCK-*` or `NO-OWNER-PACKET`: use `outcome-note.md` locally and keep `FT-0181` live.

## Workbench seed

After `PROCEED-STAGED`, the preferred path is now `owner-returned-reply-work`, which calls the seed tool only for proceed-staged bundles. The direct [`ft0181-owner-reply-workbench-seed.md`](ft0181-owner-reply-workbench-seed.md) command remains a repair/debug path. The seed verifies bundle artifact hashes and revalidates exactly one provenance reference: either source contact-status or post-readout context receipt. It writes only local metadata with `acceptance_state: NOT_ACCEPTED`; it does not copy owner answers, contact details, raw CSV rows, or proceed-staged row text.

## Closure boundary

An intake bundle and workbench seed are not evidence acceptance. It does not upgrade source truth, close `FT-0181`, or
support public claims. It only prevents a real returned CSV from becoming scattered across multiple
surfaces before receipt, triage, staging, workbench seed, custody, acceptance, public-summary, lifecycle, signoff,
closeout, and closure gates have done their work.
