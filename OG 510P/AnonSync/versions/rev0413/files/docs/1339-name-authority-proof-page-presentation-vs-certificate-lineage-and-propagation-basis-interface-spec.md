## Name-authority proof

### Purpose
Prove whether a visible text change touched only presentation or actually changed the authority-bearing identity of the installation.

### Proof rules

#### Local alias only
To say a share rename was presentation only, the product must prove the on-disk path stayed unchanged and no linked peer received the alias as its own persistent share name.

#### Device label change
To say a device rename left authority intact, the product must prove the identity fingerprint continuity for the same installation.

#### Identity name change
To say an identity name changed, the product must prove unlink plus new identity creation.
Without that proof, the stronger sentence is blocked.

#### Invite label change
To say the invite used a new label, the product must prove a newly generated link or QR payload carried that label.
That is still weaker than any claim that the share itself was renamed.

#### Filesystem rename
To say the local folder name changed on disk, the product must prove the new local path.
That is still weaker than any claim that remote peers adopted the same pathname.

### Required proof footer
Every proof ends with:

- changed naming plane
- unchanged naming planes
- propagation basis
- stronger naming sentence still blocked
