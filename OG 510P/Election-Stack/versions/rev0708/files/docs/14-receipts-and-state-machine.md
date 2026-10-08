# Receipts & state machine (normative)

**Track:** A (Deployable core)


Receipts are security-critical UX. A voter must never be misled into thinking a ballot is counted when it is not.

## Receipt states
A client MUST display one of the following states:

1) **PENDING (IntakeReceipt only)**  
   The system accepted a submission for processing, but it is **not** yet in the public log.  
   Evidence: `IntakeReceipt` signature(s) over ballot hash + deadline.

2) **RECORDED (Inclusion proof)**  
   The ballot appears as a leaf in the log and the client has an inclusion proof against an STH.  
   Evidence: `LogEntry`, `InclusionProof`, `STH`.

3) **FINAL (Quorum checkpoint)**  
   The ballot is included in a log state that is quorum-witness-cosigned (or BFT-finalized).  
   Evidence: inclusion proof against `Checkpoint = STH + WitnessCosignatures`.

4) **TALLIED**  
   Public tally artifacts prove either:
   - the ballot contributed to the tally, or
   - it was excluded by a published rule (e.g., revoting / last-vote), with evidence.

5) **AUDITED (paper mode)**  
   Paper audit evidence is consistent with the cryptographic record.

## Non-lying invariant (MUST)

**Only `RECORDED` (or higher) means “in the public record.”**

- `PENDING` means “accepted for processing” **only**.
- If the client cannot prove inclusion, it MUST NOT display synonyms like **confirmed / counted / recorded / accepted**.
- Anything below `RECORDED` MUST be presented as **NOT RECORDED** (optionally with a short-lived `PENDING` pre-state and an explicit deadline).

Recommended UI phrasing (conservative):

| State | Minimum evidence | Allowed user-facing phrase |
|---|---|---|
| PENDING | `IntakeReceipt` | "Submitted (not yet recorded)" |
| RECORDED | inclusion proof vs STH | "Recorded in public log" |
| FINAL | quorum checkpoint | "Finalized (witnessed)" |
| TALLIED | tally artifact proof | "Included in tally" |
| AUDITED | audit evidence | "Audit consistent" |

## Time bounds (MUST)
- If the client cannot obtain an inclusion proof within `T_inclusion`, it MUST display **NOT RECORDED** and present fallback.
- If the client cannot obtain a quorum checkpoint within `T_final`, it MUST display **RECORDED BUT NOT FINAL**.

## Failure messaging (MUST)
Clients MUST expose:
- whether failure is **local** (device/network) vs **global** (witnesses disagree / no checkpoints),
- recommended fallback (paper/in-person/supervised kiosk),
- how to preserve evidence (save receipt bundle; optionally publish to an evidence portal).

## Receipt bundle format (recommended)
A portable “receipt bundle” SHOULD include:
- canonical ballot ciphertext hash (not plaintext vote)
- log index
- checkpoint (STH + witness cosigns)
- inclusion proof
- verifier version info