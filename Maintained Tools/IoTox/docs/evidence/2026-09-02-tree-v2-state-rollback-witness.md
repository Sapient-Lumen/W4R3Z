# Tree-v2 semantic-state rollback-witness evidence

- Date: 2026-09-02
- Host: IoTox founding x86_64 Linux machine
- Decision: ADR 0314

## Direct gate

The final Clang build and complete test surface ran as:

```sh
nix develop --command sh -c \
  'cmake --build build/witness-clang -j2 && \
   ctest --test-dir build/witness-clang --output-on-failure -j2'
```

Result: `817/817 tests passed` in `39.00 s`. The complete 55-entry CTest surface passed in
`39.54 s`; five delegated-cgroup process cases were capability-skipped on this host.

The final sanitizer gate rebuilt the changed core and passed all 16 owned-registry shards:

```sh
nix develop --command sh -c \
  'cmake --build build/clang-asan-ubsan -j2 --target iotox_tests && \
   ctest --test-dir build/clang-asan-ubsan -L owned-registry --output-on-failure -j2'
```

Result: `16/16` passed in `26.20 s`.

The 13 dedicated checks cover:

- stable 64-way namespace-domain separation plus base-domain and device-key separation;
- digest binding of immutable namespace storage identity, the writer-sorted branch frontier, exact
  signed workspace state, and exact signed maintenance pins/cutoffs;
- publication, workspace initialize/begin/finish, pin, and unpin advancement;
- local root replacement that did not land and one that landed before remote begin;
- local-pending/root-new/external-old, local-pending/root-new/external-pending, and
  local-committed/external-pending recovery, plus impossible local-old/external-pending refusal;
- lost replies after both external pending and final committed CAS;
- complete prior tree-state rollback, same-position digest fork, wrong selector, pending-target fork,
  third local head, malformed guard signature, and multiply linked guard refusal;
- refusal before an otherwise early duplicate/stale mutator result; and
- a concurrent root reader blocked by the namespace transaction until external commit.

## Two-guest gate

The retained NixOS/Sandwurm-style test ran as:

```sh
nix build .#checks.x86_64-linux.rollback-witness-service-vm -L
```

Result: pass. The derivation rebuilt the linked-c-toxcore release binary with GCC warnings-as-errors
and validated its SPDX output. One Agent guest and one witness guest used separate processes and
virtual disks. The exact source-linked binary enrolled 11 records through authenticated TCP,
including two lane-9 single-writer namespaces and one lane-10 tree-v2 namespace under separately
derived domains. The
service exported and verified complete 11-record checkpoints and enforced the later checkpoint as a
restart floor.

The Agent advanced the existing tree-v2 namespace after enrollment. With the remote lane left
current, the test replaced its complete local namespace state with the older enrolled snapshot. The
next Agent start refused and did not create the named RuntimeTree. Restoring the exact current
namespace allowed startup. Existing authority, incarnation, route, terminal-policy, command-effect,
sync-policy, update-lifecycle, four-root, service-checkpoint, outage, and wrong-key cells remained
green.

## Evidence boundary

The direct matrix establishes the bounded tree-v2 semantic state machine and in-process
serialization. The guests establish authenticated protocol and disk/process separation on one
hypervisor. They do not establish physical or administrative independence, rollback-resistant
hardware, checkpoint custody in another real failure domain, or a live lease against another
running clone.

The lane commits semantic roots and their exact signed records. It does not prove immutable object
availability, backup, complete custody, health/worktree freshness, quarantine correctness, or safe
permanent deletion.
