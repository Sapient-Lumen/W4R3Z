# Status

## Scope of this revision

This revision is an in-place continuation of `rev0211`, driven by the current request and the now-current archive state:

- continue researching rather than merely polishing
- evaluate Resilio Sync again rather than relying on stale paraphrase
- make every `do not clone` decision point point to a better replacement page
- keep writing concrete interface contracts where the archive still has page-shape gaps
- stay narrow: prefer ordinary operator authority and lifecycle surfaces over broad product sprawl
- in this pass specifically, force a cleaner answer for ciphertext-only custody, encrypted-target admission, decrypt prerequisites, and encrypted-Archive replay ceilings

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

This revision adds one new evaluation and four new interface page specs:

- `486-resilio-ciphertext-custody-recovery-prerequisites-and-encrypted-archive-ceiling-evaluation.md`
- `487-encrypted-target-admission-page-empty-root-fkey-reuse-and-archive-side-effects-interface-spec.md`
- `488-ciphertext-custody-page-plaintext-ceiling-onward-share-and-default-ro-guardrails-interface-spec.md`
- `489-decrypt-recovery-page-saved-key-database-continuity-and-cli-witness-interface-spec.md`
- `490-encrypted-archive-limit-page-delete-state-following-and-recovery-source-ladder-interface-spec.md`

It also updates the archive-wide doctrine in:

- `README.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/11-resilio-borrow-line-and-non-clone-scorecard.md`
- `docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md`
- `docs/20-product-direction.md`
- `docs/30-interface-spec.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## Tighter answer reached in this pass

The archive now has another sharper reason to **learn from Resilio without cloning it**:

- borrow Resilio's candor that ciphertext-only custody on untrusted hosts is a real, useful product pattern
- refuse the interface contract where `is this target safe for opaque landing?`, `what can this node never do?`, `what must I preserve now for later recovery?`, and `why can't encrypted Archive replay the file from here?` still require cross-reading encrypted-folder caveats, read-only semantics, ordinary pre-populated connect notes, and CLI-style recovery instructions
- replace each refusal with one sharper public page contract

## Latest addendum — ciphertext custody, decrypt prerequisites, and encrypted-Archive ceilings after rev0211

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **encrypted target admission / ciphertext custody / decrypt recovery / encrypted Archive limit**

Current official Resilio docs still show a practical product, but they also still show that one ordinary encrypted-node answer can depend on:

- whether the chosen target path is truly empty, merely dirty, or already contains same-lineage encrypted bytes
- whether the opaque node is read-only, forced-overwrite, and non-selective by role rather than by preference
- whether later recovery still has saved RW/RO keys and intact database continuity
- whether Archive on the encrypted node contains evidence only or a real live replay path

So the tighter non-clone line is:

> borrow Resilio's useful ciphertext-only custody pattern and its unusual candor about recovery caveats, but refuse any product contract where `is this target safe?`, `can this node ever produce plaintext?`, `what must survive for later recovery?`, and `why can't this Archive restore the file from here?` still require hopping across article caveats instead of one stable page family.

That yields four more ordinary product-owned pages:

- **Encrypted target admission**
- **Ciphertext custody**
- **Decrypt recovery**
- **Encrypted Archive limit**
