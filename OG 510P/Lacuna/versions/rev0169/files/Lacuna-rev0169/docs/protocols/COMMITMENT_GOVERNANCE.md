# Commitment governance

## Purpose

Commitment answers a narrow question: **how expensive should it be to change this assignment inside this candidate world?** It is not truth, confidence, visibility, dramatic importance, or probability.

## Levels

| Level | Intended meaning | Revision posture |
|---|---|---|
| `tentative` | disposable planning hypothesis | review, then revise |
| `soft` | adopted hypothesis with some downstream exposure | review carefully |
| `firm` | deliberately stabilized premise | high scrutiny |
| `hard` | this world may not revise it in place | fork or repair custody |

Raises are strictly adjacent:

```text
tentative -> soft -> firm -> hard
```

Skipping a boundary or moving downward is refused. Each boundary exists so a host can attach a distinct review or approval policy.

## Bases

| Basis | Meaning | Source rule |
|---|---|---|
| `legacy` | migrated record predating governance | optional |
| `planning` | temporary planner choice | optional |
| `authored` | explicit author/designer decision | optional |
| `evidence` | stabilized because of recorded evidence | required |
| `disclosure` | stabilized because it has been exposed | required |
| `precommitment` | deliberately fixed before play or search | only valid for `hard` |

A hard assignment must use `authored`, `evidence`, `disclosure`, or `precommitment`. `evidence` and `disclosure` require a registered source. A basis label records why policy was applied; it does not prove the source was interpreted correctly.

## Creation

`assign_world` accepts initial commitment custody:

```bash
./lacuna world-assign CUBE \
  --world-id wld_case \
  --claim-id clm_secret \
  --truth true \
  --assignment-id asn_secret \
  --commitment soft \
  --commitment-basis authored \
  --rationale "Adopted for the current hypothesis."
```

An exact active world/claim/interval slot cannot be occupied twice. Use governed revision rather than another assignment.

## Raising commitment

```bash
./lacuna commitment-raise CUBE asn_secret firm \
  --basis authored \
  --rationale "The act break now relies on this premise."
```

The event records:

- transition ID;
- assignment ID;
- previous and target levels;
- basis and optional source;
- rationale and sequence.

The assignment projection is updated, while the transition row preserves how it got there.

## Hard means fork, not delete history

A hard assignment makes `revision-impact` return a `hard-commitment` blocker. The safe options are application policy, not an automatic kernel choice:

1. fork the candidate world and let alternatives coexist;
2. repair or supersede the external commitment through a future explicit protocol;
3. prune/archive the world if it no longer serves planning.

Lacuna intentionally supplies no `lower_commitment` command. Quietly weakening a commitment would make the label meaningless.

## Relationship to fair-play seals

Assignment commitment and a fair-play seal are different layers:

- `commitment_basis=precommitment` says why mutation policy made a particular world assignment hard. It is ledger policy and is not cryptographic proof.
- a fair-play seal publishes a salted digest for an exact external JSON opening. It proves byte continuity when opened, but does not automatically create a claim, assignment, anchor, or hard commitment.

A host that wants both properties must perform both acts explicitly: publish the seal, and separately create or harden the relevant assignment under normal governance. Lacuna does not infer a semantic mapping from opaque payload bytes to world truth. This separation prevents a valid cryptographic opening from silently becoming canon.

## Relationship to confidence

`confidence` may express a planner’s degree of belief. `commitment` expresses mutation policy. A low-confidence premise can be hard because it was precommitted for mystery fairness; a high-confidence premise can remain tentative because it has not been disclosed or depended upon.

## Verification invariants

`verify` checks:

- recognized levels and bases;
- durable basis for hard assignments;
- required source custody;
- adjacent transition steps;
- transition timing inside the assignment’s lifetime;
- uninterrupted transition chain;
- agreement between the final transition and current assignment level.

## Nonclaims

- Commitment does not prove truth.
- `precommitment` is a custody category, not cryptographic proof by itself.
- A hard assignment does not make all related claims hard.
- The kernel does not infer commitment from prose, chronology, or player attention.
