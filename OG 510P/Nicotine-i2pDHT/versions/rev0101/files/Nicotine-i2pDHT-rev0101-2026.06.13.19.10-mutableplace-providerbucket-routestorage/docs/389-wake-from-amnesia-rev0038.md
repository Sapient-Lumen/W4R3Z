# Wake from amnesia — rev0038

Read these first:

```text
docs/383-rev0038-servicecontinuity-branchfold.md
docs/384-service-continuity-joined-boundary.md
docs/385-branchlet-fold-service-surfaces.md
docs/386-profile-gc-catalog-succession-joins.md
docs/387-servicecontinuityfold-audit-refactor.md
```

Mental model:

```text
catalog says what might exist
announcement says what is exposed
ingress says what reached the gate
ticket says what one caller may spend
handoff/use says what side effect is attempted
receipt says what happened
withdrawal says why otherwise valid service must stop
continuity says whether those observations agree
```

The cube is still intentionally no-network. The next dangerous step is persistence and replay memory for these folded service signals.
