# Unlink and hidden-device boundary page: local unlink, remote non-unlink, and offline residue interface spec

## Purpose

This review appears whenever an operator tries to clean up or detach a linked seat rather than adopt it.
The review exists to answer one ordinary question before commit:

> is this seat really being detached, or am I only hiding one local view while latent linked membership survives elsewhere?

## When this review must appear

Trigger this review for changes such as:

- unlink this seat from identity
- hide / clear offline linked seat
- remove dormant seat from roster
- claim that a seat is gone because it vanished locally

## Fixed page order

1. boundary summary header
2. local effect vs remote effect matrix
3. residue and reappearance examples
4. follow-up actions rail
5. approval footer

### 1) Boundary summary header

Show:

- target seat
- requested verb (`hide`, `unlink-local`, `revoke-remote`, `forget-history`, `unknown`)
- strongest safe sentence after apply
- stronger rejected sentence after apply

### 2) Local effect vs remote effect matrix

Columns:

- effect plane
- local result
- remote result
- later reappearance possible?
- proof freshness

Rows should include at least:

- roster visibility
- seat linkage
- ordinary subject continuity
- ability to reappear later
- required further cleanup

### 3) Residue and reappearance examples

Provide concrete examples in plain language:

- `This hides the seat from this roster only.`
- `The dormant seat can reappear if it returns online.`
- `This detaches only the current seat; other linked seats remain untouched.`

### 4) Follow-up actions rail

Show:

- `Open remote revocation path` if available
- `Emit residue receipt`
- `Review latent member watch`
- `Open identity merge contract`

### 5) Approval footer

Require acknowledgement whenever the change creates a state such as:

- hidden but still linked
- local unlink with surviving remote continuity
- latent member residue
- unknown final detach status

## Rules

### Rule 1 — hide, unlink, revoke, and forget stay separate verbs

The operator must never have to infer which one happened.

### Rule 2 — reappearance potential must be visible before commit

Hidden is not harmless if it can quietly come back.

### Rule 3 — local-only detach must block remote-finality language

The product cannot say the seat is gone everywhere when it is not.
