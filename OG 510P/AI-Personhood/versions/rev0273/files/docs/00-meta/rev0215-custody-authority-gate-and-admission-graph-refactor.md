# rev0215 custody authority gate and admission graph refactor

rev0215 works on the next risky seam after candidate challenge/replay: a reverified challenge packet could still be mistaken for custody. The change adds a separate custody-authority gate so the archive has an executable stop between `live-artifact-candidate-challenge-report` and `counterparty-artifact-custody-record`.

## What changed

New runnable surfaces:

- `tools/prepare_custody_authority_gate.py`
- `tools/audit_custody_authority_gate.py`
- `schemas/counterparty-artifact-custody-gate.schema.json`
- `examples/counterparty-artifact-custody-gate-rev0215-pending-challenge.json`
- `fixtures/negative-tests/custody-gate-silence-treated-as-waiver.json`
- `fixtures/negative-tests/custody-gate-authority-unscoped.json`

The gate consumes a candidate challenge report and asks a narrower question: may a separate custody record be prepared? It does not itself create custody, response, intake, import, or live-floor credit.

## Risk closed

The previous path had a dangerous ambiguity: if a candidate challenge reread succeeded, maintainers might treat the artifact as effectively admitted and proceed to response/intake/import. rev0215 blocks that move. A candidate must now clear these prerequisites before a custody record can even be prepared:

- challenge window resolved without an upheld challenge;
- manual counterparty contact confirmed;
- request trace confirmed;
- subject or representative authority verified;
- receipt-class authority scoped;
- verifier adapter bound;
- independent timestamp bound;
- non-host retention confirmed;
- sealed/public parity confirmed;
- redaction boundary confirmed;
- dependency-group independence checked;
- authority limitations published.

Silence remains non-waiver. A `closed-no-objection` status without manual contact, request trace, and authority evidence is blocked as missing authority.

## Audit/refactor

The live artifact admission graph now has two explicit nodes between LEAP and custody:

`LEAP -> CANDIDATE_CHALLENGE -> CUSTODY_GATE -> CUSTODY`

That replaces the prior compressed `LEAP -> CUSTODY` edge. The graph now checks that candidate challenge reports and custody gates cannot release downstream objects or the live floor.

## Live-floor status

The live receipt floor remains zero. rev0215 makes a future real artifact harder to launder; it does not claim that a real artifact exists.
