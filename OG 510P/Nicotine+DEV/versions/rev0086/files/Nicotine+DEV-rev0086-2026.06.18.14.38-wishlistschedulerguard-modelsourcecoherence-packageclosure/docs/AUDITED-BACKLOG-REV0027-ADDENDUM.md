# Audited backlog addendum — rev0027

New verified audited-backlog packet:

```text
DISTRIB-PARENT-FANOUT-01 / U-173 + U-187 + U-216 + U-214
```

Status:

```text
verified across 3.3.10, 3.3.x, and master
not strict-promoted
not production-ready disclosure text
```

The Pass 195 row for U-173 claimed that the server `PossibleParents` list is not capped to the documented maximum of 10 before distributed parent connection fanout. Rev0027 confirms this current behavior: all three source lanes parse a 25-entry list and initiate 25 distributed parent connection attempts.

U-187 remains useful, but it is not a separate top report. The child-slot budget can be filled by distinct claimed usernames; duplicate same-username child replacement is better treated as PB-01 support.

U-216 is verified as semantic username/root-string validation hardening. It should be solved with a shared username validator, not a one-off distributed-only filter.

U-214 is demoted to a 3.3.10 backport/regression note because current/future lanes no longer forward unsupported embedded distributed messages in the same way.

Strict/front lane remains unchanged:

```text
1. U-123
2. PB-01 / U-168 + U-176
3. SEARCH-RESP-01 / U-163
```

Next narrow target:

```text
SEARCH-SEND-POLICY-01 / U-174 + U-247
```
