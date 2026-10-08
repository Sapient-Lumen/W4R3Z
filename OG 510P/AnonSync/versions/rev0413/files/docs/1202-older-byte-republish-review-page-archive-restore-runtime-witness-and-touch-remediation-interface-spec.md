# Older-byte republish review page — archive restore, runtime witness, and touch remediation

## Purpose

Review any attempt to make an older local version authoritative again.
This page exists because `copy file out of Archive` is not equivalent to `mesh rollback succeeded`.

## The page must answer

1. Is the candidate version coming from Archive, another parked location, or an external backup?
2. Is the runtime currently alive on the peer performing the restore?
3. Will the restored byte version be observed as a fresh change now, or risk being re-archived or overwritten?
4. Does manual touch or explicit rescan need to be part of the republish sequence?
5. What survivor map will remain after the action?

## Candidate source classes

Represent exactly one:

- local Archive version
- parked local copy outside the subject
- external restore source
- unknown older byte source

## Runtime-witness classes

Represent exactly one:

- **Runtime live and observing**
- **Runtime not live / restore would be weak**
- **Runtime live but detection uncertain**
- **Unknown runtime posture**

## Review ladder

### Branch 1 — live restore with strong witness

Use this when the runtime is live and observing the subject.
The page should permit `Restore and republish` and state the remaining proof ceiling.

### Branch 2 — live restore but weak detection

Use this when the runtime is up but the file may need touch or rescan for honest observation.
The page should recommend one of:

- `Restore, then touch`
- `Restore, then rescan subject`
- `Restore to parked location first`

### Branch 3 — runtime absent

Use this when Sync is not running or cannot currently observe the subject.
The page must warn that an older restored file may lose again and be re-archived or overwritten when the runtime later compares mtimes.
The recommended default should be:

- `Do not claim rollback yet`
- `Start runtime and re-open review`

## Survivor map section

The page must show what remains after the action:

- archived losing versions still present
- current winner still present on remote peers
- restored candidate now staged but not authoritative
- restored candidate published and awaiting convergence proof

## Future recurrence footer

After a restore action, the page may optionally recommend:

- reviewing file-class delay for this extension
- reviewing clock/time-zone hygiene across peers
- reviewing change-detection health for this path

These recommendations must appear as *future-risk reduction* rather than proof that the restore is already authoritative.

## Required blocked stronger sentences

The page must explicitly refuse to imply any of these unless separately proven:

- `rollback completed`
- `all peers now agree`
- `archive restore is equivalent to version control revert`
- `touch proves the older version is correct`

## Required outputs

- source class of restored bytes
- runtime-witness class
- remediation required before publish claim
- survivor map
- blocked stronger sentence

