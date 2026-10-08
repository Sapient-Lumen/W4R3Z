## Local-vs-remote alias review

### What this page prevents
This page prevents one visible label from hiding whether the operator changed the filesystem subject, only the local UI alias, only a device label, or only the label inserted into a newly generated invite.

### Review branches

#### 1. Filesystem subject rename
Use this branch when the folder is renamed in the file browser.
The UI must say the rename affects this device's on-disk folder, that Sync tracks the change locally, and that other peers do not automatically adopt the new pathname.

#### 2. Local UI alias only
Use this branch when a desktop custom share name is changed in preferences.
The UI must say that the on-disk folder stays unchanged, remote peers do not inherit the alias, and the alias may persist in UI after disconnect until reset.

#### 3. Invitation label only
Use this branch when the operator changes the name in the share flow before generating a link or QR.
The UI must say the new text is inserted into that generated invite only and does not by itself rename the local share alias or the filesystem subject.

#### 4. Device label only
Use this branch when the operator changes a device name on mobile.
The UI must say that the device label is part of how that installation is presented, but it is not the same thing as regenerating the identity.

#### 5. Identity handle regeneration
Use this branch when the operator wants a different identity name.
The UI must say the change requires unlinking and generating a new identity, which is stronger than relabeling because certificate lineage changes.

### Required outputs
Every branch publishes:

- active naming plane
- what other planes remain unchanged
- propagation scope
- strongest honest human sentence
- stronger naming sentence still blocked
