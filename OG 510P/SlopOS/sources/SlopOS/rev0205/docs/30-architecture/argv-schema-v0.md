# CH-ARGV v0: capability-bound argv token list (schema)

Purpose: eliminate ambient authority in workflow automation by representing command-line inputs as a **typed token list** that can bind to already-held capabilities/leases/portal handles.

CH-ARGV is designed for D-CAPSHELL:
- **LLMs propose** a `capshell.exec` action carrying `exec_pack_digest = digest(CH-EXECPACK v2)`; the referenced pack binds `argv_digest = digest(CH-ARGV v0)`.
- deterministic validators/runners **execute** only after validating the token list and binding referenced descriptors to already-held handles.

CH-ARGV is **non-authoritative**:
- it MUST NOT contain bearer secrets or raw capability material,
- it MUST NOT be interpreted as a “permission grant,”
- and any binding from the token list to real handles MUST be checked against already-held authority (e.g., a bound CH-WALLET core digest).

References: REF-SHILL-OSDI14, REF-PLASH, REF-ROBUST-COMPOSITION.

## Encoding
Candidate baseline: canonical CBOR (D-ENC).
Decoders MUST reject non-canonical encodings (I-ENC-1; PO-ENC-DECODE).

## Design constraints (v0)
- total decoding + fail-closed validation
- bounded sizes and closed enums
- **no bearer secrets** and **no raw capabilities**
- no ambient-authority surrogates (host paths, environment variables, implicit network names) as “permission grants”
- hashable and stable for binding into CH-ACP / transcripts / receipts

## Data model (conceptual)

CH-ARGV v0 := {
  v: 0,

  argv: [ Arg ],

  ; Optional binding hints. These are non-authoritative and MUST NOT change
  ; validator meaning; they exist for UX/debugging only.
  note?: tstr,
  meta?: { * tstr => any }
}

Arg :=
  ; literal token (flags, subcommands, small identifiers). Literal tokens are
  ; treated as **data only** and MUST NOT be used by the runner to acquire
  ; authority from ambient namespaces.
  { kind: "lit", s: tstr }

| ; typed descriptor reference (digest only). The runner binds the referenced
  ; descriptor to an already-held handle (e.g., from a wallet inventory or
  ; explicit handle passing) and passes the resulting handle to the child
  ; process by a profile-defined mechanism.
  { kind: "desc",
    desc_schema: tstr,   ; allowlisted descriptor schema (closed-world; must be permitted by the bound CH-EFFCON v0 effects; e.g., "CH-DOCREF v0")
    desc_digest: bstr,   ; digest of canonical bytes of the descriptor
    role?: tstr          ; closed enum: "arg" | "read" | "write" | "exec"
  }

### Roles (v0; closed)
Unknown roles MUST be rejected.

- `arg` — descriptor is passed as an argument token (profile-defined formatting)
- `read` / `write` — intent hints for open mode; enforcement is by the bound handle rights, not by this field
- `exec` — descriptor identifies the executable artifact (profile-defined)

Executable binding (D-CAPSHELL strict):
- For `capshell.exec`, the runner MUST select the executable artifact **only** from a `desc` token with `role="exec"`.
- The runner MUST NOT resolve an executable from `lit` tokens or an **ambient PATH** (or any other ambient namespace).
- Validators MUST require **exactly one** `role="exec"` token per execution; missing or multiple selectors MUST fail closed and be transcript-visible.

See: `capshell-exec-selector-posture-v0.md`.

Note: stdio binding is modeled separately by **CH-STDIO v0** (`stdio-schema-v0.md`).
## Validation rules (minimum)

An argv validator MUST be total and fail closed (PO-ARGV-VALIDATE):
1) `v == 0`.
2) `argv` is non-empty and bounded.
3) Each Arg has `kind` in the closed enum.
4) For `lit` args: `s` is bounded.
5) For `desc` args:
   - `desc_schema` is allowlisted (closed-world) and is permitted by the bound CH-EFFCON v0 effect list (see CH-EFFCON “Workflow-bound descriptor allowlist”); profiles may further restrict (subset),
   - `desc_digest` length matches profile hash,
   - `role` (if present) is in the closed enum.
6) Unknown keys reject (or are rejected by canonical CBOR decode).

## Binding semantics (capshell runner)

CH-ARGV is a **veto-only** structure:
- It never grants authority (I-ARGV-1).
- Runners MUST NOT interpret `lit` tokens as authority acquisition instructions.

When `capshell.exec` (via CH-EXECPACK) binds `argv_digest`:
- The runner MUST check that every `desc` reference corresponds to already-held authority in the bound wallet/handle inventory for the execution context.
- The runner MUST also check that each `desc_schema` is permitted by the bound CH-EFFCON `effects[*].kind` list (see CH-EFFCON “Workflow-bound descriptor allowlist”). Any mismatch MUST fail closed and SHOULD emit CH-DENY `deny_code = effcon-violation` bound to `reason.ref_digest = effcon_digest`.
- The runner MUST NOT resolve an executable from `lit` tokens or an ambient PATH; the executable MUST be bound from exactly one `desc` token with `role="exec"`.
- If any `desc` reference is unknown/unavailable/unbindable, execution MUST fail closed and be transcript-visible (I-ARGV-2; PO-CAPSHELL-ARGV-BIND).
- Rejects SHOULD emit CH-DENY with deny_code `argv-bind-failed`, binding `reason.kind="schema"`, `reason.ref_schema="CH-ARGV v0"`, and `reason.ref_digest=argv_digest`.

Notes:
- The mechanism for passing bound handles to children is profile-defined (FD passing, handle tables, view binding, etc.), but the validation and “no ambient acquisition” rule is invariant.
- Environment variables are modeled separately by **CH-ENV v0** (`env-schema-v0.md`), so the runner can avoid inheriting ambient environments and keep env binding receipt-shaped.
- The child working directory is modeled separately by **CH-CWD v0** (`cwd-schema-v0.md`), so the runner never inherits an ambient host cwd and can bind a directory handle explicitly.
- Process stdio bindings are modeled separately by **CH-STDIO v0** (`stdio-schema-v0.md`), so the runner never inherits ambient host stdio/TTY state and all stream bindings are explicit.
- Extra child handles beyond stdio are modeled separately by **CH-FDSET v0** (`fdset-schema-v0.md`), so the runner never inherits an ambient host handle/FD table.
- Secrets should not be carried as literal strings in argv/env. Prefer portal-mediated secret descriptors (e.g., CH-APPSECRET) and bind them as descriptor references.
