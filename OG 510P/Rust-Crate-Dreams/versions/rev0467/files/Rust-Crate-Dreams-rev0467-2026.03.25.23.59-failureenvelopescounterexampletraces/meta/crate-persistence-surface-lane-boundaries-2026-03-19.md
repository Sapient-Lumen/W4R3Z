# P-0522 — persistence-surface lane boundaries (2026-03-19)

This note exists to stop the archive from collapsing several nearby ideas into one fake “storage support” lane.

## Keep these lanes separate

### 1. Persistence-surface packs are not serializers
- Postcard can provide a stable wire specification.
- `serde-reflection` can provide a format registry under version control.
- `revision` can provide version-aware serialization / deserialization.

Those are **compatibility-authority inputs**.
They are not the full receiver-facing persistence contract.

### 2. Persistence-surface packs are not storage engines
- redb, SQLite wrappers, WAL crates, and domain stores may expose real recovery or repair substrate.
- A persistence-surface pack sits **above** them and says what another team is actually promised.

### 3. Persistence-surface packs are not release-code upgrade packs
- **P-0514** explains source/API/release migration.
- **P-0522** explains migration and compatibility for persisted state that outlives the process.

### 4. Persistence-surface packs are not lifecycle/resource/authority packs
- **P-0520** is about activation, stop verbs, drain, teardown.
- **P-0521** is about queues, pools, permits, backlog ownership, caller fate.
- **P-0519** is about ambient power, determinism, sandbox/profile posture.
- **P-0522** is about durable bytes/state and what success/recovery/migration really mean.

### 5. Persistence-surface packs are not embedded flash/filesystem adoption kits
- **P-0527** is about native LittleFS adoption, storage-adapter truth, compatibility witnesses, and power-cut evidence for a specific substrate.
- **P-0522** is a broader receiver-facing contract that can import evidence from engines like that, but does not replace them.

### 6. Persistence-surface packs are not async-file ergonomics crates
- Tokio’s file APIs may change scheduling/performance posture.
- They do **not** automatically create a stronger durability or publication contract.

## The key distinctions future revisions must keep explicit

1. **publication target**
   - destination path replaced,
   - symlink replaced,
   - canonical target modified,
   - or manual-review-required.

2. **identity retention**
   - permissions,
   - ownership,
   - timestamps,
   - ACLs,
   - xattrs / SELinux context,
   - and similar metadata classes.

3. **durability boundary**
   - buffer / visible / synced / committed / remotely acknowledged.

4. **compatibility authority**
   - stable external spec,
   - schema snapshot,
   - revision history,
   - engine docs,
   - or best-effort shape.

5. **recovery witness**
   - declared only,
   - integrity-check observed,
   - repair observed,
   - or manual review.

## Anti-patterns to avoid

- “Uses temp-file replace, therefore it is durable.”
- “Uses async file APIs, therefore the commit contract is stronger.”
- “Uses Serde, therefore the format is stable.”
- “Uses a crash-safe engine, therefore all recovery claims are witnessed.”
- “Atomic replace means metadata retention is unchanged.”
- “Overwriting a symlink path means the target file was modified.”

## Working sentence

**P-0522** should stay the lane for the receiver-facing persisted-state contract: what path object changes, what metadata survives, what success means, what compatibility authority exists, and what recovery/migration story was actually checked.
