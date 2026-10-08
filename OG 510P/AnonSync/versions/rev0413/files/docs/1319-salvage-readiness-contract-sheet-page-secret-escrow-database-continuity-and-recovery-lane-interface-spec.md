## Salvage-readiness contract sheet

### Purpose
Make the product say **whether future rescue is still honestly possible and what present-day prerequisites keep that rescue alive** before it says `backup`, `recoverable`, `safe copy`, `encrypted mirror`, or `can be restored later`.

### The contract object
Each serious dormant-recovery sentence renders these fields together:

- **Recovery family**: reconnect-and-download, local CLI decrypt, ordinary archive restore, recycle-bin restore, or another typed recovery lane.
- **Readable-now class**: plaintext-readable now, ciphertext-only now, archive-only now, or unknown.
- **Secret escrow basis**: RW key saved, RO key saved, encrypted-only key saved, secret not proven saved, or unknown.
- **State continuity basis**: original database continuity preserved, folder still present but continuity not proven, folder removed / re-added, storage root changed, or unknown.
- **Locator basis**: exact db path proven, storage root only known, shareID only known, debug-log discovery needed, or unknown.
- **Late-decrypt lane**: safe workstation reconnect with RW key, local CLI decrypt, support-assisted db discovery, no known lane, or unknown.
- **Failure dependency**: requires encrypted node still present, requires at least one online byte-holder, requires logs or storage access, requires human-held secret escrow, or another typed dependency.
- **Salvage floor**: full folder rescue plausible, some byte classes only, archive only, no honest salvage claim, or unknown.
- **Blocked stronger sentence**: the next stronger rescue claim the product refuses to make.

### Default language rules
- `encrypted backup exists` is intentionally weaker than `future salvage remains possible`.
- `folder still exists on disk` is intentionally weaker than `database continuity still survives`.
- `have an encrypted key` is intentionally weaker than `have the RW secret needed for decryption`.
- `can restore later` is intentionally weaker than `the recovery lane and its prerequisites are still proven now`.
- `bytes are stored somewhere` is intentionally weaker than `a live late-decrypt path is still available without guesswork`.

### Required persistent receipts
Any serious backup, disaster-recovery, or encrypted-node sentence stores one durable receipt preserving recovery family, secret escrow basis, state continuity basis, locator basis, salvage floor, and the blocked stronger sentence.
