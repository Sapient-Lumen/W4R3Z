# Claim/evidence ladder — rev0075

A passing fixed-behavior test answers only “does this implementation enforce this assertion?” It does not answer whether the assertion describes a reachable threat, a trustworthy boundary, a compatible policy, or a meaningful impact.

| Rung | Question | Minimum evidence | What remains unproven |
|---:|---|---|---|
| 0 | Can the parser construct the message? | exact parser/wire fixture | handler reachability |
| 1 | Does current code accept or mutate it? | exact-current behavior witness | protocol legitimacy |
| 2 | Does it violate a stated local invariant? | request/state comparison | remote capability |
| 3 | Can protocol actors reach the needed state? | message order, routing, connection state | identity trust |
| 4 | Is the security-relevant identity or token bound to that actor? | server-mediated, cryptographic, or equivalent proof | exploitation |
| 5 | Can an unrelated actor exercise the capability reliably? | end-to-end reproducer with timing/state | impact |
| 6 | What persists or crosses a boundary? | bounded metrics and user/security outcome | safe policy |
| 7 | Is the desired policy compatible and complete? | negative controls, legacy/mixed-client cases, history | implementation quality |
| 8 | Does a candidate implementation satisfy the policy without regressions? | focused plus native/integration suites | upstream suitability |

## SEARCH-RESP-01A placement

```text
rung 0: reached — FileSearchResponse parses with an allowed token
rung 1: reached — off-request msg.username is accepted
rung 2: reached — user-mode request retains a narrower intended user set
rung 3: reached in part — a response arrives over a P connection and PeerInit supplies msg.username
rung 4: not reached — PeerInit username is not server-bound by the current protocol
rung 5: not reached — no reliable unrelated-peer injection reproducer
rung 6: not reached — no measured durable or boundary-crossing impact
rung 7: partial — historical Museek compatibility is known; canonicalization/mixed-client proof is absent
rung 8: mechanical only — rev0039 tests and upstream units pass, but no patch is selected
```

The old packet treated rung 8 mechanics as though rungs 4–7 had already been established. Rev0075 corrects that inversion.

## Rules for future packets

1. Name the identity source and say whether it is merely claimed.
2. Keep correlation tokens separate from authorization capabilities.
3. Include at least one adversarial counterexample to the proposed policy.
4. Preserve historical compatibility intent before narrowing acceptance.
5. Record missing rungs in the current ledger.
6. Do not use “production-ready,” “security fix,” or “selected patch” based only on patched green tests.
7. Treat current-source parity as necessary but never sufficient.
