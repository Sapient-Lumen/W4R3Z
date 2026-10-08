# rev0324 mission kernel

AI-EDU remains an education-design archive, not a registry machine. The mission
is to make AI-normal education more understandable, agency-preserving,
accessible, teacher-capacitating, and truthful while reducing shortcutting,
surveillance, dependency, workload waste, and false outcome claims.

## Current center of gravity

The two live blockers are still human boundaries:

1. `FT-0181` needs a real accountable owner send, route block, or returned
   owner-attested packet.
2. The teacher/tutor micro-pilot needs a real local owner-approved cycle whose
   aggregate readout is reviewed and then recorded without becoming evidence.

## rev0324 change

Rev0324 adds the local aggregate result receipt command:

```bash
make micro-pilot-result
```

It runs only after readiness has passed and `make micro-pilot-owner-review` has
recorded a real human local owner-review stop. It refuses synthetic dry-runs,
missing review records, changed packet hashes, identifying/raw/protected markers,
and release-path outputs.

## What must happen next

- Send the bounded `FT-0181` owner request or record the route block.
- Run a fresh local teacher/tutor micro-cycle, score the aggregate packet, record
  the owner-review stop only after human review, and then record the local result
  receipt if the cycle actually happened.
- Do not add another schema, branch, validator, or registry unless a real owner
  result, real micro-pilot result, or release failure demonstrates the need.

## Boundary

Rev0324 does not contact an owner, run a micro-pilot, accept evidence, create
custody, update service authority, support public claims, or close `FT-0181`.
