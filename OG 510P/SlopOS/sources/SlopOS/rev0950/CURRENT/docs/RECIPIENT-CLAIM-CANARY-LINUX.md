# RecipientClaimCanary V1 — Linux operated slice

## Boundary

RecipientClaimCanary V1 is a local post-join construction. It begins with one exact `INCARNATION` and `INTENT` already retained by a hypothetical external atomic winner-to-intent join.

The public header intentionally exposes no function that can create that premise. There is no initializer, installer, provider response adapter, winner-value mapper, owner-admission adapter, or recovery submission path.

## Fixed records

The operated store contains at most five fixed records:

```text
INCARNATION
INTENT
CLAIM
EFFECT
RESULT
```

Every retained record must be a regular file owned by the effective UID, have one hard link, exact mode `0400`, canonical UTF-8 text, bounded size, and a stable before/after descriptor profile during read. The root must be an effective-UID-owned directory at exact mode `0700`.

The no-replace hard-link fallback is accepted only if the staging alias is removed. Failure to remove that alias returns unsafe, so a permit is never derived from a newly multi-linked fixed record.

These local checks do not establish independent custody or administrator exclusion.

## Claim-before-meaning cut

`claim_pending` opens the root with Linux `openat2`, rejects symlinks and magic links in every path component, and publishes `CLAIM` with no replacement. It does this before opening `INTENT` or `INCARNATION`.

Only the fresh no-replace winner can receive a move-only `ClaimPermit`. Missing, malformed, or wrong-incarnation intent remains claimed and receives no permit. Only an exact safe canonical retained claim is a duplicate. A pre-existing symlink, directory, wrong-mode file, multi-link file, or malformed claim is unsafe rather than a duplicate.

`enter_effect` burns the claim permit before checking whether caller-supplied expected meaning is canonical or equal to the retained operation. Rejection retains exact `no_effect`; it does not restore a claim or retry right.

## Descriptor-rooted authority

The claim permit carries the already-open directory file descriptor. A successful meaning check moves that descriptor into one `EffectPermit`. Neither stage reopens the pathname.

The path-substitution campaign renames the original directory and installs another pending directory at the old pathname. The effect follows the pinned descriptor into the original directory; the replacement remains pending.

This closes post-open pathname redirection only. `mount_traversal_rejected=false` and `same_uid_writer_exclusion=false` are explicit nonclaims.

## Effect and result

The bounded canary effect is one fixed no-replace `EFFECT` file. It is not a network, cloud, financial, or privileged external effect.

`RESULT V2` binds terminal class plus exact incarnation, operation, route, and payload digest. Reopen requires the complete retained topology. EFFECT or RESULT without CLAIM and INTENT is malformed. A mismatched RESULT or orphan EFFECT is malformed.

If EFFECT exists without RESULT, `reconcile_effect_result` may append the exact effect result after re-reading and validating the complete chain. Reconciliation has no claim, entry, submission, or effect-emission path.

## Reopen vocabulary

```text
unjoined           no fixed records; observation only, never no-effect
pending            exact incarnation and intent; no claim
claimed_uncertain  claim exists but no exact terminal result
settled_no_effect  exact bound no-effect result and no effect
settled_effect     exact complete effect chain and result
effect_unsettled   exact effect chain but result not yet retained
malformed          partial, underbound, conflicting, or unsafe retained topology
unsafe             root acquisition itself failed the profile
```

An incarnation-only root is malformed rather than unjoined because the external join is required to retain the exact pair atomically.

## Campaign

The 23 process/filesystem cases cover:

- unjoined absence without no-effect inference and incarnation-only partial-join rejection;
- exact joined intent with zero response bytes;
- real two-process claim race;
- mismatch and noncanonical burn;
- missing, malformed, and wrong-incarnation intent;
- crash after claim and after effect;
- inert staging residue;
- unsafe root, fixed-name symlink rejection, and unsafe pre-existing CLAIM collision;
- full operation-result binding and orphan-effect rejection;
- descriptor-pinned path replacement;
- required claim topology and exact record modes;
- all-component root-path symlink rejection;
- clone and restore two-effect countermodels;
- exact profile of all five retained records.

Witness SHA-256:

`67f11e6057503631847af1815f51e657a19be6f9a3479d85d05c6973e3d5bdc0`

## Nonclaims

The canary does not prove owner admission, provider identity, an external atomic join, mount identity, same-UID writer exclusion, stable media, power-loss survival, independent custody, rollback resistance, global one-use, an authoritative external effect, an authoritative query, or epoch exit.
