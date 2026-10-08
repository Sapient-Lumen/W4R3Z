## Resilio seam evaluation — claim quantifier, audience truth, and sufficiency threshold

Current official Resilio Sync docs still expose another strong non-clone seam around **claim quantifier truth**.
The important current facts are not subtle:

- `Sync Share Dialog (Desktop)` still says a link can require approval from **only new peers** or from **all peers** for each shared folder.
- `Sync functionality in detail` still says that **any linked device** can approve a folder connection.
- `Sync Main View (Desktop)` still says `X of Y peers` means **online peers** out of the **total peers including offline**.
- `Synchronization Modes` still says a disconnected folder can reconnect when **any peer in the swarm** is online, while Selective Sync fetch requires **at least one peer that has the files** online.
- `Sharing a folder locally` still says a local share connects only to **self**, only pulls from the parenting share, and does **not** sync with remote peers directly even though peer rows can increase.
- `Disconnecting and Removing Folders` still says removal from linked devices does **not** prove disappearance from remote devices outside that linked identity.

This is strong operational candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `who is this claim actually about, and how many counterparts are enough for it to be true?` still depends on combining share-dialog docs, identity/linking docs, main-view docs, folder-mode docs, local-share docs, and remove/disconnect docs.

So this tranche freezes a stronger replacement line: **subject set, audience set, sufficiency threshold, and claim horizon become separate modeled truths.**

That is why this revision adds five more first-class pages: **Quantifier contract sheet**, **Audience-scope review**, **Sufficiency proof**, **Quantifier-drift timeline**, and **Quantifier lineage receipt**.
