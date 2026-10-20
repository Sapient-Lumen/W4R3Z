# Protected state and authority-witness evidence

Date: 2026-09-02
Host: founding x86_64-linux machine; NixOS VM kernel 6.6.94
Decision: ADR 0303

## Owned implementation

```bash
nix develop -c cmake --build --preset gcc-debug --parallel 2
nix develop -c ctest --test-dir build/gcc-debug \
  --output-on-failure -R '^iotox\.unit-and-integration$'
```

The direct registry passed all 759 checks. The twelve additions establish inseparable
mode/root/public-policy-pin CLI selection,
plaintext refusal before runtime mutation, strict witness record initialization/one-step transition,
an actual two-thread stale-expectation CAS race with exactly one winner, normal witnessed authority
commit, rejection after complete ledger/guard deletion while the witness remains advanced,
deterministic recovery across unapplied intent, pending/local-old, pending/local-new, and
committed/local-new states, both pending and final committed-CAS lost replies, missing-intent refusal,
refusal to label a same-domain backend production-independent, and refusal of a matching
ledger/guard snapshot taken immediately before principal revocation.

## Encrypted filesystem boundary

```bash
nix build .#checks.x86_64-linux.protected-state-fscrypt-vm --no-link -L
```

The VM creates a separate ext4 filesystem with the encryption feature, externally installs one
32-byte test key, applies a policy-v2 root, and executes both source-linked `run-check` and real
`iotox run`. The test requires:

- the exact configured policy identifier and `runtime=tmpfs` in preflight;
- real Tox savedata creation under the encrypted root;
- private `0700` Agent-created state parents that remain admissible after key removal/re-addition;
- no configured swap;
- refusal of a mismatched public policy-ID pin, prefix sibling, configured symlink, multiply linked
  regular file, FIFO, and nested bind mount;
- removal of the correct key, installation of a different key, exact missing-policy-key refusal,
  and no runtime tree after refusal;
- recovery only after the original key is re-added; and
- absence of the plaintext canary when the filesystem is synchronized, unmounted, and scanned as a
  raw block device.

The deterministic zero-filled key is a VM fixture, never deployment guidance. This gate establishes
construction-kernel fscrypt behavior, not key custody, secure deletion, swap/hibernation safety on
another system, all filesystem implementations, or runtime secrecy after unlock.

## Witness boundary at the ADR 0303 checkpoint

The in-memory backend is deliberately `independently_controlled=0`; it proves coordinator logic only.
At this checkpoint no production backend, credential ceremony, witness replacement/re-anchor
operation, or broader lane was claimed. ADR 0305 and
`2026-09-02-remote-authority-witness-service.md` subsequently add the authenticated service backend
and the same-host two-guest logic gate. They do not retroactively turn this coordinator-only evidence
into physical/admin/failure-domain independence, nor close the broader-lane and exhaustive campaign.
