# Resilio encrypted-custody workflow fragmentation and proof-ownership evaluation

## Bottom line

Current official Resilio docs still make a strong case for borrowing **encrypted custody on untrusted machines**.
They still say the quiet part out loud:

- the encrypted peer is useful specifically because plaintext never appears there
- the encrypted lane uses a different key lane and different admission rules
- linked-device encrypted intake needs `Disconnected` mode and manual connection
- recovery from the encrypted node is real only if key material and database continuity were preserved in advance

That is valuable product candor.

It is also a strong reason **not** to clone Resilio's interface contract.
The operator still does not get one owned review for the entire encrypted-custody journey.
Instead they have to reconstruct it from several articles:

- `Encrypted folders`
- `Sync Private Identity & Linking My Devices`
- `Can I connect two pre-populated pre-existing folders?`
- `Disconnecting and Removing Folders`

Those articles are individually useful.
Together they still leave one ordinary operator question under-owned:

> am I doing an ordinary non-empty merge, a linked-device reconnect, or a special encrypted-custody intake with materially different safety, recovery, and continuity rules?

That is the tighter non-clone line for this pass.

## What current Resilio docs still get right

### 1) The product still has a real encrypted-custody pattern

Current `Encrypted folders` guidance still describes an untrusted peer that stores only encrypted bytes, does not decrypt on destination, and can stay online as a seed.
That remains a meaningful capability, not marketing language.

### 2) The special encrypted lane is honestly special

Current docs still openly say that encrypted intake is not just ordinary connect-with-a-different-checkbox.
The operator still must:

- create an encrypted folder at the source
- pass the encrypted key
- use manual connection on the destination
- keep a linked destination in `Disconnected` mode when using one identity
- choose a fresh encrypted directory rather than casually landing into an arbitrary non-empty path

That difference is real and worth preserving.

### 3) Ordinary pre-populated connect is still different in kind

Current `pre-populated folders` and `Disconnecting and Removing Folders` docs still describe an ordinary non-empty intake where Resilio will hash, compare, merge, or replace based on content/timestamps, and where reconnect may propose a different default path or create a new sibling directory with `(1)` unless the operator manually retargets.

That is not the same contract as encrypted custody.
The operator deserves a first-class product-owned branch review before those worlds are confused.

### 4) Recovery truth is still preparation-dependent

Current encrypted-folder docs still say the encrypted peer cannot decrypt in ordinary flow, and that later recovery depends on saved RW/RO keys plus preserved database continuity, or on an explicit CLI decrypt lane with the database path and a pre-created output folder.
That is serious operational truth.

## Where the current page shape still fails

### 1) The workflow has no single owned operator spine

Today the operator can learn all the facts, but not from one place that owns the whole sequence:

1. choose encrypted custody rather than ordinary share/join
2. verify the target host is in the right identity mode
3. use the correct key lane
4. review target-path hygiene
5. accept the node's capability ceiling
6. attest that future recovery is actually prepared
7. record what was committed

That is an interface problem, not a feature problem.

### 2) The same `non-empty path` idea still means different things in different articles

Current docs still allow ordinary pre-populated merge/reuse with confirmation, while encrypted intake warns against non-empty directories and treats same-lineage encrypted residue as a special extra-space/Archive case.

Those are materially different semantics.
A product should not expect operators to keep that distinction in article memory.

### 3) Linked-device automation and encrypted-node exception still sit too far apart

Current identity docs still celebrate linked devices by making all folders available across the cohort.
Current encrypted-folder docs still require a linked encrypted destination to be in `Disconnected` mode so it behaves as an opaque intake node rather than an automatically attached plaintext-capable seat.

That exception is important enough to deserve a reviewed page, not a remembered caveat.

### 4) Recovery preparedness is still not checked at commit time

Current docs still explain later that recovery requires saved keys and preserved database continuity.
They do not turn that into an up-front reviewed attestation when encrypted custody is first accepted.

That is exactly the kind of lifecycle truth AnonSync should own earlier.

## What AnonSync should do instead

AnonSync should keep the candor and replace the fragmented article family with four ordinary pages:

1. **Encrypted custody setup flow**
   - decide which lane this is
   - verify the destination seat posture
   - review target-path admission
   - commit with a durable receipt

2. **Encrypted custody seat**
   - show what this seat can do now
   - show what it can never do here
   - show current recoverability posture
   - show strongest next action

3. **Recovery material attestation**
   - check saved-key posture
   - check continuity posture
   - classify recoverability rung
   - encourage rehearsal instead of folklore

4. **Encrypted custody dossier**
   - package the committed truths
   - make support/escalation evidence portable
   - keep `what we set up` distinct from `what we hope later still works`

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for the real encrypted-custody capability and for its unusual candor about the hard ceilings of encrypted peers. But it is not worth cloning the way the operator still has to reconstruct the *whole encrypted-custody workflow* across identity docs, encrypted-folder caveats, ordinary pre-populated merge guidance, reconnect prompts, and later recovery instructions instead of one stable product-owned flow.

## New replacement pages added in this revision

- `492` Encrypted custody setup flow
- `493` Encrypted custody seat
- `494` Recovery material attestation
- `495` Encrypted custody dossier
