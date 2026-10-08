# Revision 0966 validation

## Focused product slice

The final focused query-replace, witness, headless journey, undo-transaction, and
action-authority slice passed:

```text
56 passed
```

It includes the original supported corruption reproduction, external-action
selection clearing, two-step undo ordering, direct host-style edit splitting,
every response after generation drift, stale plugin snapshot restore,
same-name/different-object rejection, and version-counter disappearance.

## Lifecycle and containment slices

Plugin runtime group policy passed:

```text
74 passed
```

The 56-test plugin containment/capability file passed in three bounded slices:

```text
19 passed
19 passed
18 passed
```

Command-dispatch hygiene, default-keybinding, and delayed-interaction authority
slices passed:

```text
5 passed
11 passed
9 passed
```

The combined lifecycle invocation exceeded its process timeout after 98 passing
cases and emitted no failure; the same files were therefore rerun as completed
named slices above. No complete-suite claim is made from the interrupted run.

## Static checks

```text
mxlint: ok
```

Further revision, context, archive, audit, screen, and packaging checks are
recorded by the final packaging preflight and archive verifier.

## Revision and contract slices

Revision index, context, and deterministic archive tests passed:

```text
59 passed, 1 expected duplicate-ZIP-member warning
```

Generated effect/resource tests passed:

```text
5 passed
```

The four structural-audit tests passed as individual bounded invocations:

```text
1 passed
1 passed
1 passed
1 passed
```

Living-doc/index, screen producer, strict screen consumer, and the new journey
passed:

```text
19 passed
10 passed
13 passed
1 passed
```

Real wheel packaging and installed-resource probes passed:

```text
1 passed
2 passed
```

Direct tools also completed cleanly: `mxcontext --check`, `mxaudit --check`,
`mxeffects --check --check-help-doc`, 156 portability cases, and `mxlint`.
Repeated mixed-file invocations could remain alive after their pytest result in
this cloudtainer while an unrelated abandoned workspace process was active, so
completed per-file/per-slice results above are the claimed evidence.
