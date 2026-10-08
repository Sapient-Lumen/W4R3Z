## Resend-geometry review page

### Question
Why did this file move the way it did?

### Mandatory review branches
1. **Piecewise delta branch**  
   Use when the current evidence says only changed pieces are moving.

2. **Whole-file resend branch**  
   Use when edit geometry shifted all pieces or the product lacks stronger diff-delta proof.

3. **Archive-assisted rename branch**  
   Use when the destination can satisfy a rename/move by finding the same hash in Archive instead of re-downloading the bytes.

4. **Archive-missing rename branch**  
   Use when the operator expects rename reuse but Archive is absent or unusable, so the bytes will be re-synced again.

5. **Priority-only branch**  
   Use when the only current claim is queue order, not byte-cost reduction.

6. **Splittability ceiling branch**  
   Use when strict priority behavior cannot be promised because the file or lane is not proven splittable.

### Required review outputs
- byte-cost class
- reuse basis
- splittability class
- queue order class
- active fallback trigger
- blocked stronger sentence

### Review language guardrails
Never let:
- `renamed` imply `no retransmission`
- `prioritized` imply `cheaper`
- `suspended` imply `aborted`
- `changed` imply `piecewise delta`
