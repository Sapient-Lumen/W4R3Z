# Witness rotation execution checklist

**Track:** Shared (cross-cutting)


- [ ] Publish rotation schedule update
- [ ] Verify new witness keys and endpoints
- [ ] Ensure quorum and diversity constraints still met
- [ ] Publish executed rotation event with before/after witness set hashes
- [ ] Run post-rotation consistency verification
- [ ] Close out prior witness periods and open new witness periods in `artifacts/registries/witness-health-log.csv` (bounded pointers only).
