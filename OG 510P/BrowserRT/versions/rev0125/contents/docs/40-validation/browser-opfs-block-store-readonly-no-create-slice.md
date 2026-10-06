# Browser OPFS block-store read-only no-create slice

Revision: rev0102  
Task: `browser:opfs-block-store-readonly-no-create-proof`

This managed Chromium proof checks the same no-create boundary against real OPFS. It starts with unique absent prefixes, performs missing `verify`, `has`, `delete`, and `get` operations, then probes the prefix with `getDirectoryHandle(..., { create: false })` to confirm the prefix is still absent.

The browser proof also covers `verifyOnHas: false`, then seeds a real block to prove existing `put` / `verify` / `has` / `get` / `delete` still work. A guarded OPFS/Web Locks smoke path is retained so the current OPFS path is not hardened in isolation from the lock wrapper used by browser slices.

Evidence expected from the proof:

- missing real-OPFS prefixes remain absent after read-only misses;
- missing calls do not mark the store as opened and do not increment mutable `opens`;
- `noCreateMisses` increments for the miss paths;
- existing block reads/deletes still work;
- the guarded Web Locks path verifies and leaves no held or pending locks.

Non-claims: managed Chromium only; no Firefox/Safari coverage, no quota/eviction survival, no fsync durability, no crash/power-loss recovery, no Web Locks fairness or starvation-freedom claim, no multi-tab atomicity claim, and no production-readiness claim.

Audit wording: this is a cross-browser non-claim. The proof is specifically checking that missing read-only lookups do not leave empty OPFS prefix or bucket directories behind in managed Chromium.
Managed Chromium exact audit anchor: this proof is Managed Chromium only and not cross-browser.
