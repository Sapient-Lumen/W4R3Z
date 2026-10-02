# Signed-update release and retention operations

IoTox keeps release signing, device authority, synchronization publication, and update application
as separate roles. The commands in this document operate only on owner-local release policy and the
recoverable inactive-slot store. They do not grant a peer apply, restart, health, or deletion
authority.

## Create and inspect a release signer

Create the signer in an already existing owner-private directory. The creation primitive writes a
mode-`0600` temporary, synchronizes it, and commits with Linux `renameat2(RENAME_NOREPLACE)`. It never
adopts or replaces an existing destination.

```sh
install -d -m 0700 /secure/offline/iotox-release
iotox update-signer-keygen /secure/offline/iotox-release/2026-q3.identity
iotox update-signer-show /secure/offline/iotox-release/2026-q3.identity
```

The file uses the fixed IoTox Ed25519 identity container with an explicit `release` role byte.
Device-identity loading rejects it, release loading rejects a device-role file, and bundle creation
requires the release role even when local policy happens to pin the other public key. Do not reuse a
sync writer identity or a RecallRoot-derived authority key as a release signer. The commands print
only the path, public key, format, and result; secret seed bytes never enter stdout.

Before admitting the public key into device policy:

1. Create the key on the intended offline signing host or medium.
2. Record the complete public key through two independently checked views.
3. Make at least two encrypted or physically controlled backups and prove each backup can be opened
   with `update-signer-show`. Custody, encryption, and destruction are deployment responsibilities;
   IoTox does not invent a recovery service or escrow key.
4. Keep the online bundle-building environment separate from the long-lived backup whenever the
   deployment can support an offline signing workflow.

## Author initial policy

`update-policy-template` writes a reviewable canonical record to stdout. Redirect it to a new file,
lint it, compare the public keys against the ceremony record, and only then install it through the
host's owner-controlled configuration mechanism.

```sh
iotox update-policy-template system-image iotox-example-x86_64 \
  /var/lib/iotox/update RELEASE_PUBLIC_KEY_HEX > update.policy.new
chmod 0600 update.policy.new
iotox update-policy-lint update.policy.new
```

The template does not mutate a running Agent or an existing policy file.

## Normal two-epoch rotation

Rotation deliberately uses an overlap epoch so the replacement signer can be exercised before the
old signer is retired.

```sh
# Epoch N+1: admit the replacement while the old signer remains active.
iotox update-policy-rotate update.policy \
  --add-signer NEW_PUBLIC_KEY_HEX > update.policy.overlap
chmod 0600 update.policy.overlap
iotox update-policy-lint update.policy.overlap

# After every intended device has loaded the overlap policy and a new-key
# canary has completed its local lifecycle, retire the old signer.
iotox update-policy-rotate update.policy.overlap \
  --retire-signer OLD_PUBLIC_KEY_HEX > update.policy.retired
chmod 0600 update.policy.retired
iotox update-policy-lint update.policy.retired
```

Every successful rotation increments `signer-policy-epoch`. Additions must be absent from both the
active and revoked sets. Retirements must currently be active. A key cannot be added and retired in
one transition, mutation arguments must be unique, and at least one active signer must remain.

If a key is believed compromised and another trusted signer is already prepared, one reviewed
transition may add the replacement and retire the compromised key at the same epoch. This shortens
overlap but sacrifices the canary period; it is an emergency tradeoff, not the routine ceremony.

A device rejects future bundles from keys in its loaded revoked set. Policy v2 does not rewrite
already staged or confirmed state. Reinstalling an older complete policy can still defeat a purely
software policy epoch, so policy deployment and backup must preserve the latest reviewed epoch. ADR
0311 now offers an optional authenticated `update-lifecycle` witness that binds the exact policy and
signed state before runtime. Its first protocol freezes the policy within one witness epoch;
rotation therefore requires the still-open replacement/re-anchor ceremony rather than a live edit.

## Recoverable slot retention

The hot slot directory admits at most eight immutable payload files. The confirmed slot and any live
candidate named by stable-device-signed state are protected. Historical unreferenced slots can be
removed from that hot bound only through explicit local quarantine:

```sh
iotox update-gc dry-run
iotox update-gc quarantine
```

Dry-run reports the signed state generation, active/protected/eligible counts, eligible bytes, and
the existing quarantine population without mutation. Quarantine repeats the same inventory under
the Agent's update-operation lock and atomically moves every eligible slot, in canonical filename
order, from `slots/` to `quarantine/`. Destination names append `.q.STATE_GENERATION`; no destination
is replaced.

The quarantine is owner-private, shape-checked at every Agent start, and bounded to 256 files.
Admission proves capacity before the first move. A crash between moves leaves a valid subset in each
directory; restart validates both, continues using the protected confirmed slot, and a later
quarantine request moves the remaining eligible files. Both directories are synchronized after the
move set.

There is no purge opcode, CLI mode, automatic age rule, or unlink path. Quarantined bytes are
recoverable custody/evidence, not an install source and not permission to lower the confirmed
sequence. To reissue old content, publish and sign it at a new higher release sequence. Moving or
deleting quarantine files outside IoTox is an explicit administrator action beyond this contract.

## What remains target-specific

These operations close release-key authoring/rotation and non-destructive hot-slot retention.
`update-linux-service-v1.md` now defines the separately gated executable consumer for policy-v3
service slots, its exact readiness predicate, and signed rollback/relaunch behavior. Opaque v1/v2
slots remain inert.

The repository still does not define boot selection, recovery media, secure boot, hardware anti-
rollback, flash-wear limits, a physical power-cut matrix, or representative-hardware qualification.
A production service deployment must also name its enclosing manager and whole-cgroup shutdown
policy. Those remain the physical M7 target gate; construction process/VM evidence cannot satisfy it.
