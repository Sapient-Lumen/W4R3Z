## Sufficiency proof

### Purpose
Prove that the threshold behind the sentence is real before the product says `available now`, `approved already`, `synced`, or `removed everywhere I control`.

### Proof rules

#### Fetchability now
To say a file is fetchable now, the product must prove **at least one online source peer has the needed bytes**.
A generic `one peer online` count is not enough.

#### Approved already
To say a requester is already approved, the product must prove both the remembered authority basis and the active folder approval rule.
If the folder uses `all peers`, older approval memory does not satisfy the stronger sentence.

#### Synced with all connected peers
To say a folder is synced with all connected peers, the product may only range over the current connected set.
That sentence does not cover offline peers, future reconnects, or remembered holders.

#### Removed everywhere I control
To say a folder was removed everywhere I control, the product must prove the linked-family scope and must still block any stronger claim about nonlinked remote holders.

### Required proof footer
Every proof ends with:

- proven threshold
- known excluded counterparts
- what stronger quantifier sentence remains blocked
