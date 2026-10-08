# Resilio ciphertext custody, recovery prerequisites, and encrypted-archive ceiling evaluation

## Bottom line

Current official Resilio docs still make a strong case for borrowing **ciphertext-only custody on untrusted hosts**.
They still describe a real pattern: put one peer on a VPS, NAS, or otherwise untrusted machine, keep the bytes encrypted there, and let that node seed continuously without exposing plaintext.
That is useful, serious product behavior.

They also still show why AnonSync should **not** clone Resilio's page contract.
The ordinary operator answers are still too scattered.
Today the operator still has to stitch together several caveats to know:

- whether the chosen encrypted target is actually safe to admit
- whether this opaque node can ever produce plaintext in ordinary product flow
- what exact materials must be preserved now to make later recovery real
- why encrypted Archive is not a real `restore back into the live share from here` path

That is the sharper no-clone line for this pass.

## What current Resilio docs still get very right

### 1) Ciphertext-only custody is still a first-class pattern

The current `Encrypted folders` article still openly says the point is to keep a peer on an untrusted device without revealing any data, with encryption before transfer and no decryption on the destination.
It still explicitly frames the untrusted node as a continuously online seed.
That is worth borrowing.

### 2) Admission hygiene is still candidly documented

The same article still says the encrypted destination should be a freshly created directory, not a non-empty one.
It also still says ordinary pre-existing files there will simply be ignored, while files previously encrypted with the same encrypted key can be re-synced and moved to Archive, consuming extra space.
That is unusually concrete product honesty.

### 3) Recovery truth is still real, but conditional

The current docs still say there is a real failure-path recovery story from the encrypted node, but only if two conditions were prepared in advance:

- the RW and RO keys were saved somewhere
- the encrypted folder was never removed from Sync, so the original database continuity remains intact

They also still preserve a second path: local CLI decryption using the RW key, the database path, the encrypted folder path, and a pre-created output folder.
That is a real product capability.
It is also still support-shaped.

### 4) Encrypted Archive still has a hard replay ceiling

The same article is still admirably blunt that the encrypted node cannot restore a deleted file from its Archive back into the live share.
The reasons are explicit:

- the encrypted node follows the delete state because `Overwrite any changed files` is always on
- the encrypted node is read-only, so it cannot upload the restored file back

This is exactly the kind of sharp edge AnonSync should make explicit instead of burying in an article.

## Where the current page shape still fails

### 1) Encrypted admission is still split from ordinary bind/adopt truth

Current Resilio docs still let ordinary pre-populated folder connection work through one set of prompts, while encrypted-node admission has materially different rules:

- use the encrypted key manually
- do not use a non-empty directory casually
- same-F-key residue behaves differently from ordinary local files
- linked-device encrypted nodes require disconnected-mode handling

That is too much hidden branch logic for one everyday `connect this here` action.

### 2) Ciphertext custody truth still hides inside caveats

Current docs still say the encrypted node is:

- always read-only
- always `Overwrite any changed files`
- never Selective Sync
- able to share onward only in encrypted format
- unable to decrypt in ordinary use

Those are not small implementation details.
They are the whole capability story, and they should live on one ordinary page.

### 3) Recovery depends on continuity the product should foreground earlier

Current docs still make later recovery depend on things the operator had to save or preserve before the failure:

- the right key class
- the same database continuity on the encrypted node
- the ability to identify the correct database path
- a deliberately prepared output folder if using CLI decrypt

That is precisely the sort of precondition AnonSync should state up front as a recovery contract, not leave to support-style lore later.

### 4) Encrypted Archive looks stronger than it really is

Current docs are truthful here, but still only if the operator reads closely.
The encrypted node has Archive, yet Archive there is not a live replay authority.
So the operator still has to understand the difference between:

- ciphertext history exists
- ciphertext is still fetchable by another decrypt-capable seat
- deleted content can be replayed back into the live subject from this node

Those are materially different states.

## What AnonSync should do instead

AnonSync should keep the candor and replace the scattered caveat family with four ordinary pages:

1. **Encrypted target admission**
   - is this target safe for ciphertext landing
   - what residue already exists here
   - what same-key reuse side effects will happen
   - what exact postcondition will hold after connect

2. **Ciphertext custody**
   - what this node can do now
   - what it can never do here
   - what default guardrails are forced
   - what onward-share ceiling applies

3. **Decrypt recovery**
   - what current recovery rung is actually available
   - which saved materials are present or absent
   - whether database continuity is intact
   - whether CLI/offline decrypt is admissible and well-specified

4. **Encrypted Archive limit**
   - what encrypted Archive contains
   - why it is not a live restore authority from this node
   - what higher rungs still exist elsewhere
   - what honest recovery ladder remains

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for ciphertext-only custody on untrusted machines and for its unusual candor about the recovery caveats. But it is not worth cloning the way ordinary answers to `is this target safe`, `can this node ever produce plaintext`, `what must survive for later recovery`, and `why can't encrypted Archive restore the file from here` still sprawl across encrypted-folder guidance, read-only caveats, ordinary pre-populated connect notes, and CLI-style recovery instructions instead of one stable page family.

## New replacement pages added in this revision

- `487` Encrypted target admission
- `488` Ciphertext custody
- `489` Decrypt recovery
- `490` Encrypted Archive limit
