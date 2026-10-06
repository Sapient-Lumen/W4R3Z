# ZFS native encryption as a first-class primitive (generations, state, and key-use evidence)

DeriveBSD is ZFS-backed by design, so “rollbackable generations” are already natural.
A missing piece is **at-rest protection** for specific datasets (especially per-workload state) without breaking the explainability or rollback story.

OpenZFS provides native dataset encryption with explicit key loading/unloading and clear inheritance semantics.

References (OpenZFS):
- Encrypted dataset roots and inheritance: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-change-key.8.html
- Key loading semantics: https://openzfs.github.io/openzfs-docs/man/master/8/zfs-load-key.8.html
- Encryption command set overview: https://openzfs.github.io/openzfs-docs/man/master/8/zfs.8.html

FreeBSD ecosystem note:
- FreeBSD Foundation article (dataset encryption + load/unload keys): https://freebsdfoundation.org/our-work/journal/browser-based-edition/storage-and-filesystems/protecting-data-with-zfs-native-encryption
- “Raw send” with encryption as a distribution consideration (historical context): https://freebsdfoundation.org/wp-content/uploads/2020/07/OpenZFS-Encryption-Arrives-on-FreeBSD.pdf

## Lessons to steal

### 1) Encryption roots as an authority boundary

OpenZFS treats the first encrypted dataset as an **encryption root**.
Descendants inherit the key by default; loading/unloading/changing the root key affects inheritors.
That makes “which bytes are protected by which key?” a **tree-structured fact**.

### 2) Key load/unload is an explicit operation

`zfs load-key` and `zfs unload-key` make “key present” a discrete state, not an ambient condition.
This is a strong fit for DeriveBSD’s evidence-first posture.

### 3) Raw transport matters (optional)

If using ZFS send/recv as a distribution lane, encryption introduces choices:
- send decrypted blocks vs send raw encrypted blocks

DeriveBSD should treat this as policy, and record it as evidence.

## DeriveBSD mapping

### Dataset taxonomy

- Host generations (boot environments): typically **not encrypted** by default (operational simplicity)
- Workload *private state* datasets: **encrypted by default** (policy-controlled)
- Secrets store datasets: **encrypted by default** (policy-controlled)

The key point: encryption is a **per-dataset** decision derived from policy, not a global “encrypt everything or nothing”.

### Evidence objects

When policy enables ZFS native encryption, emit:

- `zfs.encryption.plan.json`
  - dataset path
  - encryption root id
  - key policy reference (not the key)
  - whether “raw send” is permitted for this dataset class

- `zfs.keyuse.evidence.json`
  - action: `load-key | unload-key | change-key`
  - operator/automation identity
  - reason / policy decision id
  - dataset list affected (inheritance-expanded)

This keeps “why was this key loaded?” explainable without logging secrets.

### Operational rules (defaults)

- keys are only loaded inside the **smallest possible compartment** (e.g., secrets service jail)
- workloads never receive dataset keys unless explicitly intended
- key material must not enter the store; it is delivered via the secrets path (see `docs/63-secrets-sealing-and-delivery.md`)
- when keys are unloaded, the dataset should become inaccessible (keystatus unavailable), and that transition is recorded

### Interaction with distribution lanes

If ZFS send is used (`docs/126-zfs-send-distribution.md`):
- treat the stream as an Artifact
- quarantine → verify → promote
- require the stream labeling to state whether it is raw-encrypted or plaintext

Candidate RFC: *ZFS native encryption policy + key-use evidence*.

Last updated: 2026-02-23
