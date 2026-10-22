# WinnerIntentJoin V1 proof

## Subject

WinnerIntentJoin V1 is a finite C++20 relation at the provider-winner to retained-intent boundary. It begins with a **hypothetical externally constituted live winner lease** bound to one exact operation and one recipient interface.

It is not constructible from response bytes, signatures, query results, local journals, or caller booleans. `authority_adapter_present()` and `provider_adapter_present()` are permanently false.

## State

The relation carries:

- phase: `winner_live`, `query_only`, `dispatch_active`, or `fail_stop`;
- lease: `live`, `consumed`, or `lost`;
- exact recipient: none, A, or B;
- independent observations that A or B copied the winner value;
- a restart flag;
- the exact DispatchCut V3 downstream state.

Copy observations never affect authority. The positive join consumes the one shared lease and invokes DispatchCut’s `plan_dispatch` in the same transition, thereby creating one retained C2 intent and binding one recipient.

## Laws

1. A copy of the winner value is observation-only.
2. Exact join consumes the shared lease before any later dispatch action.
3. Subject, route, or format mismatch consumes the lease before validation and fail-stops.
4. There is no successful crash gap between lease consumption and retained C2 intent in the model.
5. Restart before the join destroys the live lease and all copy observations.
6. Restart after the join preserves the exact recipient and downstream retained intent.
7. Provider query, detached response, and recovery cannot mint or consume a lease.
8. Downstream recovery remains governed by DispatchCut V3 and cannot mint first-dispatch authority.
9. One relation history reaches at most one retained intent and one effect.
10. Copying, cloning, or restoring the complete premise defeats global one-use.

## Exhaustive result

The canonical relation contains:

- 91 reachable states;
- 39 events;
- 3,549 saturated transitions;
- 530 applied transitions;
- 3,015 rejected transitions;
- four environment-impossible proof-world observations;
- zero candidate/reference disagreements;
- eight copy observations;
- 32 lease-consumption edges;
- eight recipient bindings and intent persistences;
- 24 validation-failure burns;
- 281 observation-only edges;
- 182 query observations;
- zero copy, query, detached, recovery, or post-restart authorizations;
- zero successful crash-gap edges;
- maximum one intent and one effect per local trace.

Canonical relation SHA-256:

`f5953046e304e6cfb119b03d73ebfa70ad53ff5ff49947ed0dc379abfedc919b`

## Executed countermodels

The witness retains three explicit two-effect constructions:

- **copied-value replay:** the same copyable winner value initializes two fresh recipient premises;
- **clone:** two copies of the complete pre-join premise each consume locally;
- **restore:** restoring the complete pre-join premise after one effect enables another local consume.

These are not test constants. The C++ campaign and independent Python verifier execute the exact transition sequences and count the resulting intents and effects.

## Interpretation boundary

`exact_join_is_atomic_in_model=true` means only that the finite relation has no intermediate successful state between consume and intent. It does not identify a database, transaction, filesystem, power-loss guarantee, administrator, or provider operation.

The proof closes a specification seam. It does not instantiate the premise. A real Deployment Bridge must either co-locate the conditional provider mutation and retained pending intent in one protected transaction or provide an equivalent recipient-bound consume primitive whose state cannot be cloned or restored with the subject.
