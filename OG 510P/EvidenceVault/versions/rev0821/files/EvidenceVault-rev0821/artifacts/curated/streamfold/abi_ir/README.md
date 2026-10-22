# StreamFold ABI IR (prototype)

This folder contains a **minimal ABI intermediate representation (IR)** for StreamFold.

Goals:

- **Human-reviewable:** small JSON files suitable for code review.
- **Machine-checkable:** tools can validate fixtures and (eventually) generate wrappers/gadgets.
- **Hash-stable:** the canonical IR bytes are hashed to an `abi_fpr` (ABI fingerprint).

## IR shape

An IR file is a JSON object with (at minimum):

- `abi_id` — a versioned ABI identifier string (e.g. `"sumcheck/abi:v1"`).
- `ir_version` — IR format version (integer).
- `codec_profile` — canonical encoding rules for semantic types (prototype).
- `schema` — an event-schedule specification (prototype: DFA over event signatures).

Optional (IR v2+):

- `ciphersuite` — a pinned transcript descriptor (e.g., hash function + framing + challenge rule) enabling deterministic re-derivation of challenge bytes.
- `bounds` — public transcript budgets (e.g., `max_steps`) used to bound cyclic schemas for worst-case ledger accounting.

Experimental (IR v3+):

- `schema.kind = "schedule-dsl-v1"` — a small schedule DSL that can express
  *commutative bag phases* without exploding the DFA state space. The prototype
  normalizer lives in `tools/streamfold_sdl.py` and is used by the paper's toy
  example `abi_ir/pcs_queries_toy_v3_sdl.json`.

The pinned JSON Schema for the experimental schedule DSL is now kept at the canonical top-level path `schemas/schedule_dsl_schema_v1.json`; this curated ABI directory carries a compact canonical-path index for that schema so the normalization contract stays reviewable without shipping a second exact mirror. A tiny validator lives in `tools/streamfold_ir_validate.py`.

### Event signature

An **event signature** is the triple:

- `op` ∈ {`absorb`, `challenge`, `absorb_digest`}
- `tag` — a domain-separation label string
- `type` — a semantic type name (or a bytes type)

### Schema: DFA

In this prototype, `schema.kind = "dfa"` and the automaton is described by:

- `start` — start state (integer)
- `accept` — list of accepting states
- `edges` — list of edges `{from,to,sig}`

Where `sig` is an event signature object `{op,tag,type}`.

### Guards (`requires`) on challenge edges

For implementation-flexible schedules, a challenge edge may additionally carry
`requires: ["tag1", "tag2", ...]`, interpreted under guarded semantics:
the required tags must have been observed (via `absorb`/`absorb_digest`) since
the previous challenge (or start). This expresses common barriers like
"observe all opened values before sampling batching coefficients" without
enumerating every possible ordering in the DFA.

`absorb_digest` is intended for boundaries where a caller commits to an already-hashed payload
(e.g., a module-level transcript digest). JSONL fixtures represent this with a `digest: "0x..."` field.

## Tooling

See `tools/streamfold_abi_ir.py`:

- `digest` — compute a domain-separated hash of canonical IR JSON bytes.
- `validate` — validate a JSONL fixture against an IR schema.
- `compat` — check backward compatibility between two IRs (schema inclusion + shared-type encoding equality) and output a shortest witness trace on failure.
- `rename` — apply a tag prefix to an IR (namespacing helper for composition).
- `compose` — sequentially compose two DFA-schema IR modules into a single IR.

See `tools/streamfold_cert.py`:

- `make` — build a toy compatibility certificate (IR digest + fixture digests + cert digest).

**Important:** canonical JSON here is *JCS-like* (sorted keys, no whitespace). It is not a full RFC 8785 implementation; for production, plug in a strict JCS library and restrict the IR to a JSON subset without floats.
