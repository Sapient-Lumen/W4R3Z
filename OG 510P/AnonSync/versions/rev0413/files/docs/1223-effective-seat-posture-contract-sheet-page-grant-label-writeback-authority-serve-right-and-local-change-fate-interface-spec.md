# Effective-seat-posture contract sheet page — grant label, writeback authority, serve-right, and local-change fate

## Purpose

Give the operator one first surface for any serious `is this peer actually read-only?`, `why did my edit not publish?`, `can this seat still help another peer?`, or `why did this posture change underneath me?` dispute.
The page must stop the product from collapsing grant label, writeback authority, onward-share authority, byte-serving, and local-divergence fate into one vague permission badge.

## The page must answer

1. What direct grant label does this seat currently present?
2. What is the effective posture after inheritance, hard-wiring, or linked-family defaults are applied?
3. Can this seat publish new mutations, serve already-approved bytes, onward-share, or revoke others?
4. If a local user edits, renames, deletes, or adds material here, what fate class applies?
5. Which stronger sentence is blocked?

## Core model

### A. Grant-label class

Represent exactly one current class:

- **Read-only grant**
- **Read-write grant**
- **Owner grant**
- **Encrypted-key hard-wire**
- **Derived-local-share grant**
- **Grant unresolved**

### B. Effective-posture class

Represent exactly one current class:

- **Direct ordinary writer**
- **Direct observer / narrow seat**
- **Owner / delegating writer**
- **Linked-family owner default**
- **Inherited local-share posture**
- **Encrypted hard-wired observer posture**
- **Posture unresolved**

### C. Mutation-authority class

Represent exactly one current class:

- **Can publish create/edit/delete/rename**
- **Can mutate locally but cannot publish**
- **Local mutation will suspend file continuity**
- **Local mutation is auto-healed back to source posture**
- **Mutation class varies by action and needs review**
- **Mutation authority unresolved**

### D. Serve-right class

Represent exactly one current class:

- **May serve approved bytes to peers**
- **May serve only through source-parent path**
- **May not serve beyond local seat**
- **Serve-right unresolved**

### E. Delegation-authority class

Represent exactly one current class:

- **May onward-share and revoke**
- **May onward-share narrow artifact only**
- **Cannot onward-share**
- **Delegation unresolved**

### F. Local-divergence-fate class

Represent exactly one current class per action family:

- **Ordinary allowed mutation**
- **Suspends file continuity**
- **Auto-healed / reverted from source**
- **Local-only residue not propagated**
- **Blocked from action surface entirely**
- **Fate unresolved**

## Required warnings

The page must warn when:

- `Read Only` is being over-read as `cannot contribute bytes`;
- local edits on a narrow seat will suspend or auto-heal rather than simply fail immediately;
- added files remain local-only and therefore create silent divergence from peer expectations;
- `Overwrite any changed files` is destructive and not available under some posture combinations;
- linked devices look like separate seats but actually collapse into one owner family;
- the seat is derived from a parent source and therefore may downshift automatically when the parent is narrowed;
- an encrypted node looks like backup authority even though it is hard-wired into RO and delete-following posture.

## Required blocked stronger sentences

The page must explicitly refuse to imply any of these unless separately proven:

- `read-only means no local changes can exist`
- `read-only means this peer cannot serve data`
- `owner badge means direct grant rather than linked-family default`
- `local share permission can be edited like any other peer`
- `encrypted backup can republish deleted material`
- `permission label alone explains the observed mutation fate`

## Compact output

The page must produce:

- `grant_label`
- `effective_posture`
- `mutation_authority`
- `serve_right`
- `delegation_authority`
- `local_divergence_fate_map`
- `blocked_stronger_sentence`
