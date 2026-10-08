## Resilio seam evaluation — participant unit, grouped peer rows, and approval-scope truth

Current official Resilio Sync docs still expose another strong non-clone seam around **participant unit truth**.
The important current facts are not subtle:

- `Sync Private Identity & Linking My Devices` still says one human-facing identity generates a digital certificate, that the certificate fingerprint is later used for further connections, and that a remote user can choose to approve all linked devices for future sharing after approving one of them.
- `What's the difference between Standard and Advanced folders` still says Advanced folders can reflect a user identity and group multiple linked devices under that user, while Standard folders do **not** reflect user identity in the peer list and instead show each linked device as a separate entity.
- `Sync functionality in detail` still says peers and devices are grouped in the Peer List and that search can target folders, users, and devices.
- `Settings on mobile platforms` still says other users are shown the identity name, device name, and certificate fingerprint, and that the device name can be edited.
- `Can I change the name of my Sync identity?` still says identity-name change is not cosmetic: changing it requires unlinking and creating a new identity, which regenerates the certificate.

This is strong semantic candor.
It is also exactly why AnonSync should not clone the present page contract.
One ordinary answer to `who exactly is this participant row talking about, what unit did I approve, and what does this count really count?` still depends on combining identity docs, Standard-vs-Advanced folder docs, peer-list behavior notes, and mobile identity/settings pages.

So this tranche freezes a stronger replacement line: **human label, certificate continuity, linked-device family, individual device seat, visible peer row, grouped user row, and historical roster memory become separate modeled truths.**

That is why this revision adds five more first-class pages: **Participant-unit contract sheet**, **Peer-row granularity review**, **Participant-authority proof**, **Participant regroup timeline**, and **Participant-unit lineage receipt**.
