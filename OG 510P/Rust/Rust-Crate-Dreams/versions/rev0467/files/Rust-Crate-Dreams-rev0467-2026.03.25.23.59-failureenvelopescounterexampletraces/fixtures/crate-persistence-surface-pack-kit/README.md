# Crate Persistence Surface Pack Kit fixtures

These fixtures exist to keep **P-0522** concrete about five questions:

1. **What object was actually published?**
2. **What metadata or identity survived replacement?**
3. **What durability boundary was really reached?**
4. **Why should a compatibility claim be trusted?**
5. **Was recovery merely declared, or actually witnessed?**

The point of this fixture family is to stop “safe save”, “stable format”, and “crash-safe backend” from collapsing into one fake support claim.

In particular, this family should keep separate:

- temp-file replacement versus durable publication,
- path replacement versus canonical-target mutation,
- visible success versus synced or committed success,
- stable external specs versus schema snapshots versus best-effort Serde shape,
- and declared recovery paths versus currently witnessed recovery paths.
