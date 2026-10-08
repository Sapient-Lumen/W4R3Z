# Resilio path identity, canonicalization, and equivalence-class fragmentation evaluation

## Why this pass exists

The archive already had portability repair, invalid-name handling, rename-plane separation, and conflict recovery.
What it still lacked was one direct current Resilio evaluation for another ordinary seam:

> when two paths look similar or identical to a human, which name form actually governs identity, collision, portability, and sync safety across the cohort?

Current official Resilio docs still preserve several real distinctions, but they still make the operator reconstruct the answer from troubleshooting pages, power-user settings, and changelog notes rather than one stable contract page.

## What current Resilio still gets right

Current official docs are still candid that path identity is not only `whatever the current machine accepted locally`.
They still say all of the following:

- `Power user preferences` still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode filenames into composed/decomposed form.
- `Conflict files in Sync` still says collisions can arise from case-insensitive peers, decomposed UTF symbols, prohibited filesystem symbols, and linked junctions.
- The same conflict guidance still explains that composed and decomposed Unicode names can look the same to a human while still being different at filesystem level.
- `My files don't sync` still says Sync expects UTF-8 naming, flags special-symbol / encoding trouble, and still warns about path-length limits.
- `Unsupported asterisk (*)...` still says one invalid trailing-asterisk family can be interpreted as system data and disrupt syncing.
- The current changelog lineage still records fixes for crashes caused by mixed composed/decomposed filename symbols, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

That candor is valuable.
Resilio is not pretending that local acceptance, rendered appearance, and peer-safe canonical identity are always the same truth.

## Why this is still a good reason not to clone them

### 1) Canonicalization policy is still a hidden advanced lever

The product still has a real normalization policy, but the ordinary operator answer to `what counts as the same name here?` is still partly hidden behind a power-user setting and partly implied by conflict outcomes.

### 2) Equivalence-class truth is still learned from failure

Current docs still teach the operator about case collisions, composed/decomposed collisions, and invalid-symbol substitutions mostly through conflict examples, bugfix notes, and repair prose.
That means the product still surfaces identity classes too late.

### 3) Path validity is still local-looking but cohort-shaped

A local filesystem may accept one name form while another peer will rewrite, reject, or collide with it.
Current docs preserve that truth, but the ordinary question `is this rename safe for the whole cohort?` is still scattered across troubleshooting and changelog archaeology.

### 4) Rendered names and byte-level names still collapse too easily

Humans see one filename.
The product reality still depends on codepoint form, case posture, portability restrictions, and symbol-rewrite rules.
AnonSync should not clone any contract where that distinction remains mostly implicit until damage appears.

## What AnonSync should do instead

AnonSync should keep the candor and refuse the fragmentation.
The replacement contract should make path identity first-class:

1. **Path identity contract sheet**
   - rendered label
   - raw name form
   - canonical comparison basis
   - cohort portability horizon

2. **Canonicalization review**
   - case posture
   - Unicode normalization posture
   - forbidden-symbol and rewrite posture
   - strongest safe sentence

3. **Equivalence collision warning**
   - same-looking / different-byte names
   - same-byte / rewritten-peer names
   - local-safe / cohort-unsafe rename plans

4. **Path validity preview**
   - local acceptability
   - peer portability
   - blocked rename/adoption effects
   - safe alternative ladder

5. **Path identity receipt**
   - reviewed canonical basis
   - equivalence verdict
   - portability ceiling
   - blocked stronger sentence

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that path identity really depends on case posture, Unicode normalization, invalid-symbol rules, and peer portability. But it is not worth cloning the way ordinary answers to `are these two names the same thing, a collision, or a peer-specific rewrite?` still sprawl across power-user preferences, conflict guidance, troubleshooting notes, invalid-name warnings, and changelog archaeology instead of one stable page family.
