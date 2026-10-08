# rev0317 field execution risk burndown

## Risk posture

`FT-0181` remains live because the archive still lacks a real owner-reviewed `SRC2+` packet. The
main risk is a stall: operators keep improving local artifacts while no owner is contacted and no
teacher/tutor cycle runs.

## Burned down in rev0317

| Risk | Previous state | rev0317 change | Remaining boundary |
|---|---|---|---|
| owner send ambiguity | scratch packet existed but was easy to miss | durable send pack records the router state and exact post-send command | human must actually send or record route block |
| overbroad data request | owner rail could be read as a data export path | send template repeats minimized eight-row aggregate request and exclusions | owner may still refuse or send unusable material |
| micro-pilot incompleteness | plan existed but lacked daily run artifacts | run card, owner plan, and session log added | no real owner has run it |
| governance distraction | cold-tail history could pull attention back to doctrine | governance-tail audit names cold retrieval families and deletion test | deletion waits for a real cycle |

## Next field actions

1. Run or regenerate `make owner-field-work`.
2. Use [`../30-operations/ft0181-owner-contact-send-pack.md`](../30-operations/ft0181-owner-contact-send-pack.md)
   to send the bounded request or record a route block.
3. Use [`../30-operations/teacher-tutor-micro-pilot-run-card.md`](../30-operations/teacher-tutor-micro-pilot-run-card.md)
   to prepare one concept, one owner, one fallback, and one no-AI transfer check.
4. When real owner material returns, run `make owner-field-next CSV=/path/to/real-owner-return.csv`
   and execute only the emitted command.

## Claim boundary

Rev0317 lowers execution friction. It does not prove that the owner exists, that an owner will reply,
that the micro-pilot improves learning, or that any service is safe or effective. It does not close
`FT-0181`.

