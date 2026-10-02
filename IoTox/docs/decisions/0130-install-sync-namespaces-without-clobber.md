# ADR 0130: install synchronization namespaces without clobber

Status: accepted

Date: 2026-08-21

## Decision

The first owner-local synchronization administration effect is creation-only installation of one
complete canonical `iotox-sync-namespace-v1` record:

```text
iotox sync-namespace-template NAMESPACE ROOT WRITER_PUBLIC_KEY_HEX \
  [SUBSCRIBER_PUBLIC_KEY_HEX...] > namespace.policy
iotox sync-namespace-lint namespace.policy
iotox sync-namespace-install namespace.policy
```

Template generation and linting are offline, effect-free operations. The template selects the first
integrated engine (`range-v1`), manual activation, and the existing bounded default quotas; the
operator supplies the exact normalized absolute data root, one stable writer device principal, and
zero or more stable subscriber principals. The output is the ordinary canonical record rather than a
second configuration language. Advanced quotas remain editable fields in that record and the linter
requires byte-for-byte canonical re-encoding.

Installation sends the validated record through local control protocol v1.27. The running Agent must
have synchronization explicitly enabled and the caller must pass the existing owner-private,
same-user `control.sock` admission boundary. Remote friendship and `sync.admin` authority do not
admit this host-local effect.

The policy store must already pass the strict no-follow owner-only loader boundary. IoTox takes an
exclusive cooperative `flock` on the opened namespace-directory inode before capacity inspection,
then encodes the validated policy into an unnamed `O_TMPFILE`, sets mode 0600, writes and fsyncs it
completely, and publishes `<namespace>.namespace` with one atomic no-clobber
`linkat(AT_EMPTY_PATH)`. It then fsyncs the namespace directory, reloads the complete store, and
atomically replaces the live registry. There is no visible partially written filename and
cooperating installers cannot race the 64-namespace ceiling.

An exact retry is a duplicate and does not advance the live registry generation when it is already
loaded. An existing namespace ID with different bytes is refused and remains unchanged. Concurrent
same-record creation converges on duplicate; a different winner is refused. Replacement and removal
need a later explicit quiescence and state-retirement contract and are not smuggled into `install`.

## Consequences

- An operator no longer has to hand-encode `root-hex` or stop the Agent to create the first
  namespace.
- The generated file is ordinary inspectable policy and can be reviewed, versioned privately, or
  linted before the effect.
- Creating policy grants no network authority. Writer/subscriber membership still composes with the
  exact current authority-ledger v3 proof at every remote entrance.
- The namespace data root is named by local policy and is not created, populated, activated, or
  removed by installation.
- `content-v2` remains representable in the frozen record, but the current Agent data path still
  supports only `range-v1`.
- Live conflicting update, removal, persistent subscription administration, and cancellation remain
  S3 work.

## Evidence

One new direct check covers unnamed-file publication, mode/link shape, strict reload, exact duplicate,
conflicting replacement refusal, and absence of temporary directory entries. A CLI check decodes a
generated template and proves canonical principal ordering. The existing live-Agent construction
check now creates a namespace through operation 72, observes registry generation 2, proves exact
retry leaves that generation unchanged, refuses a conflicting record, and reloads the durable store.

The owned registry grows from 505 to 507. The complete 26-target GCC/CTest suite and the complete
41-target Clang 21 ASan/UBSan suite pass; five delegated-cgroup checks skip in the non-delegated
construction shell by design.
